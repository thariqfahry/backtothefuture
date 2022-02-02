# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 00:23:36 2022

@author: Thariq
"""

import os, itk, numpy as np, cv2 as cv

def find(path, substring):
    results = []
    for root, directories, files in os.walk(path):
        for filename in files:
            if substring in filename:
                results.append(os.path.join(root, filename))
        
    return results


def get_list_of_image_dimensions(paths):
    
    dims = []
    

    for path in paths:
        print('Reading ',path)
        
        imageio = itk.ScancoImageIO.New()
        image = itk.imread(path, imageio = imageio)
        
        dim = image.shape
        dims.append((path,dim))
        
        print('dimension = ',dim)
        
        del imageio
        del image
        
    return dims

def get_middle_slice(volume):
    middle_index = volume.shape[-1]//2
    return volume[:,:,middle_index]


def beautify_and_resize(image, resize_factor):
    '''
    Takes a 2-D array of raw CT absorption values and (roughly) squashes them 
    into the (0,255) renderable grayscale range.
    '''
    
    #map raw CT absorption values to (0,255) grayscale pixel values
    image = 255*((image + 2048)/10000)
    
    #make sure pixel values are integers as OpenCV expects an int in the range (0,255) for the grayscale colorspace
    image = image.astype(np.uint8)
    
    #resize image by a decimal resize_factor
    image = cv.resize(image, None, fx=resize_factor,fy=resize_factor)
    
    #Returns an OpenCV-renderable Numpy array.
    return image