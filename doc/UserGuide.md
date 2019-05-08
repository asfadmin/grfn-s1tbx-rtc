# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* Windows 10
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation

1. Download the [Docker Desktop for Windows](https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe) installer
1. Follow the [Install Docker Desktop for Windows desktop app](https://docs.docker.com/docker-for-windows/install/#install-docker-desktop-for-windows-desktop-app) instructions
   1. Leave the 'Use Windows Containers instead of Linux Containers' option unchecked when prompted

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. [Start Docker Desktop for Windows](https://docs.docker.com/docker-for-windows/install/#install-docker-desktop-for-windows-desktop-app#start-docker-desktop-for-windows)
1. Download the [s1tbx-rtc.bat](https://s3.amazonaws.com/asfdaac/s1tbx-rtc.bat) script to the directory where RTC products should be saved
1. Run the s1tbx-rtc.bat script
   1. If prompted with "Windows protected your PC", click "More info", then "Run Anyway"
1. Provide your granule name, Earthdata Login username, and Earthdata Login password
1. Processing can take up to several hours depending on the granule, internet connection, and computer resources.
