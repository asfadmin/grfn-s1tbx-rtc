#!/usr/local/bin/python

import numpy, sys
from osgeo import gdal
from osgeo.gdalconst import GDT_Float32


def remove_small_raster_values(input_file, output_file, tolerance=0.003811):
    gdal.AllRegister()

    inputDS = gdal.Open(input_file)

    band1 = inputDS.GetRasterBand(1)
    rows = inputDS.RasterYSize
    cols = inputDS.RasterXSize

    sourceData = band1.ReadAsArray(0,0,cols,rows)
    driver = inputDS.GetDriver()
    outputDS = driver.Create(output_file, cols, rows, 1, GDT_Float32)

    outBand = outputDS.GetRasterBand(1)
    outData = numpy.zeros((rows,cols), numpy.float32)

    for row in range(0, rows):
        for col in range(0, cols):
            if sourceData[row,col] < tolerance:
                outData[row,col] = 0
            else:
                outData[row,col] = sourceData[row,col]

    outBand.WriteArray(outData, 0, 0)
    outBand.FlushCache()
    outBand.SetNoDataValue(0)

    outputDS.SetGeoTransform(inputDS.GetGeoTransform())
    outputDS.SetProjection(inputDS.GetProjection())

    del outData
