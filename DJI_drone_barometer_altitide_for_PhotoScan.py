#!/usr/bin/env python3

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



def get_exif_gps(image):
    exif = image._getexif()
    gps_out = {'lat':float('nan'), 'lon':float('nan'), 'alt':float('nan')}
    if exif:
        # latitude in decimal degrees
        gps_out['lat'] = (float(exif[34853][2][0][0])/float(exif[34853][2][0][1])
                        + float(exif[34853][2][1][0])/float(exif[34853][2][1][1])/60
                        + float(exif[34853][2][2][0])/float(exif[34853][2][2][1])/3600)
        if exif[34853][1][0][0] == 'N':
            gps_out['lat'] = -gps_out['lat']
        # longitude in decimal degrees
        gps_out['lon'] = (float(exif[34853][4][0][0])/float(exif[34853][4][0][1])
                        + float(exif[34853][4][1][0])/float(exif[34853][4][1][1])/60
                        + float(exif[34853][4][2][0])/float(exif[34853][4][2][1])/3600)
        if exif[34853][3][0][0] == 'W':
            gps_out['lon'] = -gps_out['lon']
        # gps altitude in m
        gps_out['alt'] = float(exif[34853][6][0])/float(exif[34853][6][1])
        if exif[34853][5][0] == 1:
            gps_out['alt'] = -gps_out['alt']
    return gps_out


def get_xmp_dji(image):
    dji = {'rel_alt':float('nan'), 'yaw':float('nan'), 'pitch':float('nan'), 
           'roll':float('nan')}
    for chunk, content in image.applist:
        id, __ = content.split(b'\x00', 1)
        if id == b'http://ns.adobe.com/xap/1.0/' and chunk == 'APP1':
            c = str(content)
            # relative altitude from takeoff in meters, using barometer
            dji['rel_alt'] = (
                float(c.split('drone-dji:RelativeAltitude=\"')[1].split('\"')[0]))
            # gimble yaw degrees
            dji['yaw'] = (
                float(c.split('drone-dji:GimbalYawDegree=\"')[1].split('\"')[0]))
            # gimble pitch degrees
            dji['pitch'] = (
                float(c.split('drone-dji:GimbalPitchDegree=\"')[1].split('\"')[0]))
            # gimble roll degrees
            dji['roll'] = (
                float(c.split('drone-dji:GimbalRollDegree=\"')[1].split('\"')[0]))
    return dji


fname  = sys.argv[1]
with Image.open(fname) as im:
    dji = get_xmp_dji(im)
    gps = get_exif_gps(im)
    print(dji)
    print(gps)



# 
# basedir = sys.argv[1]
# if basedir[-1]=='/':
#     basedir = basedir[:-1]
# 
# for fname in glob.iglob(basedir+'/**/DJI_*.JPG', recursive=True):
#     
# # 34853    1   GPSInfo Exif.GPSInfo.GPSLatitudeRef, 'N' or 'S'
# # 34853    2   GPSInfo Exif.GPSInfo.GPSLatitude
# # 34853    3   GPSInfo Exif.GPSInfo.GPSLongitudeRef, 'E' or 'W'
# # 34853    4   GPSInfo Exif.GPSInfo.GPSLongitude
# # 34853    5   GPSInfo Exif.GPSInfo.GPSAltitudeRef,  '0' above sea level or '1' below
# # 34853    6   GPSInfo Exif.GPSInfo.GPSAltitude
#     
# #GPS info 34853
# #Lat deg,  float(info[34853][2][0][0])/float(info[34853][2][0][1]) 
# #Lat min,  float(info[34853][2][1][0])/float(info[34853][2][1][1]) 
# #Lat sec,  float(info[34853][2][2][0])/float(info[34853][2][2][1])    
#     
# # check out this example of exif using PIL 
# # https://gist.github.com/erans/983821
#     
# # get the XMP data
# '''
# with Image.open(filename) as im:
#     for segment, content in im.applist:
#         marker, body = content.split(b'\x00', 1)
#         if segment == 'APP1' and marker == b'http://ns.adobe.com/xap/1.0/':
#             c = str(content)
#             print( (c.split('drone-dji:GimbalPitchDegree=\"'))[1].split('\"')[0])
#             
# drone-dji:RelativeAltitude
# drone-dji:GimbalRollDegree
# drone-dji:GimbalYawDegree
# drone-dji:GimbalPitchDegree            
# '''            
# 
# def get_exif_data(image):
#     """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
#     exif_data = {}
#     info = image._getexif()
#     if info:
#         for tag, value in info.items():
#             decoded = TAGS.get(tag, tag)
#             if decoded == "GPSInfo":
#                 gps_data = {}
#                 for t in value:
#                     sub_decoded = GPSTAGS.get(t, t)
#                     gps_data[sub_decoded] = value[t]
# 
#                 exif_data[decoded] = gps_data
#             else:
#                 exif_data[decoded] = value
# 
#     return exif_data
# 
# def _get_if_exist(data, key):
#     if key in data:
#         return data[key]
# 		
#     return None
# 	
# def _convert_to_degress(value):
#     """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
#     d0 = value[0][0]
#     d1 = value[0][1]
#     d = float(d0) / float(d1)
# 
#     m0 = value[1][0]
#     m1 = value[1][1]
#     m = float(m0) / float(m1)
# 
#     s0 = value[2][0]
#     s1 = value[2][1]
#     s = float(s0) / float(s1)
# 
#     return d + (m / 60.0) + (s / 3600.0)
# 
# def get_lat_lon(exif_data):
#     """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
#     lat = None
#     lon = None
# 
#     if "GPSInfo" in exif_data:		
#         gps_info = exif_data["GPSInfo"]
# 
#         gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
#         gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
#         gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
#         gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')
# 
#         if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
#             lat = _convert_to_degress(gps_latitude)
#             if gps_latitude_ref != "N":                     
#                 lat = 0 - lat
# 
#             lon = _convert_to_degress(gps_longitude)
#             if gps_longitude_ref != "E":
#                 lon = 0 - lon
# 
#     return lat, lon