#!/bin/bash
echo Checking for updates
docker pull asfdaac/s1tbx-rtc
echo
read -p "Granule: " GRANULE
docker run -it --cpus=0 --memory 16g -v $(pwd):/output --rm asfdaac/s1tbx-rtc --granule $GRANULE
echo
read -p "Press any key to continue"
