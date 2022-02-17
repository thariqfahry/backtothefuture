from functools import lru_cache
import os, itk, numpy as np, cv2 as cv


def find(path, substring):
    results = []
    for root, directories, files in os.walk(path):
        for filename in files:
            if substring in filename:
                results.append(os.path.join(root, filename))
        
    return results


def get_middle_of_innermost_index(image3d):
    middle_index = image3d.shape[-1]//2
    return middle_index
    

#Takes a 2-D array of raw CT absorption values and (roughly) squashes them into the (0,255) renderable grayscale range.
def beautify_and_resize(image, resize_factor):  
    #map raw CT absorption values to (0,255) grayscale pixel values
    image = 255*((image.copy() + 2048)/10000)
    
    #make sure pixel values are integers as OpenCV expects an int in the range (0,255) for the grayscale colorspace
    image = image.astype(np.uint8)
    
    #resize image by a decimal resize_factor
    image = cv.resize(image, None, fx=resize_factor,fy=resize_factor)
    
    #Returns an OpenCV-renderable Numpy array.
    return image


# TODO does it matter that this is a mutable object being hashed?
class HashableNDArray(np.ndarray):
    def __hash__(self):
        return hash(self.tobytes())
    

def get_max_per_slice(image3d):
    
    if hash(image3d) in get_max_per_slice.cache:
        return get_max_per_slice.cache[hash(image3d)]
    
    #Get value of brightest pixel in each slice: amax along axes (1,2).
    maxarr = np.amax(image3d,(1,2))
    
    #Update cache dictionary with {hash:result}.
    get_max_per_slice.cache[hash(image3d)] = maxarr
    
    return maxarr

get_max_per_slice.cache = {}


#Ignore the first and last 1/Xth of slices of an array.
def drop_firstlast(array, X, replacewith = False):
    
    array = array.copy()
    num_slices = array.shape[0]
    
    #Set the first and last 1/Xth elements to replacewith.
    array[:num_slices//X] = replacewith 
    array[num_slices - num_slices//X:] = replacewith
    
    return array


#tolerate_upto = the minimum number of standard deviations to qualify as a gap slice
def get_all_gap_slice_indices(image3d, tolerate_upto = 1):
    maximums = get_max_per_slice(image3d)
    
    #Determine which slice maximums lie below tolerate_upto standard deviations
    mask = maximums < (maximums.mean() - tolerate_upto*maximums.std())
    
    #Ignore the first and last 25% of slices.
    mask = drop_firstlast(mask, 4)
    
    #Convert a True/False mask into a list of indices.
    gap_slices = np.where(mask)[0]
    
    #Check if the array is empty, because we are about to index it. 
    if len(gap_slices) < 1:
        return np.array([], dtype = np.int16)
    
    #Within the middle 50%, assume the gap is contiguous. If not, it will be later marked as invalid for being too large.
    contiguous_gap_slices = np.arange(gap_slices[0], gap_slices[-1]+1)
    
    return contiguous_gap_slices
    

def contains_valid_gap(image3d, tolerate_upto = 1):    
    mps = get_max_per_slice(image3d)
    contiguous_gap_slices = get_all_gap_slice_indices(image3d, tolerate_upto)
                                                      
    #Is gap smaller than 40% the of the number of slices? Likely to be invalid otherwise.
    is_gap_not_too_big =  True if len(contiguous_gap_slices) < 0.4*image3d.shape[0] else False
    
    #Is gapp mean at least 30% less than global mean? Likely to be invalid otherwise.
    is_gap_average_sufficiently_deviant = bool((mps.mean() - mps[contiguous_gap_slices].mean()) / mps.mean() > 0.3)
    
    return is_gap_not_too_big and is_gap_average_sufficiently_deviant and len(contiguous_gap_slices) > 0


#Add 2000 to the raw CT intensity of the suspected gap slices.
def highlight_gap(image3d, tolerate_upto = 2):
    gap_indices = get_all_gap_slice_indices(image3d, tolerate_upto)
    
    #print('gap indices were ', gap_indices)
    #print('gap width: ', len(gap_indices))
    
    image3d[gap_indices] = image3d[gap_indices] + 2000
    return image3d, len(gap_indices)


def get_area_of_biggest_contour(ctslice, blur = 15):
    
    #Apply a simple kernel blur to the image.
    x = cv.blur(ctslice.copy(), (blur, blur))
    
    #Make values less than 3000 'blank', and values more than 3000 'bone'. The image is then effectively binary.
    x[x<3000] = -1000
    x[x>3000] = 5000
    
    #Apply Canny edge detection to the image, after rendering it.
    canny = cv.Canny(beautify_and_resize(x, 1), 150, 150)
    
    #Get contours and sort them by area in descending order.
    contours, hierarchy = cv.findContours(canny, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours.sort(key = cv.contourArea, reverse=True)
    
    if contours:
        biggest_contour = contours[0]
        (x,y), radius = cv.minEnclosingCircle(biggest_contour)
        
        area = cv.contourArea(biggest_contour)
        circularity = area / (3.1415*(radius**2))
        
        return area, circularity
    
    return 0, 0


def get_cont_area_profile(image3d, blur = 15):
    return [get_area_of_biggest_contour(ctslice, blur) for ctslice in image3d]

    
    




















