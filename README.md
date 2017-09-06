# PhotoScan_Scripts
handy scripts for SfM processing in Agisoft PhotoScan Pro

##PS_get_gcp_checkpoint_errors.py: 
calculates the total rms error and the error at each enabled ground control point
(gcp) by disabling each gcp, one at a time, re-optimizing the cameras, and finding the
model-to-world error. The script uses the last optimizeCameras parameters specified
by the user, which means you'll need to run optimizeCameras at least once before you 
run this script (you should really be running this when you're finished with your 
model).

