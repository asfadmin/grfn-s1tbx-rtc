#!/usr/local/bin/python

import os
import argparse
import requests
import subprocess
import shutil

CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION_IDS = [
    "C1214470533-ASF", # SENTINEL-1A_DUAL_POL_GRD_HIGH_RES
    "C1214471521-ASF", # SENTINEL-1A_DUAL_POL_GRD_MEDIUM_RES
    "C1214470488-ASF", # SENTINEL-1A_SLC
    "C1214470682-ASF", # SENTINEL-1A_SINGLE_POL_GRD_HIGH_RES
    "C1214472994-ASF", # SENTINEL-1A_SINGLE_POL_GRD_MEDIUM_RES
    "C1327985645-ASF", # SENTINEL-1B_DUAL_POL_GRD_HIGH_RES
    "C1327985660-ASF", # SENTINEL-1B_DUAL_POL_GRD_MEDIUM_RES
    "C1327985661-ASF", # SENTINEL-1B_SLC
    "C1327985571-ASF", # SENTINEL-1B_SINGLE_POL_GRD_HIGH_RES
    "C1327985740-ASF", # SENTINEL-1B_SINGLE_POL_GRD_MEDIUM_RES
]
USER_AGENT = "asfdaac/s1tbx-rtc"


def download_file(url):
    local_filename = url.split("/")[-1]
    headers = {'User-Agent': USER_AGENT}
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192): 
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
    for product in cmr_data["feed"]["entry"][0]["links"]:
        if "data" in product["rel"]:
            download_url = product["href"]
    return download_url


def get_args():
    parser = argparse.ArgumentParser(description="Radiometric Terrain Correction using the SENTINEL-1 Toolbox")
    parser.add_argument("--granule", "-g", type=str, help="Sentinel-1 Granule Name", required=True)
    parser.add_argument("--username", "-u", type=str, help="Earthdata Login Username", required=True)
    parser.add_argument("--password", "-p", type=str, help="Earthdata Login Password", required=True)
    args = parser.parse_args()
    return args


def write_netrc_file(username, password):
    netrc_file = os.environ["HOME"] + "/.netrc"
    with open(netrc_file, "w") as f:
        f.write("machine urs.earthdata.nasa.gov login " + username + " password " + password)


def delete_dim_files(name):
    os.unlink(name + ".dim")
    shutil.rmtree(name + ".data")


if __name__ == "__main__":
    args = get_args()

    print("\nFetching Granule Information")
    download_url = get_download_url(args.granule)

    print("\nDownloading Granule from " + download_url)
    write_netrc_file(args.username, args.password)
    local_file = download_file(download_url)
    
    print("\nApplying Orbit File")
    subprocess.run(["gpt", "Apply-Orbit-File", "-Ssource=" + local_file, "-t",  "Orb"])
    os.unlink(local_file)

    print("\nRunning Calibration")
    subprocess.run(["gpt", "Calibration", "-PoutputBetaBand=true", "-PoutputSigmaBand=false", "-Ssource=Orb.dim", "-t", "Cal"])
    delete_dim_files("Orb")

    print("\nRunning Terrain Flattening")
    subprocess.run(["gpt", "Terrain-Flattening", "-PdemName=SRTM 1Sec HGT", "-PreGridMethod=False", "-Ssource=Cal.dim", "-t", "TF"])
    delete_dim_files("Cal")

    print("\nRunning Terrain Correction")
    subprocess.run(["gpt", "Terrain-Correction", "-PpixelSpacingInMeter=30.0", "-PmapProjection=EPSG:32613", "-PdemName=SRTM 1Sec HGT", "-Ssource=TF.dim", "-t", "TC"])
    delete_dim_files("TF")

    for file_name in os.listdir("TC.data"):
        if file_name.endswith(".img"):
            polarization = file_name[-6:-4]
            temp_file_name = "temp.tif"
            output_file_name = args.granule + "_" + polarization + "_RTC.tif"
            print("\nCreating " + output_file_name)
            subprocess.run(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", "TC.data/" + file_name, temp_file_name])
            subprocess.run(["gdaladdo", "-r", "average", temp_file_name, "2", "4", "8", "16"])
            subprocess.run(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", temp_file_name, "/output/" + output_file_name])
            os.unlink(temp_file_name)
    delete_dim_files("TC")
