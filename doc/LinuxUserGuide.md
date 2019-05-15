# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* a 64-bit installation
* kernel at 3.10 or newer
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation

1. Follow the [Install Docker on linux](https://runnable.com/docker/install-docker-on-linux) instructions

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. Download the [s1tbx-rtc.sh](https://s3.amazonaws.com/asfdaac/s1tbx-rtc.bat) script to the directory where RTC products should be saved
1. Execute the s1tbx-rtc wrapper with granule name and desired options

