#!/usr/local/bin/python3

# Standard libraries
import os
import math
import subprocess
from argparse import ArgumentParser
from shutil import rmtree
from datetime import datetime

# pip3 install
import requests
from shapely.geometry import Polygon
from jinja2 import Template
from lxml import etree
from get_dem import get_dem

CHUNK_SIZE = 5242880
CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION_IDS = [
    "C1214470533-ASF", # SENTINEL-1A_DUAL_POL_GRD_HIGH_RES
    "C1214471521-ASF", # SENTINEL-1A_DUAL_POL_GRD_MEDIUM_RES
    "C1214470682-ASF", # SENTINEL-1A_SINGLE_POL_GRD_HIGH_RES
    "C1214472994-ASF", # SENTINEL-1A_SINGLE_POL_GRD_MEDIUM_RES
    "C1327985645-ASF", # SENTINEL-1B_DUAL_POL_GRD_HIGH_RES
    "C1327985660-ASF", # SENTINEL-1B_DUAL_POL_GRD_MEDIUM_RES
    "C1327985571-ASF", # SENTINEL-1B_SINGLE_POL_GRD_HIGH_RES
    "C1327985740-ASF", # SENTINEL-1B_SINGLE_POL_GRD_MEDIUM_RES
]
USER_AGENT = "asfdaac/s1tbx-rtc"

# Metadata
def get_download_url(entry):
    for product in entry["links"]:
        if "data" in product["rel"]:
            return product["href"]
    return None

def get_poly(entry):
    floats = [float(ii) for ii in entry['polygons'][0][0].split()]
    points = zip(floats[::2], floats[1::2])
    return Polygon(points)

def get_utm_projection(poly):
    lat, lon = poly.centroid.coords[0]

    utm_band = (math.floor((lon + 180) / 6) % 60) + 1
    if lat >= 0:
        return f"EPSG:326{utm_band:02}"
    else:
        return f"EPSG:327{utm_band:02}"

def get_bbox(poly):
    return {
        "lat_min": poly.bounds[0],
        "lon_min": poly.bounds[1],
        "lat_max": poly.bounds[2],
        "lon_max": poly.bounds[3],
    }

def get_metadata(granule):
    params = {
        "readable_granule_name": granule,
        "provider": "ASF",
        "collection_concept_id": COLLECTION_IDS
    }
    response = requests.get(url=CMR_URL, params=params)
    response.raise_for_status()
    cmr_data = response.json()

    if cmr_data["feed"]["entry"]:
        entry = cmr_data["feed"]["entry"][0]
        poly = get_poly(entry)
        return {
            'download_url': get_download_url(entry),
            'bbox': get_bbox(poly),
            'utm_projection': get_utm_projection(poly)
        }
    return None

# Write a netrc file
def write_netrc_file(username, password):
    netrc_file = os.environ["HOME"] + "/.netrc"
    with open(netrc_file, "w") as f:
        f.write(f"machine urs.earthdata.nasa.gov login {username} password {password}")

# Download the granule file
def download_file(url):
    local_filename = url.split("/")[-1]
    headers = {'User-Agent': USER_AGENT}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    return local_filename

# Get the DEM
def get_dem_file(bbox):
    temp_file = "temp_dem"
    dem_name = get_dem(bbox['lon_min'], bbox['lat_min'], bbox['lon_max'], bbox['lat_max'], temp_file, True, 30)
    cleanup("temp.vrt")
    cleanup("tempdem.tif")
    cleanup("temputm.tif")
    cleanup("temp_dem_wgs84.tif")
    rmtree("DEM")
    system_call(["gdal_translate", "-ot", "Int16", temp_file, dem_name])
    cleanup(temp_file)
    return dem_name

# XML
def get_xml_template():
    with open('arcgis_template.xml', 'r') as t:
        template_text = t.read()
    template = Template(template_text)
    return template

def pretty_print_xml(content):
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(content, parser)
    pretty_printed = etree.tostring(root, pretty_print=True)
    return pretty_printed

def create_arcgis_xml(input_granule, output_file, polarization):
    template = get_xml_template()
    data = {
        'now': datetime.utcnow(),
        'polarization': polarization,
        'input_granule': input_granule,
        'acquisition_year': input_granule[17:21],
    }
    rendered = template.render(data)
    pretty_printed = pretty_print_xml(rendered)
    with open(output_file, 'wb') as f:
        f.write(pretty_printed)

