#!/usr/local/bin/python3

import os
import subprocess
from argparse import ArgumentParser
from shutil import rmtree
from datetime import datetime
import glob
import re
from getpass import getpass

# pip3 install
import requests
from shapely.geometry import Polygon
from jinja2 import Template
from lxml import etree
from get_dem import get_dem

CHUNK_SIZE = 5242880
CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION_IDS = [
    "C1214470533-ASF",  # SENTINEL-1A_DUAL_POL_GRD_HIGH_RES
    "C1214471521-ASF",  # SENTINEL-1A_DUAL_POL_GRD_MEDIUM_RES
    "C1214470682-ASF",  # SENTINEL-1A_SINGLE_POL_GRD_HIGH_RES
    "C1214472994-ASF",  # SENTINEL-1A_SINGLE_POL_GRD_MEDIUM_RES
    "C1214470488-ASF",  # SENTINEL-1A_SLC
    "C1327985645-ASF",  # SENTINEL-1B_DUAL_POL_GRD_HIGH_RES
    "C1327985660-ASF",  # SENTINEL-1B_DUAL_POL_GRD_MEDIUM_RES
    "C1327985571-ASF",  # SENTINEL-1B_SINGLE_POL_GRD_HIGH_RES
    "C1327985740-ASF",  # SENTINEL-1B_SINGLE_POL_GRD_MEDIUM_RES
    "C1327985661-ASF",  # SENTINEL-1B_SLC
]
USER_AGENT = "asfdaac/s1tbx-rtc"


# Metadata
def get_download_url(entry):
    for product in entry["links"]:
        if "data" in product["rel"]:
            return product["href"]
    return None


def get_polygon(entry):
    floats = [float(ii) for ii in entry["polygons"][0][0].split()]
    points = zip(floats[::2], floats[1::2])
    return Polygon(points)


def get_bounding_box(polygon):
    return {
        "lat_min": polygon.bounds[0],
        "lon_min": polygon.bounds[1],
        "lat_max": polygon.bounds[2],
        "lon_max": polygon.bounds[3],
    }


def get_metadata(granule):
    print("\nFetching granule information")

    params = {
        "readable_granule_name": granule,
        "provider": "ASF",
        "collection_concept_id": COLLECTION_IDS
    }
    response = requests.get(url=CMR_URL, params=params)
    response.raise_for_status()
    cmr_data = response.json()

    if not cmr_data["feed"]["entry"]:
        return None

    entry = cmr_data["feed"]["entry"][0]
    polygon = get_polygon(entry)
    return {
        "download_url": get_download_url(entry),
        "bounding_box": get_bounding_box(polygon),
    }


# Write a netrc file
def write_netrc_file(username, password):
    netrc_file = os.environ["HOME"] + "/.netrc"
    with open(netrc_file, "w") as f:
        f.write(f"machine urs.earthdata.nasa.gov login {username} password {password}")


# Download the granule file
def download_file(url):
    print(f"\nDownloading granule from {url}")
    local_filename = url.split("/")[-1]
    headers = {"User-Agent": USER_AGENT}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    return local_filename


# Get the DEM
def get_dem_file(bounding_box):
    print("\nPreparing digital elevation model")
    temp_file = "temp_dem"
    dem_name = get_dem(bounding_box["lon_min"], bounding_box["lat_min"], bounding_box["lon_max"], bounding_box["lat_max"], temp_file, True, 30)
    cleanup("temp.vrt")
    cleanup("tempdem.tif")
    cleanup("temputm.tif")
    if "NED" in dem_name:
        cleanup("temp_dem_wgs84.tif")
    rmtree("DEM")
    system_call(["gdal_translate", "-ot", "Int16", temp_file, dem_name])
    cleanup(temp_file)
    return dem_name


# Code used a little everywhere
def system_call(params):
    print(" ".join(params))
    return_code = subprocess.call(params)
    if return_code:
        exit(return_code)


def cleanup(input_file):
    os.unlink(input_file)
    if input_file.endswith(".dim"):
        data_dir = input_file.replace(".dim", ".data")
        rmtree(data_dir)


def gpt(input_file, command, *args, dem_parameters=None, cleanup_flag=True):
    print(f"\n{command}")
    if dem_parameters is None:
        dem_parameters = []
    system_command = ["gpt", command, f"-Ssource={input_file}", "-t", command] + list(args) + dem_parameters
    system_call(system_command)
    if cleanup_flag:
        cleanup(input_file)
    return f"{command}.dim"


