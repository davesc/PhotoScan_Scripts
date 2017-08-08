# Script for finding the error at each GCP in a PhotoScan model.
# This script enables all the markers, then turns off one at a time

import PhotoScan


# get the current file name minus the .psx part
fName =  PhotoScan.app.document.path
fName = fName[:len(fName)-4]

# open a text file to save the errors
outfile = open('{}{}'.format(fName,'_ERRORS.txt'),'w')
outfile.write('PhotoScan file: {}\n\n'.format(fName))

print('\nrunning:\n    PS_get_gcp_checkpoint_errors.py\n')

for chunk in PhotoScan.app.document.chunks:

	print('Processing chunk: {}'.format(chunk.label))
	print('Enabling all markers')
	outfile.write('chunk = {}\n'.format(chunk.label))
	
	# enable all the markers
	for marker in chunk.markers:
		marker.reference.enabled = True

	errorList = []
	errorList2 = []
	markerList = []
	for marker in chunk.markers:
		print('processing marker:',marker.label)
		markerList.append(marker.label)
		# turn off the marker to find the error
		marker.reference.enabled = False
		# re-optimize the cameras without the marker
		chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_b1=True, fit_b2=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True, fit_p3=False, fit_p4=False)
		# get the error
		source = chunk.crs.unproject(marker.reference.location) #measured values in geocentric coordinates
		estim = chunk.transform.matrix.mulp(marker.position) #estimated coordinates in geocentric coordinates
		local = chunk.crs.localframe(chunk.transform.matrix.mulp(marker.position)) #local LSE coordinates
		error = local.mulv(estim - source) # error at the GCP marker
		errorList.append(error.norm()) #list of errors
		errorList2.append(error.norm() ** 2) #list of squared errors
		# turn the marker back on
		marker.reference.enabled = True
		outfile.write('   marker {}:  error = {}\n'.format(marker.label,error.norm()))
		outfile.flush()


	suma = sum(errorList2)
	n = len(errorList)
	rmsError = (suma / n) ** 0.5

	# write the errors to the console
	for ii, nm in enumerate(markerList):
		print('marker {}:  error = {}'.format(marker.label,errorList[ii]))
	
	# write the RMS error	
	print('total rms error in chunk {} = {}\n'.format(chunk.label,rmsError))
	outfile.write('\n   RMS = {}\n\n\n'.format(rmsError))
	outfile.flush()
	

	# re-optimize the cameras with all markers enabled
	chunk.optimizeCameras(fit_f=True, fit_cxcy=True, fit_b1=True, fit_b2=True, fit_k1k2k3=True, fit_p1p2=True, fit_k4=True, fit_p3=False, fit_p4=False)
	print('\n')
		
outfile.close()



print('Errors written to file: {}{}'.format(fName,'_ERRORS.txt'))


# str(sys.argv)