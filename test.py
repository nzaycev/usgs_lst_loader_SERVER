# import numpy
#
# from main import bandAsArray
#
# ndvi = bandAsArray("out/pr4.tif", 1)
# NDVI = bandAsArray("out/NDVI.tif", 1)
#
# print(numpy.array_equal(ndvi, NDVI))

def defaultTemplate(dir):
    import os
    os.chdir(dir)
    filenames = os.listdir()
    print('listdir', filenames)
    os.chdir("../..")
    f = None
    # fd = f.split("_{0}")[0]
    for fn in filenames:
        if fn.find('SR_B5') > -1:
            f = fn.replace('SR_B5', '{0}')
            break
    os.chdir('out')
    fd = f.split("_{0}")[0]
    try:
        os.mkdir(f.split("_{0}")[0])
    except:
        pass
    os.chdir('..')
    print(f)
    if f == None:
        raise Exception('File error')
    from os.path import expanduser
    return dir + "/" + f, "{0}/USGS_Loader/out/{1}/{2}".format(expanduser('~').replace('\\\\', '/'), f.split("_{0}")[0], "{0}.TIF"), fd.replace('layers', 'out')


def unpack_zip(filename):
    import tarfile
    import os
    file = tarfile.open(filename)
    print('files', file.getnames())
    dir = filename.split('./')[1] + '_SOURCE'
    try:
        os.mkdir(dir)
        file.extractall(dir)
    except:
        pass
    return dir

if __name__ == '__main__':
    from usgs_test import checkScenes
    print(checkScenes()['results'][0]['temporalCoverage']['endDate'])
    # print(checkScenes()['temporalCoverage']['endDate'])
