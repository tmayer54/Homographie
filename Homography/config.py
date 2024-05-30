"""
Created on Mon Nov 13 8:47:59 2023

@author: tmayer
"""
# Base -> used as a reference for the homographic transformation on the other image
BASE_PATH = 'Data/1'
BASE_IMG_EXT = '.tif'
BASE_IMG_COORDS = 'points_image1.txt'

# Modify -> image to be modified to match the base image reference points (homographic transformation)
MODIFY_PATH = 'Data/10'
MODIFY_IMG_EXT = '.tif'
MODIFY_IMG_COORDS = 'points_image2.txt'

OUTPUT_NAME = "data12-t"
OUTPUT_FORMAT = ".tif"

OUTPUT_FOLDER = "homographie"

#True if you want to keep 0 value inside the image (black pixels). If False, 0 value (black pixels) will mean that
BLACK_PIXEL = False