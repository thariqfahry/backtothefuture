import itk, numpy as np, cv2 as cv, sys, math, os, pandas as pd
import matplotlib.pyplot as plt
import bttf_utilities as bu
from bttf_constants import text_params
from plotting import get_line, stitch

from total_size import total_size as ts

# Write the middle slice of all ISQs to a folder after highlighting gap slices
imageio = itk.ScancoImageIO.New()

output_data = []

for substudy in ['High Cycle','Injection','Needle Puncture']:
    root = 'H:\\' +substudy
    output_path = r'C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\backtothefuture\separation_highlighted'
    
    image_list = bu.find(root , '.ISQ')

    for index, path in enumerate(image_list):
        
        #Free up memory
        if "image3d" in globals():
            del image3d; print("Deleted image3d")     

        print('reading',index,'/',len(image_list)-1,path)
        
        #Explicitly turn the weird array returned by imread into a Numpy array, so it actually responds to deletion
        image3d = np.asarray(itk.imread(path, imageio=imageio)).view(bu.HashableNDArray)

        #Get middle slice (when looking along side axis), render to grayscale, and add text to image
        preview_slice = bu.get_middle_of_innermost_index(image3d)
        #preview_slice = bu.get_index_of_horizontal_slice_containing_minimax_pixel(image3d)[-1][-1]
        
        #Get max-per-slice profile
        mps = bu.get_max_per_slice(image3d)
        maxpixelplot = get_line(mps)
        
        #Highlight gap pixels
        tolerance = 1.3
        image3d, gap_width = bu.highlight_gap(image3d, tolerate_upto = 1.3)
        
        #Render preview slice
        preview_slice = bu.beautify_and_resize(image3d[...,preview_slice], 1)
        
        #Add text to preview slice.
        cv.putText(img = preview_slice, text = f'gap width: {gap_width}', **text_params)
        
        #Add MPS graph to preview slice.
        preview_slice = stitch(preview_slice, maxpixelplot)
        
        #Save image, using its file path in the HDD to construct its filename
        filename = path[len(root)+1:].replace('\\','_') + '.png'
        image_write_path = os.path.join(os.path.join(output_path, substudy), filename)
        cv.imwrite(image_write_path, preview_slice)
        
        output_data.append({"study":substudy,"sample":filename,"path":path,"gap":gap_width,"tolerance":tolerance,"maxperslice":""})
        
        bu.get_max_per_slice.cache = {}
        

#Construct a dataframe with the output data and write it to a CSV.
df = pd.DataFrame(output_data)
df.to_csv('output_data.csv', index = False)

pass