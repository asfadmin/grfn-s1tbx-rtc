#!/bin/bash
docker pull asfdaac/s1tbx-rtc
docker run -it -v $(pwd):/output --rm asfdaac/s1tbx-rtc "$@"
