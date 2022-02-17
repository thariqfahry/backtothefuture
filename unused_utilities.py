#Currently unused.
def get_index_of_horizontal_slice_containing_minimax_pixel(image3d):
    
    axial_gap_slice = beautify_and_resize(image3d[get_most_likely_gap_slice_index(image3d)], 1)
    
    maximums = get_max_per_slice(image3d)
    maximums = drop_firstlast(maximums, 5)
    minimax_pixel_brightness = maximums.min()
    
    poss = np.where(axial_gap_slice == minimax_pixel_brightness)
    
    print('Poss: ', poss, 'Indexed: ', poss[-1][-1])
    
    return poss


#Currently unused, since gap_width is calculated via stddev.
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