# Process images
def create_geotiff_from_img(input_file, output_file):
    print(f"\nCreating {output_file}")
    temp_file = "temp.tif"
    system_call(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", input_file, temp_file])
    system_call(["gdaladdo", "-r", "average", temp_file, "2", "4", "8", "16"])
    system_call(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", temp_file, output_file])
    cleanup(temp_file)

def get_img_files(dim_file):
    img_files = []
    data_dir = dim_file.replace('.dim', '.data')
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".img"):
            img_files.append(f"{data_dir}/{file_name}")
    return img_files

def process_img_files(granule, dim_file):
    for img_file in get_img_files(dim_file):
        if 'projectedLocalIncidenceAngle' in img_file:
            tif_file_name = f"/output/{granule}_PIA.tif"
        elif 'layover_shadow_mask' in img_file:
            tif_file_name = f"/output/{granule}_LS.tif"
        else:
            polarization = img_file[-6:-4]
            tif_file_name = f"/output/{granule}_{polarization}_RTC.tif"
            create_arcgis_xml(granule, f"{tif_file_name}.xml", polarization)
        create_geotiff_from_img(img_file, tif_file_name)
    cleanup(dim_file)
    return None

def processing_granule(granule, has_incidence_angle, has_layover, local_file, dem_file, utm_projection):
    local_file = gpt(local_file, "Apply-Orbit-File")
    local_file = gpt(local_file, "Calibration", "-PoutputBetaBand=true", "-PoutputSigmaBand=false")
    local_file = gpt(local_file, "Speckle-Filter")
    local_file = gpt(local_file, "Multilook", "-PnRgLooks=3", "-PnAzLooks=3")
    terrain_flattening_file = gpt(local_file, "Terrain-Flattening", "-PreGridMethod=False", "-PdemName=External DEM", f"-PexternalDEMFile={dem_file}", "-PexternalDEMNoDataValue=-32767")

    if has_layover:
        local_file = gpt(terrain_flattening_file, "SAR-Simulation", "-PdemName=External DEM", f"-PexternalDEMFile={dem_file}", "-PexternalDEMNoDataValue=-32767", "-PsaveLayoverShadowMask=true", cleanup_flag=False)
        local_file = gpt(local_file, "Terrain-Correction", f"-PmapProjection={utm_projection}", "-PimgResamplingMethod=NEAREST_NEIGHBOUR", "-PpixelSpacingInMeter=30.0", "-PsourceBands=layover_shadow_mask",
                         "-PdemName=External DEM", f"-PexternalDEMFile={dem_file}", "-PexternalDEMNoDataValue=-32767")
        process_img_files(granule, local_file)

    local_file = gpt(terrain_flattening_file, "Terrain-Correction", "-PpixelSpacingInMeter=30.0", f"-PmapProjection={utm_projection}", f"-PsaveProjectedLocalIncidenceAngle={has_incidence_angle}", "-PdemName=External DEM",
                     f"-PexternalDEMFile={dem_file}", "-PexternalDEMNoDataValue=-32767", cleanup_flag=True)
    cleanup(dem_file)
    process_img_files(granule, local_file)

# Code used a little everywhere
def system_call(params):
    print(' '.join(params))
    return_code = subprocess.call(params)
    if return_code:
        exit(return_code)
    return None

def cleanup(input_file):
    os.unlink(input_file)
    if input_file.endswith(".dim"):
        data_dir = input_file.replace(".dim", ".data")
        rmtree(data_dir)

def gpt(input_file, command, *args, cleanup_flag=True):
    print(f"\n{command}")
    system_command = ["gpt", command, f"-Ssource={input_file}", "-t", command] + list(args)
    system_call(system_command)
    if cleanup_flag:
        cleanup(input_file)
    return f"{command}.dim"

if __name__ == "__main__":
    parser = ArgumentParser(description="Radiometric Terrain Correction using the SENTINEL-1 Toolbox")
    parser.add_argument("--granule", "-g", type=str, help="Sentinel-1 granule name", required=True)
    parser.add_argument("--username", "-u", type=str, help="Earthdata login username", required=True)
    parser.add_argument("--password", "-p", type=str, help="Earthdata login password", required=True)
    parser.add_argument("--layover", "-l", dest="has_layover", action='store_true', help="Include layover shadow mask in ouput")
    parser.add_argument("--incidence_angle", "-i", dest="has_incidence_angle", action='store_true', help="Include incidence angle in ouput")
    args = parser.parse_args()

    print("\nFetching Granule Information")
    metadata = get_metadata(args.granule)
    if metadata is None:
        print(f"\nERROR: Either {args.granule} does exist or it is not a GRD product.")
        exit(1)

    print("\nWriting .netrc File")
    write_netrc_file(args.username, args.password)

    print("\nPreparing Digital Elevation Model")
    dem_file = get_dem_file(metadata['bbox'])

    print(f"\nDownloading Granule from {metadata['download_url']}")
    local_file = download_file(metadata['download_url'])

    print("\nProcessing Granule")
    processing_granule(args.granule, args.has_incidence_angle, args.has_layover, local_file, dem_file, metadata['utm_projection'])
