#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 7 10:17:51 2023

@author: tmayer
"""

import cv2
import pandas as pd
from config import BASE_PATH, BASE_IMG_EXT, BASE_IMG_COORDS, MODIFY_PATH, MODIFY_IMG_EXT, MODIFY_IMG_COORDS, OUTPUT_NAME, OUTPUT_FORMAT, BLACK_PIXEL

def get_measurements(fichier_texte):
    """
    Read a file and extract Reference data from findcoords file.

    This function reads the specifie    d file and filters the rows with 'Reference' in the 'Type' column. 
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
    print(df)
    # Filter the rows with 'Measurement' in the 'Type' column
    measurements_df = df[df['Type'].str.startswith('Reference')]

    # Select the X and Y columns, then convert them into a NumPy array
    return measurements_df[['X', 'Y']].to_numpy()

if __name__ == '__main__' :

    # Base -> used as a reference for the homographic transformation on the other image
    im_dst = cv2.imread(BASE_PATH + BASE_IMG_EXT)  

    # Modify -> image to be modified to match the base image reference points (homographic transformation)
    im_src = cv2.imread(MODIFY_PATH + MODIFY_IMG_EXT)

    pts_dst = get_measurements(BASE_IMG_COORDS)
    pts_src = get_measurements(MODIFY_IMG_COORDS)
    # Remove black pixels from images : only pixels not include in the homography will be black (value : 0)
    if BLACK_PIXEL == False:
        im_src[im_src == 0] = 1
        im_dst[im_dst == 0] = 1
    else : 
        pass
    # Calculate Homography
    h, status = cv2.findHomography(pts_src, pts_dst)
    print (h)
    print (status)
    
    print(im_src.shape[1])
    
    # Warp source image to destination based on homography
    im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1], im_dst.shape[0]))
    #Save the ouput
    cv2.imwrite(OUTPUT_NAME+OUTPUT_FORMAT, im_out)
    