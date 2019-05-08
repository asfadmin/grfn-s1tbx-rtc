# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* Mac hardware 2010 and newer
* macOS Sierra 10.12 and newer
* VirtualBox prior to version 4.3.30 must NOT be installed
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation

1. Download and install [Docker Desktop for OSX](https://download.docker.com/mac/stable/Docker.dmg)
1. Download the [s1tbx-rtc.sh](https://s3.amazonaws.com/asfdaac/s1tbx-rtc.sh) convenience script

## Configure Docker

1. Open Docker and click preferences
1. clock on advanced and allocate the correct RAM and CPU to docker
![advanced](https://docs.docker.com/docker-for-mac/images/menu/prefs-advanced.png)

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. Make sure Docker is running
1. Download the [s1tbx-rtc.sh](https://s3.amazonaws.com/asfdaac/s1tbx-rtc.sh) script to the directory where RTC products should be saved
1. Run the s1tbx-rtc.bat script
1. Provide your granule name, Earthdata Login username, and Earthdata Login password

## Advanced Options
