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
[Ubuntu Setup](https://docs.docker.com/v17.12/install/linux/docker-ce/ubuntu/)
1. update apt
`sudo apt-get update`
1. install docker: 
 `sudo apt-get install docker-ce -y`
1. create a docker group and add a user to it:
`sudo usermod -aG docker ubuntu`
1. restart the machine:
`sudo shutdown -r now`
1. start docker
`sudo service docker start`
1. verify that docker is running:
`docker run hello-world`

[Centos Setup](https://docs.docker.com/v17.12/install/linux/docker-ce/centos/)
1. install docker: 
`sudo yum install docker-engine -y`
1. create a docker group and add a user to it (replace USERNAME with your username):
` sudo groupadd docker && sudo usermod -aG docker USERNAME`
1. restart the machine:
`sudo shutdown -r now`
1. start docker
`sudo service docker start`
1. verify that docker is running:
`docker run hello-world`

Other Linux Verisons
1. Follow the [Install Docker on linux](https://docs.docker.com/v17.12/install/) instructions

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. Download the [linux-s1tbx-rtc.sh](https://s3.amazonaws.com/asfdaac/linux-s1tbx-rtc.sh) script to the directory where RTC products should be saved
1. Execute the s1tbx-rtc wrapper with granule name and desired options

