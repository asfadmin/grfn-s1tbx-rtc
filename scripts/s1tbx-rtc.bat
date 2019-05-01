@echo off
echo Checking for updates
docker pull asfdaac/s1tbx-rtc
echo.
set /p GRANULE="Granule: "
docker run -it -v %CD%:/output --rm asfdaac/s1tbx-rtc --granule %GRANULE%
@pause
