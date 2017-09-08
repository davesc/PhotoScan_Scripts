# DJI_drone_barometer_altitide_for_PhotoScan(input_directory, output_file_name, [-recursive]) 
# Grab barometer altitude from DJI jpegs and create 
# a text file to use them with Agisoft PhotoScan.
# The GPS altitude on most DJI drones is so bad you 
# can't use it with PhotoScan. Better to use the
# barometer altitude, which will need an offset if
# you did not take off from sea level. 

import glob
import sys
from PIL import Image


basedir = sys.argv[1]
if basedir[-1]=='/':
    basedir = basedir[:-1]

for fname in glob.iglob(basedir+'/**/DJI_*.JPG', recursive=True):
    
    
    
# check out this example of exif using PIL 
# https://gist.github.com/erans/983821
    
# get the XMP data
'''
with Image.open(filename) as im:
    for segment, content in im.applist:
        marker, body = content.split(b'\x00', 1)
        if segment == 'APP1' and marker == b'http://ns.adobe.com/xap/1.0/':
            c = str(content)
            print( (c.split('drone-dji:GimbalRollDegree=\"'))[1].split('\"')[0])
'''            