class ProcessGranule():

    def __init__(self, args, dem_parameters, dem_file, cleandem):
        self.granule = args.granule
        self.has_layover = args.has_layover
        self.has_incidence_angle = args.has_incidence_angle
        self.clean = args.clean
        self.dem_parameters = dem_parameters
        self.dem_file = dem_file
        self.cleandem = cleandem
        self.projection = "AUTO:42001"

        self.output_dir = f"/output"

    def process_granule(self, local_file):
        local_file = gpt(local_file, "Apply-Orbit-File")
        local_file = gpt(local_file, "Calibration", "-PoutputBetaBand=true", "-PoutputSigmaBand=false")

        range_looks = 3
        if "_SLC__" in self.granule:
            range_looks = 12
            local_file = gpt(local_file, "TOPSAR-Deburst")

        local_file = gpt(local_file, "Speckle-Filter")
        local_file = gpt(local_file, "Multilook", f"-PnRgLooks={range_looks}", "-PnAzLooks=3")
        terrain_flattening_file = gpt(local_file, "Terrain-Flattening", "-PreGridMethod=False", dem_parameters=self.dem_parameters)
        if self.has_layover:
            local_file = gpt(terrain_flattening_file, "SAR-Simulation", "-PsaveLayoverShadowMask=true", dem_parameters=self.dem_parameters, cleanup_flag=False)
            local_file = gpt(local_file, "Terrain-Correction", f"-PmapProjection={self.projection}", "-PimgResamplingMethod=NEAREST_NEIGHBOUR", "-PpixelSpacingInMeter=30.0", "-PsourceBands=layover_shadow_mask", dem_parameters=self.dem_parameters)
            self._process_img_files(local_file)

        local_file = gpt(terrain_flattening_file, "Terrain-Correction", "-PpixelSpacingInMeter=30.0", f"-PmapProjection={self.projection}", f"-PsaveProjectedLocalIncidenceAngle={self.has_incidence_angle}", dem_parameters=self.dem_parameters)
         
        if self.cleandem:
            cleanup(self.dem_file)
        self._process_img_files(local_file)
        self._create_arcgis_xml()

    def _process_img_files(self, dim_file):
        data_dir = dim_file.replace(".dim", ".data")
        for img_file in glob.glob(f"{data_dir}/*.img"):
            self._process_img_file(img_file)
        cleanup(dim_file)

    def _process_img_file(self, img_file):
        print("\nCreating output file")
        temp_file = "temp.tif"
        system_call(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", img_file, temp_file])
        cleanup(img_file)

        if "projectedLocalIncidenceAngle" in img_file:
            tiff_suffix = "PIA"
        elif "layover_shadow_mask" in img_file:
            tiff_suffix = "LS"
        else:
            if self.clean:
                temp_file = self._clean_pixels(temp_file)
            polarization = img_file[-6:-4]
            tiff_suffix = f"{polarization}_RTC"

        system_call(["gdaladdo", "-r", "average", temp_file, "2", "4", "8", "16"])
        system_call(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", temp_file, f"{self.output_dir}/{self.granule}_{tiff_suffix}.tif"])
        cleanup(temp_file)

    # Process images
    def _clean_pixels(self, temp_file):
        cleaned_file = "cleaned.tif"
        system_call(["gdal_calc.py", "-A", temp_file, f"--outfile={cleaned_file}", "--calc=A*(A>.005)", "--NoDataValue=0"])
        cleanup(temp_file)
        return cleaned_file

    # XML
    def _create_arcgis_xml(self):
        for tif_file in glob.glob(f"{self.output_dir}/{self.granule}_*_RTC.tif"):
            output_file = f"{tif_file}.xml"
            print(f"\nPreparing arcgis xml file {output_file}.")


            groups = re.match(f"{self.output_dir}/{self.granule}_(.*)_RTC.tif", tif_file)
            data = {
                "now": datetime.utcnow(),
                "polarization": groups[1],
                "input_granule": self.granule,
                "dem_name": self.dem_file,
            }

            template = self._get_xml_template()
            rendered = template.render(data)
            pretty_printed = self._pretty_print_xml(rendered)
            with open(output_file, "wb") as f:
                f.write(pretty_printed)

    @staticmethod
    def _get_xml_template():
        with open("arcgis_template.xml", "r") as t:
            template_text = t.read()
        template = Template(template_text)
        return template

    @staticmethod
    def _pretty_print_xml(content):
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.fromstring(content, parser)
        pretty_printed = etree.tostring(root, pretty_print=True)
        return pretty_printed


if __name__ == "__main__":
    parser = ArgumentParser(description="Radiometric Terrain Correction using the SENTINEL-1 Toolbox")
    parser.add_argument("--granule", "-g", type=str, help="Sentinel-1 granule name", required=True)
    parser.add_argument("--username", "-u", type=str, help="Earthdata Login username")
    parser.add_argument("--password", "-p", type=str, help="Earthdata Login password")
    parser.add_argument("--layover", "-l", dest="has_layover", action="store_true", help="Include layover shadow mask in ouput")
    parser.add_argument("--incidenceAngle", "-i", dest="has_incidence_angle", action="store_true", help="Include projected local incidence angle in ouput")
    parser.add_argument("--clean", "-c", dest="clean", action="store_true", help="Set very small pixel values to No Data. Helpful to clean edge artifacts of granules processed before IPF version 2.90.")
    parser.add_argument("--demName", "-d", type=str, help="The digital elevation model. Default %(default)s", choices=["ASF", "SRTM 1Sec Hgt", "SRTM 3Sec"], default="ASF")
    args = parser.parse_args()
    if not args.username:
        args.username = input("\nEarthdata Login username: ")

    if not args.password:
        args.password = getpass("\nEarthdata Login password: ")

    metadata = get_metadata(args.granule)
    if metadata is None:
        print(f"\nERROR: Either {args.granule} does exist or it is not a GRD/SLC product.")
        exit(1)

    if metadata["bounding_box"]["lon_min"] < -170 and metadata["bounding_box"]["lon_max"] > 170:
        print(f"\nERROR: Granules crossing the antimeridian are not supported.")
        exit(1)

    write_netrc_file(args.username, args.password)
    local_file = download_file(metadata["download_url"])

    if args.demName == "ASF":
        cleandem = True
        dem_file = get_dem_file(metadata["bounding_box"])
        dem_parameters = ["-PdemName='External DEM'", f"-PexternalDEMFile={dem_file}", "-PexternalDEMNoDataValue=-32767"]
    else:
        cleandem = False
        dem_file = args.demName
        dem_parameters = [f"-PdemName={args.demName}"]

    pg = ProcessGranule(args, dem_parameters, dem_file, cleandem)
    pg.process_granule(local_file)
