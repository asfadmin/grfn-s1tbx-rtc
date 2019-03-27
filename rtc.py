#!/usr/local/bin/python

import os
import argparse
import requests
import subprocess
import shutil

CMR_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"
COLLECTION_IDS = ["C1214470533-ASF","C1214471521-ASF","C1214470488-ASF","C1214470682-ASF","C1214472994-ASF","C1327985645-ASF","C1327985660-ASF","C1327985661-ASF","C1327985571-ASF"]


def download_file(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: 
                    f.write(chunk)
    return local_filename


def get_args():
    parser = argparse.ArgumentParser(description='Validate username and password.')
    parser.add_argument("--username", type=str, help="URS Username", required=1)
    parser.add_argument("--password", type=str, help="URS Password", required=1)
    parser.add_argument("--granule", type=str, help="Granule Name", required=1)
    args = parser.parse_args()
    return args


def write_netrc_file(username, password):
    netrc_file = os.environ['HOME'] + "/.netrc"
    with open(netrc_file, "w") as f:
        f.write("machine urs.earthdata.nasa.gov login " + username + " password " + password)


def delete_dim_files(name):
    os.unlink(name + ".dim")
    shutil.rmtree(name + ".data")


args = get_args()
params = dict(
    readable_granule_name=args.granule,
    provider='ASF',
    collection_concept_id=["C1214470533-ASF","C1214471521-ASF","C1214470488-ASF","C1214470682-ASF","C1214472994-ASF","C1327985645-ASF","C1327985660-ASF","C1327985661-ASF","C1327985571-ASF"]
)

cmr_url = "https://cmr.earthdata.nasa.gov/search/granules.json"
response = requests.get(url=cmr_url, params=params)
cmr_data = response.json()
download_url = ""
for product in cmr_data['feed']['entry'][0]['links']:
	if 'data' in product['rel']:
		download_url = product['href']

write_netrc_file(args.username, args.password)

local_file = download_file(download_url)

subprocess.run(["gpt", "Apply-Orbit-File", "-Ssource=" + local_file, "-t",  "Orb"])
os.unlink(local_file)

subprocess.run(["gpt", "Calibration", "-PoutputBetaBand=true", "-PoutputSigmaBand=false", "-Ssource=Orb.dim", "-t", "Cal"])
delete_dim_files("Orb")

subprocess.run(["gpt", "Terrain-Flattening", "-PdemName=SRTM 1Sec HGT", "-PreGridMethod=False", "-Ssource=Cal.dim", "-t", "TF"])
delete_dim_files("Cal")

subprocess.run(["gpt", "Terrain-Correction", "-PpixelSpacingInMeter=30.0", "-PmapProjection=EPSG:32613", "-PdemName=SRTM 1Sec HGT", "-Ssource=TF.dim", "-t", "TC"])
delete_dim_files("TF")

subprocess.run(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", "TC.data/Gamma0_VH.img", "VH.tif"])
subprocess.run(["gdal_translate", "-of", "GTiff", "-a_nodata", "0", "TC.data/Gamma0_VV.img", "VV.tif"])
delete_dim_files("TC")

subprocess.run(["gdaladdo", "-r", "average", "VH.tif", "2", "4", "8", "16"])
subprocess.run(["gdaladdo", "-r", "average", "VV.tif", "2", "4", "8", "16"])

subprocess.run(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", "VH.tif", "/output/" + args.granule + "_vh.tif"])
subprocess.run(["gdal_translate", "-co", "TILED=YES", "-co", "COMPRESS=DEFLATE", "-co", "COPY_SRC_OVERVIEWS=YES", "VV.tif", "/output/" + args.granule + "_vv.tif"])
os.unlink("VV.tif")
os.unlink("VH.tif")
