#!/bin/bash
set -xe

URS_USERNAME=$2
URS_PASSWORD=$3
GRANULE_URL=https://datapool.asf.alaska.edu/GRD_HD/SB/S1B_IW_GRDH_1SDV_20190203T010956_20190203T011021_014775_01B8E9_C18A.zip
GRANULE_NAME=S1B_IW_GRDH_1SDV_20190203T010956_20190203T011021_014775_01B8E9_C18A

wget --user $URS_USERNAME --password $URS_PASSWORD --progress=dot:giga $GRANULE_URL

/usr/local/snap/bin/gpt Apply-Orbit-File -Ssource=$GRANULE_NAME.zip -t Orb
rm $GRANULE_NAME.zip

/usr/local/snap/bin/gpt Calibration -PoutputBetaBand=true -PoutputSigmaBand=false -Ssource=Orb.dim -t Cal
rm -R Orb.dim Orb.data

/usr/local/snap/bin/gpt Terrain-Flattening -PdemName="SRTM 1Sec HGT" -PreGridMethod=False -Ssource=Cal.dim -t TF
rm -R Cal.dim Cal.data

/usr/local/snap/bin/gpt Terrain-Correction -PpixelSpacingInMeter=30.0 -PmapProjection=EPSG:32613 -PdemName="SRTM 1Sec HGT" -Ssource=TF.dim -t TC
rm -R TF.dim TF.data

gdal_translate -of GTiff -a_nodata 0 TC.data/Gamma0_VH.img VH.tif
gdal_translate -of GTiff -a_nodata 0 TC.data/Gamma0_VV.img VV.tif
rm -R TC.dim TC.data

gdaladdo -r average VH.tif 2 4 8 16
gdaladdo -r average VV.tif 2 4 8 16

gdal_translate -co TILED=YES -co COMPRESS=DEFLATE -co COPY_SRC_OVERVIEWS=YES VH.tif /output/s1b-iw-grd-vh-20190203t010956-20190203t011021-014775-01b8e9-002-rtc.tif
gdal_translate -co TILED=YES -co COMPRESS=DEFLATE -co COPY_SRC_OVERVIEWS=YES VV.tif /output/s1b-iw-grd-vv-20190203t010956-20190203t011021-014775-01b8e9-001-rtc.tif

rm -R VV.tif VH.tif
