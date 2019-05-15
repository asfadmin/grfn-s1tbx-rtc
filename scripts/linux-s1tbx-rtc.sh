#!/bin/bash
docker run -it --cpus=0 --memory 16g -v $(pwd):/output --rm asfdaac/s1tbx-rtc "$@"
