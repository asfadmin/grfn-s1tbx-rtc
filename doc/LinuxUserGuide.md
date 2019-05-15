# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* a 64-bit installation
* kernel at 3.10 or newer
* Ubuntu, Debian, Redhat or CentOS
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation
### Ubuntu 18.04
1. Install Docker using apt<br>
   `sudo apt update`<br>
   `sudo apt install -y docker docker.io`
1. Add your user to the docker group<br>
  `sudo usermod -aG docker $USER`
1. Log out and log back in for the group change to take effect
1. To verify everything is working run the docker command <br>
  `docker run hello-world`<br>
 Confirm you see the following in your output<br>
 `Hello from Docker!`<br>
  `This message shows that your installation appears to be working correctly.`
### Centos 7
1. Install Docker<br>
`sudo yum install docker-engine -y`
1. Create a docker group and add your user to it<br>
`sudo groupadd docker && sudo usermod -aG docker $USER`
1. Log out and log back in for the group change to take effect
1. Start Docker<br>
`sudo service docker start`
1. To verify everything is working run the docker command <br>
  `docker run hello-world`<br>
 Confirm you see the following in your output<br>
 `Hello from Docker!`<br>
  `This message shows that your installation appears to be working correctly.`

### Other Linux Verisons
1. Follow the [Install Docker on linux](https://docs.docker.com/v17.12/install/) instructions

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. Download the [linux-s1tbx-rtc.sh](https://s3.amazonaws.com/asfdaac/linux-s1tbx-rtc.sh) script to the directory where RTC products should be saved
1. Execute the s1tbx-rtc wrapper with granule name and desired options

