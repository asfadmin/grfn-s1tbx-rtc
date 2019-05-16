#!/bin/bash
docker pull asfdaac/s1tbx-rtc
docker run -it -v $(pwd):/output --rm --user $(id -u):$(id -g) asfdaac/s1tbx-rtc "$@"
