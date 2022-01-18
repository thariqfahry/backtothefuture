"""
10TH JAN: DRAWS LINE BETWEEN TWO LARGEST Canny CONTOURS
USE 3-D DATA FOR BETTER LINE
COMPARE WITH FORCE DATA
"""

import itk, numpy as np, cv2 as cv, sys, math
import matplotlib.pyplot as plt

imageio = itk.ScancoImageIO.New()
image = itk.imread(r'C:\Users\Thariq_\OneDrive - University of Leeds\Elec\MECH5030M Team Project\D0004114.ISQ;1', imageio=imageio)
xray = cv.imread(r'C:\Users\Thariq_\Desktop\hand-x-ray.jpg')

#%%
title = 'ct'
image_arr = np.asarray(image)

def on_trackbar(val):
    ctslice = image_arr[val]
    z = 255*((ctslice + 2048)/10000)
    z = z.astype(np.uint8)
    z = cv.resize(z, None, fx=0.6,fy=0.6)
    
    thresh1 = cv.Canny(z, 150, 150)
    #source image, contour retrieval mode, contour approximation method
    contours, hierarchy = cv.findContours(thresh1, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    contours.sort(key = cv.contourArea, reverse=True)
    
    bg = cv.cvtColor(z, cv.COLOR_GRAY2BGR)
    drawn = cv.drawContours(bg, contours[0:10], -1, (255,255,0), 1)
    
    if len(contours) > 2:
        (x,y), radius = cv.minEnclosingCircle(contours[0])
        (x2,y2), radius2 = cv.minEnclosingCircle(contours[1])
        center = (int(x),int(y))
        center2 = (int(x2),int(y2))

        length = int(math.sqrt(abs((y2-y)+(x2-x))))

        cv.line(drawn, center, center2, (0, 255, 0), 1)
        
        font                   = cv.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10,220)
        fontScale              = 1
        fontColor              = (255,255,255)
        thickness              = 1
        lineType               = 2
        
        cv.putText(drawn,str(length), 
            bottomLeftCornerOfText, 
            font, 
            fontScale,
            fontColor,
            thickness,
            lineType)
        
        cv.imshow(title, drawn)

cv.namedWindow(title)
cv.createTrackbar('Slice', title, 0, image.shape[0]-1, on_trackbar)

on_trackbar(0)


k = cv.waitKey(0)
cv.destroyAllWindows()

#plt.imshow(np.asarray(image)[0])


