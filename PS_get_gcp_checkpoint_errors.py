# Script for finding the error at each GCP in a PhotoScan model.
# This script enables all the markers, then turns off one at a time

import PhotoScan

# get the current file name minus the .psx part
fName = PhotoScan.app.document.path
fName = fName[:len(fName) - 4]

# open a text file to save the errors
outfile = open('{}{}'.format(fName, '_ERRORS.txt'), 'w')
outfile.write('PhotoScan file: {}\n\n'.format(fName))

print('\nrunning:\n    PS_get_gcp_checkpoint_errors.py\n')


def getOptimizeParams(chunk):
    # TODO: trying getting params here instead:
    #            PhotoScan.app.document.chunk.meta['optimize/fit_flags']
    paramList = ['f',
                 'cx',
                 'cy',
                 'b1',
                 'b2',
                 'k1',
                 'k2',
                 'k3',
                 'k4',
                 'p1',
                 'p2',
                 'p3',
                 'p4']  # this is missing 'fit_shutter' 
    paramDict = {}
    for ii, param in enumerate(paramList):
        tf = not(getattr(chunk.sensors[0].calibration,param)==0)
        paramDict['fit_{}'.format(param)] = tf
    paramDict['fit_shutter'] = False
    return paramDict


for chunk in PhotoScan.app.document.chunks:

    print('Processing chunk: {}'.format(chunk.label))
#     print('Enabling all markers')
    outfile.write('chunk = {}\n'.format(chunk.label))

#     marker_list = []
#     # check which markers are enabled
#     for marker in chunk.markers:
#         marker_list.append(marker.reference.enabled)

    errorList = []
    errorList2 = []
    markerList = []
    for marker in chunk.markers:
        if marker.reference.enabled and marker.projections.values():
            print('processing marker:', marker.label)
           #  print(['marker.position',marker.position])
#             print(['marker.projections.items()',marker.projections.items()])
#             print(['marker.projections.values()',marker.projections.values()])
            markerList.append(marker.label)
            # turn off the marker to find the error
            marker.reference.enabled = False
            # print(['marker.position',marker.position])
#             print(['marker.projections.items()',marker.projections.items()])
#             print(['marker.projections.values()',marker.projections.values()])
            # re-optimize the cameras without the marker
            # TODO: figure out how to use the last users selected parameters in 
            #       Optimize cameras
            # This guesses the current optimize params from the adjusted calibration,
            # but doens't include the rolling shutter (set to False)
            optimizeParamsDict = getOptimizeParams(chunk)
            chunk.optimizeCameras(**optimizeParamsDict)
            #     fit_f=True,
#                 fit_cxcy=True,
#                 fit_b1=True,
#                 fit_b2=True,
#                 fit_k1k2k3=True,
#                 fit_p1p2=True,
#                 fit_k4=True,
#                 fit_p3=False,
#                 fit_p4=False)
            # get the error
            # measured values in geocentric coordinates
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
            outfile.write(
                '   marker {}:  error = {}\n'.format(marker.label, error.norm()))
            outfile.flush()
        elif marker.reference.enabled and not marker.projections.values():
            print('Marker {} not processed, no projections'.format(marker.label))

    suma = sum(errorList2)
    n = len(errorList)
    rmsError = (suma / n)**0.5

    # write the RMS error
    outfile.write('\n   RMS = {}\n\n\n'.format(rmsError))
    outfile.flush()

    # re-optimize the cameras with all markers enabled
    chunk.optimizeCameras(**optimizeParamsDict)  
#         fit_f=True,
#         fit_cxcy=True,
#         fit_b1=True,
#         fit_b2=True,
#         fit_k1k2k3=True,
#         fit_p1p2=True,
#         fit_k4=True,
#         fit_p3=False,
#         fit_p4=False)
    print('\n')
    
    # write the errors to the console
    print('\nErrors for chunk {}:'.format(chunk.label))
    for ii, nm in enumerate(markerList):
        print('marker {}:  error = {}'.format(nm, errorList[ii]))
    print('\n total rms error in chunk {} = {}\n'.format(chunk.label, rmsError))

outfile.close()




print('Errors written to file: {}{}'.format(fName, '_ERRORS.txt'))

# str(sys.argv)
