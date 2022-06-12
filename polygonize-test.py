import osgeo.gdal as gdal

import ogr

path = "out/LC08_L2SP_143021_20220517_20220525_02_T1/UHI_MASK.TIF"

gdalData = gdal.Open(path)
gdalBand = gdalData.GetRasterBand(1)
newField = ogr.FieldDefn('MYFLD', ogr.OFTInteger)
driver = ogr.GetDriverByName("ESRI Shapefile")
outDatasource = driver.CreateDataSource('out/uhi.shp')
outLayer = outDatasource.CreateLayer("polygonized", srs=None)
outLayer.CreateField(newField)

print(gdalBand, outLayer)

gdal.Polygonize(gdalBand, None, outLayer, -1, [], callback=None)
