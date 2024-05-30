#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 5 8:05:19 2023

@author: tmayer
"""

import numpy as np
import pandas as pd
import hyperspy.api as hs
from skimage.transform import warp
from skimage.feature import register_translation
import cv2

BASE_IMG_COORDS = "cube0.txt"
MODIFY_IMG_COORDS = "cube90.txt"

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


def apply_homography(cube, h_matrix):
    """
    Apply a homography transformation to a HyperSpy signal.

    Parameters:
        - cube (hs.signals.Signal2D or hs.signals.Signal3D): The HyperSpy signal representing the cube of data.
        - h_matrix (numpy.ndarray): The 3x3 homography matrix.

    Returns:
        - hs.signals.Signal2D or hs.signals.Signal3D: The transformed HyperSpy signal.
    """
    # Extract data from the HyperSpy signal
    data = cube.data

    # Get the shape of the data
    shape = data.shape
    data = np.array(data)

    # Reshape the data to a 2D array
    print("Data shape before reshaping:", data.shape)
    data_2d = data.reshape(shape[0], -1)

    # Apply the homography transformation to each column (spectrum)
    transformed_data_2d = warp(data_2d, h_matrix)

    # Reshape the transformed data back to the original shape
    transformed_data = transformed_data_2d.reshape(shape)

    # Create a new HyperSpy signal with the transformed data
    transformed_cube = hs.signals.Signal2D(transformed_data) if len(shape) == 2 else hs.signals.Signal2D(transformed_data)

    # Copy metadata from the original signal to the transformed signal
    transformed_cube.metadata = cube.metadata.copy()

    return transformed_cube

def load_raw_data(raw_filename):
    """
    Load raw data from a .raw file as a HyperSpy signal.

    Parameters:
        - raw_filename (str): The path to the .raw file.

    Returns:
        - hs.signals.Signal2D: The HyperSpy signal representing the loaded data.
    """
    signal = hs.load(raw_filename)
    return signal

def save_raw_data(output_filename, signal):
    """
    Save the HyperSpy signal data to a .raw file.

    Parameters:
        - output_filename (str): The path to the output .raw file.
        - signal (hs.signals.Signal2D or hs.signals.Signal3D): The HyperSpy signal containing the data to be saved.

    Returns:
        - None
    """
    # Extract data from the HyperSpy signal
    data = signal.data

    # Ensure the data is in the correct format for saving
    if data.dtype != np.float32:
        data = data.astype(np.float32)

    # Save the data to a .raw file
    data.tofile(output_filename)

# Example usage
base_cube = load_raw_data("transfer/TS3/TS3.raw")
print(base_cube)
#base_cube = load_raw_data("transfer/TS3/TS3.raw", "transfer/TS3/TS3.rpl")
modify_cube = load_raw_data("transfer/TS3/TS3.raw")
pts_src = get_measurements(BASE_IMG_COORDS)
pts_dst = get_measurements(MODIFY_IMG_COORDS)
# Assuming pts_dst and pts_src are your correspondences
h_matrix, _ = cv2.findHomography(pts_dst, pts_src)

# Apply homography to the cubes
transformed_modify_cube = apply_homography(modify_cube, h_matrix)

# Save the result
save_raw_data("output/result_cube.raw", transformed_modify_cube)
