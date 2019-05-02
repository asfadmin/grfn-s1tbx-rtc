# User Guide

## Background

Distortions in Synthetic-aperture radar (SAR) imagery are induced by the side-looking nature of SAR sensors and are compounded by rugged terrain. Terrain correction corrects geometric distortions that lead to geolocation errors by moving image pixels into the proper spatial relationship with each other based on a Digital Elevation Model (DEM). Radiometric correction removes the misleading influence of topography on backscatter values. Radiometric Terrain Correction (RTC) combines both corrections to produce a superior product for science applications.

## System Requirements

* Windows 10
* 16 GB of RAM
* 20 GB of available hard disk space

## Installation

1. Download and install [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
1. Download the [s1tbx-rtc.bat](../scripts/s1tbx-rtc.bat) convenience script

## Usage

1. Find the name of the GRD or SLC granule to process from [Vertex](https://vertex.daac.asf.alaska.edu/)
1. Make sure Docker is running
1. Download the <a href="../scripts/s1tbx-rtc.bat" download>s1tbx-rtc.bat</a> script to the directory where RTC products saved
1. Run the s1tbx-rtc.bat script
1. Provide your granule name, Earthdata Login username, and Earthdata Login password

## Advanced Options

