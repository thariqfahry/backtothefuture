from matplotlib import pyplot as plt
import cv2 as cv, numpy as np
import bttf_utilities as bu
from bttf_utilities import beautify_and_resize as br
import pdb

text_parame = {
"fontFace"               : cv.FONT_HERSHEY_SIMPLEX,
#"org"                    : (10,220),
"fontScale"              : 0.5,
"color"                  : (0,255,0),
"thickness"              : 1,
"lineType"               : 2
}

def add_validation_scale(image):
    #image2 = br(image, 1)
    
    image3 = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    #pdb.set_trace()
    image4 = cv.line(image3,(512,0), (512,image3.shape[0]), (0,255,0), 1)
    
    for row in range(image4.shape[0]-1):
        if not row % 10:
            image4 = cv.line(image4,(510,row), (514,row), (0,255,0), 1)
            
        if not row % 20:
            image4 = cv.line(image4,(508,row), (516,row), (0,255,0), 1)
            cv.putText(img = image4, text = f'{row}', **text_parame, org=(518, row+5))
    
    return image4
    
    #plt.imshow(image4)
    #cv.imshow('',image4);cv.waitKey(0);cv.destroyAllWindows()
    
    