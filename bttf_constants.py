# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 02:11:50 2022

@author: Thariq
"""
import cv2 as cv

bottomLeftCornerOfText = (10,220)

text_params = {
"fontFace"               : cv.FONT_HERSHEY_SIMPLEX,
"org"                    : bottomLeftCornerOfText,
"fontScale"              : 0.5,
"color"                  : (255,255,255),
"thickness"              : 1,
"lineType"               : 2
}