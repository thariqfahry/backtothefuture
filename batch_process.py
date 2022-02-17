import itk, numpy as np, cv2 as cv, sys, math, os, pandas as pd, plotly.express as px, time
import matplotlib.pyplot as plt
import bttf_utilities as bu
from bttf_constants import text_params

from plotting import get_line, stitch, pfa_generic, plot_two
from validation_scale import add_validation_scale

from total_size import total_size as ts

# Write the middle slice of all ISQs to a folder after highlighting gap slices
imageio = itk.ScancoImageIO.New()

#Get a list of PNGs from previous runs where validity = 1
df2 = pd.read_csv('output_data_validity_run.csv')
valid_pngs = df2[df2['validity'] == 1]['sample'].to_list()

#Initialise an empty output_data array
output_data = []

for substudy in ['High Cycle','Injection','Needle Puncture']:
    root = 'H:\\' +substudy
    output_path = r'C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\backtothefuture\separation_highlighted'
    
    #Get a list of all ISQ paths in H:
    image_list = bu.find(root , '.ISQ')
    time_measured = False

    for index, path in enumerate(image_list):
        
        #Only read the image if it is in the list of valid PNGs
        if not path[len(root)+1:].replace('\\','_') + '.png' in valid_pngs:
            continue
        
        #Free up memory
        if "image3d" in globals():
            del image3d; print("Deleted image3d")     
        
        print('reading',index,'/',len(image_list)-1,path)
        start = time.time()
        
        #Explicitly turn the object returned by imread into a Numpy array, so it actually responds to deletion
        image3d = np.asarray(itk.imread(path, imageio=imageio)).view(bu.HashableNDArray)

        #Get middle slice (when looking along side axis), render to grayscale, and add text to image
        preview_slice = bu.get_middle_of_innermost_index(image3d)
        #preview_slice = bu.get_index_of_horizontal_slice_containing_minimax_pixel(image3d)[-1][-1]
        
        #Get max-per-slice profile
        mps = np.array([])
        # mps = bu.get_max_per_slice(image3d)
        # maxpixelplot = get_line(mps)
        
        #Get contour profile and from it, get area at max circularity
        cap = bu.get_cont_area_profile(image3d, blur = 15)
        circ = [i[1] for i in cap]
        csa = cap[circ.index(max(circ))][0]
        
        #Plot and save contour profile
        # capplot = pfa_generic(plot_two(cap, title=path[len(root)+1:].replace('\\','_')))
        # filename = path[len(root)+1:].replace('\\','_') + '_CAP.png'
        # cap_write_path = os.path.join(output_path, substudy, filename)
        # cv.imwrite(cap_write_path, capplot)
        
        # #Check if image3d contains a valid gap.
        minimum_standard_deviations = 1
        validity = 1
        # validity = bu.contains_valid_gap(image3d, tolerate_upto=minimum_standard_deviations)
        
        # #Highlight gap pixels
        gap_width = 0
        # image3d_h, gap_width = bu.highlight_gap(image3d.copy(), tolerate_upto = minimum_standard_deviations)
        
        # #Render preview slice
        # preview_slice = bu.beautify_and_resize(image3d_h[...,preview_slice], 1)
        
        # #Add text to preview slice.
        # cv.putText(img = preview_slice, text = f'validity: {validity}  gap width: {gap_width}', **text_params)
        
        # #add scale to validate CT gap - preview_slice is RGB after this point
        # #preview_slice = add_validation_scale(preview_slice)
        
        # #Add MPS graph to preview slice.
        # preview_slice = stitch(preview_slice, maxpixelplot)
        
        #Save image, using its file path in the HDD to construct its filename
        filename = path[len(root)+1:].replace('\\','_') + '.png'
        # image_write_path = os.path.join(os.path.join(output_path, substudy), filename)
        # cv.imwrite(image_write_path, preview_slice)
        
        #Record extracted data.
        output_data.append({"study":substudy,"sample":filename, "path":path, "validity":int(validity),"gap":gap_width, "cross_section" : csa,
                            "tolerance":minimum_standard_deviations, "comment":"", "maxperslice":",".join(mps.astype(str))})
        
        # bu.get_max_per_slice.cache = {}
        
        end = time.time()
        if not time_measured:
            elapsed = end-start
            total = len(image_list) * elapsed
            print(f"Operation will take {total:.0f} seconds")
            time_measured = True

#Construct a dataframe with the output data and write it to a CSV.
df = pd.DataFrame(output_data)
df.to_csv('output_data_csa.csv', index = False)

pass