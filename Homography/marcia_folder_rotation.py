#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 7 10:17:51 2023

@author: tmayer
"""

import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image
from config_folder import BASE_FOLDER, BASE_IMG_COORDS, MODIFY_FOLDER, MODIFY_IMG_COORDS, OUTPUT_FOLDER, OUTPUT_FORMAT, BLACK_PIXEL

def image_difference(image1, image2):
	# Open the images
	img1 = Image.open(image1)
	img2 = Image.open(image2)

	# Ensure both images have the same size
	if img1.size != img2.size:
		raise ValueError("Input images must have the same dimensions")

	# Convert images to grayscale
	img1 = img1.convert('L') 	
	img2 = img2.convert('L')

	# Convert images to numpy arrays
	img1_array = np.array(img1)
	img2_array = np.array(img2)

	# Calculate the pixel-wise difference
	diff = img1_array - img2_array

	# Create a new grayscale image from the difference array
	diff_image = Image.fromarray(np.uint8(diff))

	diff_image = Image.eval(diff_image, lambda x: 255 -x)
	return diff_image

def get_measurements(fichier_texte):
    """
    Read a file and extract Reference data from findcoords file.

    This function reads the specified file and filters the rows with 'Reference' in the 'Type' column. 
    It then selects the 'X' and 'Y' columns and converts them into a NumPy array.

    Parameters:
        - fichier_texte (str): The path to the file containing the data.

    Returns:
        - numpy.ndarray: A NumPy array containing the 'X' and 'Y' columns of the filtered data.

    Example:
    If the file contains the following data:
    | Type          | X  | Y  |
    |---------------|----|----|
    | Reference     | 1  | 2  |
    | Reference     | 5  | 6  |
    | Measurement   | 3  | 4  |

    Calling get_measurements('data.txt') would return the following NumPy array:
    array([[1, 2],
           [5, 6]])

    Note:
    - Make sure the file exists and has a 'Type' column as well as 'X' and 'Y' columns.
    - The 'Type' column is used to filter rows containing 'Reference'.
    """

    df = pd.read_csv(fichier_texte)
    # Filter the rows with 'Measurement' in the 'Type' column
    measurements_df = df[df['Type'].str.startswith('Reference')]

    # Select the X and Y columns, then convert them into a NumPy array
    return measurements_df[['X', 'Y']].to_numpy()

pts_src = get_measurements(BASE_IMG_COORDS)
pts_dst = get_measurements(MODIFY_IMG_COORDS)

i = 0
if __name__ == '__main__' :
    for filename_base, filename_modify in zip(os.listdir(BASE_FOLDER), os.listdir(MODIFY_FOLDER)):
        print(filename_base, filename_modify)
        im_src = cv2.imread(BASE_FOLDER + '/' + filename_base)
        im_dst = cv2.imread(MODIFY_FOLDER + '/' + filename_modify)

        # Remove black pixels from images
        if not BLACK_PIXEL:
            im_src[im_src == 0] = 1
            im_dst[im_dst == 0] = 1

        h, status = cv2.findHomography(pts_dst, pts_src)
        #cv2.imshow("src avant", im_src)
        #cv2.imshow("dst avant", im_dst)
        im_out = cv2.warpPerspective(im_dst, h, (im_src.shape[1], im_src.shape[0]))
        #cv2.imshow("src apres", im_src)
        #cv2.imshow("dst apres", im_dst)
        #cv2.imshow("Warped Source Image", im_out)
        #cv2.waitKey(0)
        output_filename = OUTPUT_FOLDER + '/result_' + filename_modify
        cv2.imwrite(output_filename, im_out)
        image_difference(BASE_FOLDER + '/' + filename_base, output_filename).save('diff/' + filename_modify)