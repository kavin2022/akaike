# import the necessary packages
from __future__ import print_function
from skimage.feature import peak_local_max
try:
    from skimage.segmentation import watershed
except:
    from skimage.segmentation import watershed
from scipy import ndimage
import argparse
import imutils
import cv2
from scipy import ndimage
import numpy as np
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

def show_image(path,x=30,y=7):
    img = cv2.imread(path)
    plt.figure(figsize=(x,y))
    plt.imshow(img)
    
def contour_method(input_file_path,output_file_path,result_info = False,result_print =False ):
    
    # loading the image
    image = cv2.imread(input_file_path)
    shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)
    
 
    # grayscaling
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    # thresholding - to get binary image
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # noise removal
    kernel = np.ones((3,3),np.uint8)
    noise_removed = cv2.morphologyEx(thresh,cv2.MORPH_OPEN, kernel, iterations=2)
    
    cnts = cv2.findContours(noise_removed.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours,h = cnts
    cnts = imutils.grab_contours(cnts)
    
    # loop over the contours
    for (i, c) in enumerate(cnts):
    # draw the contour
        ((x, y), _) = cv2.minEnclosingCircle(c)
        cv2.putText(image, "#{}".format(i + 1), (int(x) - 10, int(y)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    
    # store the output image
    cv2.imwrite(output_file_path,image)
    
    total_g = []
    area_broken_g = []
    for x in contours:
        area = cv2.contourArea(x)
        total_g.append(area)
#         if area<1150:
#             area_broken_g.append(area)
    area_avg = np.average(total_g)
    
    result = {'total':len(total_g),'area_avg':area_avg,'area_median': np.quantile(total_g,.50),'method' :'contour','area':total_g}
    if result_print == True:
        print(f"data : {input_file_path}")
        print(f"method : contour")
        show_image(input_file_path)
        print('output_file')
        show_image(output_file_path)
        print(f"Total rice count : {(len(total_g))}")
        print("============================================================================================")
    
    if result_info == True:
        return result
    
def watershed_method(input_file_path,output_file_path,result_info = False,result_print =False):
    # loading image
    image = cv2.imread(input_file_path)
    shifted = cv2.pyrMeanShiftFiltering(image, 21, 51)
    
    # thersholding and greyscaling
    gray = cv2.cvtColor(shifted, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    
    # noise_removal
    kernel = np.ones((3,3),np.uint8)
    noise_removed = cv2.morphologyEx(thresh,cv2.MORPH_OPEN, kernel, iterations=2)
    
    # compute the exact Euclidean distance from every binary
    # pixel to the nearest zero pixel, then find peaks in this
    # distance map
    D = ndimage.distance_transform_edt(noise_removed)
    localMax = peak_local_max(D,indices=False, min_distance=20,labels=thresh)

    # perform a connected component analysis on the local peaks,
    # using 8-connectivity, then appy the Watershed algorithm
    markers = ndimage.label(localMax, structure=np.ones((3, 3)))[0]
    labels = watershed(-D, markers, mask=thresh)
    
    total_g = []
    area_broken_g = []
    for label in np.unique(labels):
    # if the label is zero, we are examining the 'background'
    # so simply ignore it
        if label == 0:
            continue
        # otherwise, allocate memory for the label region and draw
        # it on the mask
        mask = np.zeros(gray.shape, dtype="uint8")
        mask[labels == label] = 255

        #detect contours in the mask and grab the largest one
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        
        contours,h = cnts
        cnts = imutils.grab_contours(cnts)
        c = max(cnts, key=cv2.contourArea)
        
        # to draw contour or boundaries
        cv2.drawContours(image,contours,-1,(0, 255, 0),2)

        
        # to write the label for each rice grain
        ((x, y), r) = cv2.minEnclosingCircle(c)
        cv2.putText(image, "#{}".format(label), (int(x) - 10, int(y)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0,255),2)
        
        # using threshold to calculate area
#         area_threshold = 1497
        for x in contours:
            area = cv2.contourArea(x)
            total_g.append(area)
#             if area<=area_threshold:
#                 area_broken_g.append(area)
    
    cv2.imwrite(output_file_path,image)
    
    area_avg = np.average(total_g)
    result = {'total':len(total_g),
             'area' : total_g,
             'method' :'watershed',
              'area_median': np.quantile(total_g,.50),
             'area_avg': area_avg}
    
    if result_print == True:
        print(f"data : {input_file_path}")
        print(f"method : water shed")
        show_image(input_file_path)
        print('output_file')
        show_image(output_file_path)
        print(f"Total rice count : {(len(total_g))}")
        print("============================================================================================")
    
    if result_info == True:
        return result
        
        
    

    
    