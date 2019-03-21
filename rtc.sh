#!/bin/bash
set -xe

URS_USERNAME=$1
URS_PASSWORD=$2
GRANULE_URL=https://datapool.asf.alaska.edu/GRD_HD/SB/S1B_IW_GRDH_1SDV_20190203T010956_20190203T011021_014775_01B8E9_C18A.zip
GRANULE_NAME=S1B_IW_GRDH_1SDV_20190203T010956_20190203T011021_014775_01B8E9_C18A

wget --user $URS_USERNAME --password $URS_PASSWORD $GRANULE_URL

/usr/local/snap/bin/gpt Apply-Orbit-File -Ssource=$GRANULE_NAME.zip -t 1
rm $GRANULE_NAME.zip

/usr/local/snap/bin/gpt Calibration -PoutputBetaBand=true -PoutputSigmaBand=false -Ssource=1.dim -t 2
rm -R 1.dim 1.data

/usr/local/snap/bin/gpt Speckle-Filter -Ssource=2.dim -t 3
rm -R 2.dim 2.data

/usr/local/snap/bin/gpt Multilook -PnRgLooks=3 -PnAzLooks=3 -Ssource=3.dim -t 4
rm -R 3.dim 3.data

/usr/local/snap/bin/gpt Terrain-Flattening -PdemName="SRTM 1Sec HGT" -PreGridMethod=False -Ssource=4.dim -t 5
rm -R 4.dim 4.data

/usr/local/snap/bin/gpt Terrain-Correction -PpixelSpacingInMeter=30.0 -PmapProjection=EPSG:32613 -PdemName="SRTM 1Sec HGT" -Ssource=5.dim -t 6
rm -R 5.dim 5.data

gdal_translate -of GTiff -a_nodata 0 6.data/Gamma0_VH.img VH.tif
gdal_translate -of GTiff -a_nodata 0 6.data/Gamma0_VV.img VV.tif
rm -R 6.dim 6.data

gdaladdo -r average VH.tif 2 4 8 16
gdaladdo -r average VV.tif 2 4 8 16

gdal_translate -co TILED=YES -co COMPRESS=DEFLATE -co COPY_SRC_OVERVIEWS=YES VH.tif VH_final.tif
gdal_translate -co TILED=YES -co COMPRESS=DEFLATE -co COPY_SRC_OVERVIEWS=YES VV.tif VV_final.tif

rm -R VV.tif VH.tif 6.dim 6.data
