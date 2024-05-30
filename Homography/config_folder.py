"""
Created on Mon Nov 13 8:47:59 2023

@author: tmayer
"""
# Base -> used as a reference for the homographic transformation on the other image
BASE_FOLDER = 'dect1_0'
BASE_IMG_COORDS = 'coords_img1.txt'

# Modify -> image to be modified to match the base image reference points (homographic transformation)
MODIFY_FOLDER = 'dec1_90'
MODIFY_IMG_COORDS = 'coords_img2.txt'

OUTPUT_FOLDER = "result"
OUTPUT_FORMAT = ".tiff"

#True if you want to keep 0 value inside the image (black pixels). If False, 0 value (black pixels) will mean that
BLACK_PIXEL = False