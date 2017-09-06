# Script for finding the error at each GCP in a PhotoScan model.
# This script only runs inside Agisoft PhotoScan Pro.
# This script iterates through all enabled markers (with valid coordinates), 
# turning off one at a time, optimizing the cameras, and checking the errors.
# The errors are written to a text file in the same directory as the .psx file.

import PhotoScan

# get the current file name minus the .psx part
fName = PhotoScan.app.document.path
fName = fName[:len(fName) - 4]

# open a text file to save the errors
outfile = open('{}{}'.format(fName, '_ERRORS.txt'), 'w')
outfile.write('PhotoScan file: {}\n\n'.format(fName))

print('\nrunning:\n    PS_get_gcp_checkpoint_errors.py\n')


def getOptimizeParams(chunk):
    # get enabled optimizeCamera parameters from chunk.meta
    paramList = [
        'f', 'cx', 'cy', 'b1', 'b2', 'k1', 'k2', 'k3', 'k4', 'p1', 'p2', 'p3',
        'p4', 'shutter'
    ]

    enabledList = chunk.meta['optimize/fit_flags']
    enabledList2 = enabledList.split()

    paramDict = {}
    for param in paramList:
        if param in enabledList2:
            paramDict['fit_{}'.format(param)] = True
        else:
            paramDict['fit_{}'.format(param)] = False
    return paramDict


for chunk in PhotoScan.app.document.chunks:

    print('Processing chunk: {}'.format(chunk.label))
    outfile.write('chunk = {}\n'.format(chunk.label))

    # get the last optimizeCameras parameters used
    optimizeParamsDict = getOptimizeParams(chunk)

    errorList = []
    errorList2 = []
    markerList = []
    for marker in chunk.markers:
        if marker.reference.enabled and marker.projections.values():
            print('processing marker:', marker.label)
            markerList.append(marker.label)
            # turn off the marker to find the error
            marker.reference.enabled = False
            # re-optimize the cameras without the marker
            chunk.optimizeCameras(**optimizeParamsDict)
            # measured marker locations in geocentric coordinates
            source = chunk.crs.unproject(marker.reference.location)
            # estimated coordinates in geocentric coordinates
            estim = chunk.transform.matrix.mulp(marker.position)
            local = chunk.crs.localframe(
                chunk.transform.matrix.mulp(
                    marker.position))  # local LSE coordinates
            error = local.mulv(estim - source)  # error at the GCP marker
            errorList.append(error.norm())  # list of errors
            errorList2.append(error.norm()**2)  # list of squared errors
            # turn the marker back on
            marker.reference.enabled = True
            outfile.write('   marker {}:  error = {}\n'.format(
                marker.label, error.norm()))
            outfile.flush()
        elif marker.reference.enabled and not marker.projections.values():
            print(
                'Marker {} not processed, no projections'.format(marker.label))

    suma = sum(errorList2)
    n = len(errorList)
    rmsError = (suma / n)**0.5

    # write the RMS error
    outfile.write('\n   RMS = {}\n\n\n'.format(rmsError))
    outfile.flush()

    # re-optimize the cameras with all markers enabled
    chunk.optimizeCameras(**optimizeParamsDict)

    # write the errors to the console
    print('\n')
    print('\nErrors for chunk {}:'.format(chunk.label))
    for ii, nm in enumerate(markerList):
        print('marker {}:  error = {}'.format(nm, errorList[ii]))
    print(
        '\n total rms error in chunk {} = {}\n'.format(chunk.label, rmsError))

outfile.close()
print('Errors written to file: {}{}'.format(fName, '_ERRORS.txt'))
