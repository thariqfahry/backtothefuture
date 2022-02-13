from functools import lru_cache
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

def get_middle_of_innermost_index(image3d):
    middle_index = image3d.shape[-1]//2
    return middle_index
    

def beautify_and_resize(image, resize_factor):
    '''
    Takes a 2-D array of raw CT absorption values and (roughly) squashes them 
    into the (0,255) renderable grayscale range.
    '''
    
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
    
    #Compute the grayscale value of the brightest pixel in each slice of the 3-D CT image.
    maxarr = (255*((np.amax(image3d, (1,2)) + 2048)/10000)).astype(np.uint8)
    #maxarr = np.array([beautify_and_resize(s, 1).max() for s in image3d]).view(HashableNDArray)
    
    get_max_per_slice.cache[hash(image3d)] = maxarr
    
    return maxarr

get_max_per_slice.cache = {}

#Saturate the first and last Xth of slices of an array.
def drop_firstlast(array, X):
    
    array = array.copy()
    num_slices = array.shape[0]
    
    array[:num_slices//X] = 255
    array[num_slices - num_slices//X:] = 255
    
    return array

    
def get_most_likely_gap_slice_index(image3d):
    '''
    Gets the slice containing the minimax pixel in the entire 3-D CT image, ignoring
    the first and last 20% of slices in the image along the zeroth axis.
    '''
    
    maximums = get_max_per_slice(image3d)
    
    #Drop the first and last 20% of slices since we assume the gap won't be in
    #any slices in that range, and they might contain pixels dimmer than the 'gap'.
    maximums = drop_firstlast(maximums, 5)
    
    minimax_pixel_brightness = maximums.min()
    
    return np.where(maximums == minimax_pixel_brightness)[0][0]
    

def get_all_gap_slice_indices(image3d, tolerate_upto = 2):
    maximums = get_max_per_slice(image3d)
    
    #Drop first and last 20% of slices.
    maximums = drop_firstlast(maximums, 5)
    
    #Get value of dimmest pixel in that remaining range: this is likely to fall somewhere in the gap.
    minimax_pixel_brightness = maximums.min()
    
    
    #Return the indices of slices whose dimmest pixel's brightness is within tolerate_upto% 
    #of that of the global dimmest pixel. These slices likely span the entire gap.
    return np.where(maximums < minimax_pixel_brightness*tolerate_upto)[0]

def highlight_gap(image3d, tolerate_upto = 2):
    gap_indices = get_all_gap_slice_indices(image3d, tolerate_upto)
    
    #print('gap indices were ', gap_indices)
    #print('gap width: ', len(gap_indices))
    
    image3d[gap_indices] = image3d[gap_indices] + 2000
    return image3d, len(gap_indices)

def get_index_of_horizontal_slice_containing_minimax_pixel(image3d):
    
    axial_gap_slice = beautify_and_resize(image3d[get_most_likely_gap_slice_index(image3d)], 1)
    
    maximums = get_max_per_slice(image3d)
    maximums = drop_firstlast(maximums, 5)
    minimax_pixel_brightness = maximums.min()
    
    poss = np.where(axial_gap_slice == minimax_pixel_brightness)
    
    print('Poss: ', poss, 'Indexed: ', poss[-1][-1])
    
    return poss

    
    




















