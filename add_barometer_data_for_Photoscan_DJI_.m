
% This script searches recursively for DJI jpegs and outputs a file with 
% GPS lat lon, barometer altitude, and GPS altitude.

% REQUIRES:
% rdir.m   (https://www.mathworks.com/matlabcentral/fileexchange/32226)
% exiftool (https://www.sno.phy.queensu.ca/~phil/exiftool/)
%          (or 'brew install exiftool' on OSX with homebrew)

% In older firmware the DJI Phantom 3 recorded the barometer altitude as
% the GPS altitide.  The new firmware
% records the actual GPS altitude, which is terrible, along with the
% barometer altitude labeled "RelativeAltitude".  The barometer altitude is
% relative to where you take off, so you might need to add an offset. 

% open a file to write lat lon data from each image EXIF, and add a
% new altitude (so PhotoScan will read it)

% output path / file name
outfile  = 'put_your_output_filename_here.txt';

% path to base directory for images, will be searched recursively 
% for DJI jpegs
baseDir = 'put_your_image_directory_here/';

% recursive search for DJI images
fpaths = rdir('/Volumes/Data2/Sandwich_Imagery/**/DJI*.JPG');

% open the write file
fid  = fopen(outfile,'w+');
% add a header line
fprintf(fid,'# file -GPSLatitude -GPSLongitude -RelativeAltitude -GPSAltitude -GimbalYawDegree -GimbalPitchDegree -GimbalRollDegree\n');

% variables to store data
lat = zeros(length(fpaths),1);
lon = zeros(length(fpaths),1);
gpsAlt = zeros(length(fpaths),1);
barAlt = zeros(length(fpaths),1);

disp(sprintf('processing %g DJI jpeg files',length(fpaths)))

for ii = 1:length(fpaths);
    % get the EXIF data using exiftool
    exif = evalc(sprintf('!exiftool -n -T %s -args -GPSLatitude -GPSLongitude -RelativeAltitude -GPSAltitude -GimbalYawDegree -GimbalPitchDegree -GimbalRollDegree',fpaths(ii).name));
    exif2 = sscanf(exif,'%f %f %f %f %f %f %f',[1,7]);
    lat(ii) = exif2(1);
    lon(ii) = exif2(2);
    gpsAlt(ii) = exif2(4);
    barAlt(ii) = exif2(3);
    
    exif2(6) = exif2(6)+90; % convert from DJI to Photoscan reference frame
    
    % write the EXIF data to the file
    fprintf(fid,'%s %.08f %.08f %.02f %.02f %.02f %.02f %.02f\n',fpaths(ii).name,exif2);
    disp(sprintf('%s %.08f %.08f %.02f %.02f %.02f %.02f %.02f\n',fpaths(ii).name,exif2))
end

mGpsAlt = mean(gpsAlt);
mBarAlt = mean(barAlt);

disp(sprintf('mean GPS alt = %3.1f m,  mean barometer alt = %3.1f',mGpsAlt,mBarAlt))


            
fclose(fid);



