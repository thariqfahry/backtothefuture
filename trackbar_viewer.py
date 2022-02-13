import itk, numpy as np, cv2 as cv, sys, math, os
import matplotlib.pyplot as plt
import bttf_utilities as bu
from bttf_constants import text_params
from plotting import get_line as gl, stitch
from pathlookup import pathlookup


def on_trackbar(val, image3d, gap_width, plot, isq_path):
    
    axis = 0
    ctslice = image3d[...,val]
    
    image = bu.beautify_and_resize(ctslice, 1)
    min_pixel = image.min()
    max_pixel = image.max()
    
    image = stitch(image, plot)

    image = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    
    cv.putText(img = image, text = f'min:{min_pixel}, max:{max_pixel}, gap width: {gap_width if "gap_width" in globals() else ""}', **text_params)
    cv.imshow(isq_path , image)
    

def viewct(search_string):
    if os.path.exists(search_string):
        isq_path = search_string
    else:
        isq_path = pathlookup[search_string]
    
    #isq_path = bu.find('H:\\High Cycle' , 'D0004122.ISQ;1')[0]
    #isq_path = r"H:\High Cycle\CT Scans\1 ml Treated\T033_D1\Treated\D0004166.ISQ;1"
    #isq_path = r'C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\D0004114.ISQ;1'
    #isq_path = r'H:\High Cycle\CT Scans\0.3 ml Treated\T032_D2\Treated\00002368\00004098\D0004139.ISQ;1'
    #isq_path = "H:/High Cycle/" + "CT Scans_12G_T045_D2_1x12G_D0004283.ISQ;1.png".replace("_","/")[:-4]
    
    print('reading from disk...')
    imageio = itk.ScancoImageIO.New()
    
    if "image3d" in globals():
        del image3d; print("Deleted image3d")
        
    image3d = (itk.imread(isq_path, imageio=imageio))
    
    print('looking for gap...')
    gap_width = 0
    
    plot = gl(bu.get_max_per_slice(image3d))
    image3d, gap_width = bu.highlight_gap(image3d, tolerate_upto = 1.3)
    
    cv.namedWindow(isq_path)
    #FIXME the value of the trackbar's max is always 1024, which is too many when slicing perpendicular to bone
    cv.createTrackbar('Slice', isq_path, 0, image3d.shape[-1]-1, lambda val: on_trackbar(val, image3d, gap_width, plot, isq_path))
    k = cv.waitKey(0)
    cv.destroyAllWindows()

viewct("CT Scans_1 ml Treated_T032_D3_Degen_D0004149.ISQ;1.png")