# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* Ubuntu, Debian, Redhat, or CentOS Linux
* 64-bit installation
* Kernel at 3.10 or newer
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation

### Ubuntu 18.04

1. Install Docker using apt
   ```
   sudo apt update
   sudo apt install -y docker docker.io
   ```
1. Add your user to the docker group
   ```
   sudo usermod -aG docker $USER
   ```
1. Log out and log back in for the group change to take effect
1. To verify everything is working run the docker command
   ```
   docker run hello-world
   ```
   Confirm you see the following in your output
   ```
   Hello from Docker!
   This message shows that your installation appears to be working correctly.
   ```
1. Download **s1tbx-rtc.sh** to the directory where RTC products should be saved
   ```
   wget https://s3.amazonaws.com/asfdaac/s1tbx-rtc.sh
   ```
### CentOS 7

1. Install Docker
   ```
   sudo yum install -y docker-engine
   ```
1. Create a docker group and add your user to it
   ```
   sudo groupadd docker
   sudo usermod -aG docker $USER
   ```
1. Log out and log back in for the group change to take effect
1. Start Docker
   ```
   sudo service docker start
   ```
1. To verify everything is working run the docker command
   ```
   docker run hello-world
   ```
   Confirm you see the following in your output
   ```
   Hello from Docker!
   This message shows that your installation appears to be working correctly.
   ```
1. Download **s1tbx-rtc.sh** to the directory where RTC products should be saved
   ```
   wget https://s3.amazonaws.com/asfdaac/s1tbx-rtc.sh
   ```


## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
   ```
   S1B_IW_GRDH_1SDV_20190512T161529_20190512T161554_016213_01E839_2D9F
   ```
1. Execute **s1tbx-rtc.sh** with the granule name and desired options
   ```
   sh s1tbx-rtc.sh --granule S1B_IW_GRDH_1SDV_20190512T161529_20190512T161554_016213_01E839_2D9F
   ```
   Processing can take up to several hours depending on the granule, internet connection, and computer resources
1. Upon completion, RTC products will appear in the directory where **s1tbx-rtc.sh** was executed
   ```
   
   
