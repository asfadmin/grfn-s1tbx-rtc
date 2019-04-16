#!/usr/local/bin/python

import os
import math
import requests
import subprocess
from argparse import ArgumentParser
from shutil import rmtree
from datetime import datetime
from jinja2 import Template
from lxml import etree

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


def process_img_files(local_file, extension, create_xml=True, include_polarization=True):
    data_dir = local_file.replace(".dim", ".data")
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".img"):
            polarization = file_name[-6:-4]
            if include_polarization:
                tif_file_name = f"/output/{args.granule}_{polarization}_{extension}"
            else:
                tif_file_name = f"/output/{args.granule}_{extension}"
            if 'projectedLocalIncidenceAngle' in file_name:
                tif_file_name = f"/output/{args.granule}_PIA.tif"
            create_geotiff_from_img(f"{data_dir}/{file_name}", tif_file_name)
            if create_xml and 'projectedLocalIncidenceAngle' not in file_name:
                create_arcgis_xml(args.granule, f"{tif_file_name}.xml", polarization)

    cleanup(local_file)
    return None


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


def get_download_url(granule):
    params = {
        "readable_granule_name": granule,
        "provider": "ASF",
        "collection_concept_id": COLLECTION_IDS
    }
    response = requests.get(url=CMR_URL, params=params)
    response.raise_for_status()
    cmr_data = response.json()
    download_url = ""
    if cmr_data["feed"]["entry"]:
        for product in cmr_data["feed"]["entry"][0]["links"]:
            if "data" in product["rel"]:
                return product["href"]
    return None


def get_args():
    parser = ArgumentParser(description="Radiometric Terrain Correction using the SENTINEL-1 Toolbox")
    parser.add_argument("--granule", "-g", type=str, help="Sentinel-1 granule name", required=True)
    parser.add_argument("--username", "-u", type=str, help="Earthdata login username", required=True)
    parser.add_argument("--password", "-p", type=str, help="Earthdata login password", required=True)
    parser.add_argument("--layover", "-l", action='store_true', help="Include layover shadow mask in ouput")
    parser.add_argument("--incidence_angle", "-i", action='store_true', help="Include incidence angle in ouput")
    args = parser.parse_args()
    return args


def write_netrc_file(username, password):
    netrc_file = os.environ["HOME"] + "/.netrc"
    with open(netrc_file, "w") as f:
        f.write(f"machine urs.earthdata.nasa.gov login {username} password {password}")


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


def create_geotiff_from_img(input_file, output_file):
    print(f"\nCreating {output_file}")
    temp_file = "temp.tif"
    system_call(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", input_file, temp_file])
    system_call(["gdaladdo", "-r", "average", temp_file, "2", "4", "8", "16"])
    system_call(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", temp_file, output_file])
    cleanup(temp_file)


def get_xml_template():
    with open('arcgis_template.xml', 'r') as t:
        template_text = t.read()
    template = Template(template_text)
    return template


def convert_wgs_to_utm(lon, lat):
    utm_band = str((math.floor((lon + 180) / 6) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0' + utm_band
    if lat >= 0:
        epsg_code = '326' + utm_band
    else:
        epsg_code = '327' + utm_band
    return f"EPSG:{epsg_code}"


def get_center_point(file_name):
    output = json.loads(subprocess.check_output(['gdalinfo', '-json', file_name]))
    lon, lat = output['cornerCoordinates']['center']
    return lon, lat


def get_utm_projection(file_name):
    lon, lat = get_center_point(file_name)
    utm_projection = convert_wgs_to_utm(lon, lat)
    return utm_projection


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


if __name__ == "__main__":
    args = get_args()
    inc_angle = "true" if args.incidence_angle else "false"

    print("\nFetching Granule Information")
    download_url = get_download_url(args.granule)
    if download_url is None:
        print(f"\nERROR: Either {args.granule} does exist or it is not a GRD product.")
        exit(1)

    print(f"\nDownloading granule from {download_url}")
    write_netrc_file(args.username, args.password)
    local_file = download_file(download_url)

    local_file = gpt(local_file, "Apply-Orbit-File")
    local_file = gpt(local_file, "Calibration", "-PoutputBetaBand=true", "-PoutputSigmaBand=false")
    local_file = gpt(local_file, "Speckle-Filter")
    local_file = gpt(local_file, "Multilook", "-PnRgLooks=3", "-PnAzLooks=3")
    terrain_flattening_file = gpt(local_file, "Terrain-Flattening", "-PreGridMethod=False")

    utm_projection = get_utm_projection(terrain_flattening_file)

    if args.layover:
        local_file = gpt(terrain_flattening_file, "SAR-Simulation", "-PdemName=SRTM 1Sec HGT", "-PsaveLayoverShadowMask=true", cleanup_flag=False)
        local_file = gpt(local_file, "Terrain-Correction", f"-PmapProjection={utm_projection}", "-PimgResamplingMethod=NEAREST_NEIGHBOUR", "-PpixelSpacingInMeter=30.0", "-PsourceBands=layover_shadow_mask", "-PdemName=SRTM 1Sec HGT")
        process_img_files(local_file, 'LS.tif', create_xml=False, include_polarization=False)

    local_file = gpt(terrain_flattening_file, "Terrain-Correction", "-PpixelSpacingInMeter=30.0", f"-PmapProjection={utm_projection}", "-PdemName=SRTM 1Sec HGT", f"-PsaveProjectedLocalIncidenceAngle={inc_angle}", cleanup_flag=True)
    process_img_files(local_file, "RTC.tif")

