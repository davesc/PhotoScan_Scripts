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
import os
import argparse 

from PIL import Image



def get_exif_gps(image):
    exif = image._getexif()
    gps_out = {'lat':float('nan'), 'lon':float('nan'), 'alt':float('nan')}
    if exif:
        try:
            # latitude in decimal degrees
            gps_out['lat'] = (float(exif[34853][2][0][0])/float(exif[34853][2][0][1])
                        + float(exif[34853][2][1][0])/float(exif[34853][2][1][1])/60
                        + float(exif[34853][2][2][0])/float(exif[34853][2][2][1])/3600)
            if exif[34853][1][0][0] == 'S':
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
        except:
            print('{}: could not find GPS data'.format(fname))
    return gps_out


def get_xmp_dji(image):
    dji = {'rel_alt':float('nan'), 'yaw':float('nan'), 'pitch':float('nan'), 
           'roll':float('nan')}
    for chunk, content in image.applist:
        id, __ = content.split(b'\x00', 1)
        if id == b'http://ns.adobe.com/xap/1.0/' and chunk == 'APP1':
            try:
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
                # add 90 to convert from DJI reference frame to PhotoScan frame    
                dji['pitch'] = dji['pitch']+90
                # gimble roll degrees
                dji['roll'] = (
                    float(c.split('drone-dji:GimbalRollDegree=\"')[1].split('\"')[0]))
            except:
                print('{}: could not find DJI altitude or gimbal data'.format(fname))
    return dji


parser = argparse.ArgumentParser(description='This script pulls GPS data, DJI gimbal '
                                   +'data, and DJI relative altitude from DJI jpegs and '
                                   +'stores them in a text file for easy input into '
                                   +'Agisoft PhotoScan',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-r', '--recursive', action='store_true', default=False, 
                    help='search for DJI jpegs recursively')
parser.add_argument('-i', '--input',action='store',type=str,default='./',
                    help=('input directory to search for DJI jepgs (recursive with -r), '
                            +'or an input filename'))
parser.add_argument('-o','--output', action='store',type=str,
                    default='[output_directory]/DJI_camera_poses.txt',
                    help='file path/name for output text file') 
parser.add_argument('-e','--elevation', action='store',type=float,
                    default=0,
                    help=('elevation offset for the relative (barometer) altitide, '
                         +'generally this is the drone takeoff elevation and converts '
                         +'realtive altitide to a georefferenced elevation. Note: this '
                         +'is only useful if you used the same takeoff location for '
                         +'all the images you process at one time.'))
                    
input_args = parser.parse_args()                                 


# get the file names
path = input_args.input
# I think this should work on a Windoze machine ... not tested  
if path=='./' or path=='.':
    path = os.getcwd()
if path[-1]=='/':
    path = path[:-1]
if os.path.isdir(path):
    isdir = True
    if input_args.recursive:
        fnames = glob.iglob(path+'/**/DJI*.JPG', recursive=True)
    else:
        fnames = glob.iglob(path+'/DJI*.JPG', recursive=False)    
elif os.path.isfile(path):
    fnames = glob.iglob(path)
    isdir = False
else:
    print('could not find file or directory')
    sys.exit()

# output text file name
if input_args.output == '[output_directory]/DJI_camera_poses.txt':
    if isdir:
        fname_out = (path + '/DJI_camera_poses.txt')
    else:
        fname_out = (path.rsplit('/',1)[0] + '/DJI_camera_poses.txt')
else:
    fname_out = input_args.output


with open(fname_out,'w') as fout:
    fout.write('File, Lat, Lon, GPS_altitude, Relative_altitude, yaw, pitch, roll\n')
    for file in fnames:
        print(file)    
        with Image.open(file) as im:
            dji = get_xmp_dji(im)
            gps = get_exif_gps(im)
            fout.write('{}, {:.7f}, {:.7f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}\n'.format(
                 os.path.abspath(file), gps['lat'], gps['lon'], gps['alt'], 
                 dji['rel_alt']+input_args.elevation, dji['yaw'], dji['pitch'], 
                 dji['roll']))

