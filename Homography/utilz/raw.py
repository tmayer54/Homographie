#!/usr/bin/env python3.8
# -*- coding: utf-8 -*-

import cv2
import numpy as np 
import pandas as pd
import hyperspy.api as hs
import matplotlib.pyplot as plt

s = hs.load("cube/Ag-Pb/Ag_in_Pb.rpl")
pt_base = np.array([[0, 0], [189, 0], [189, 171], [0, 171]])
pt_image_to_modify = np.array([[189, 0], [189, 171], [0, 171], [0, 0]])

h, status = cv2.findHomography(pt_image_to_modify, pt_base)
#print(h)
#print(status)

p = s.data

print(f"Height = p.shape[0]: {p.shape[0]}")
print(f"Width = p.shape[1]: {p.shape[1]}")
print(f"Depth = p.shape[2]: {p.shape[2]}")

# Somme de toutes les tranches
summed_slice = np.sum(p, axis=2)
# Appliquer l'homographie à chaque tranche du cube
homography_cube = []
for i in range(p.shape[2]):
    warped_slice = cv2.warpPerspective(p[:, :, i], h, (p.shape[1], p.shape[0]))
    homography_cube.append(warped_slice)

# Affichage de la somme
plt.imshow(summed_slice, cmap='gray')  # Assuming grayscale, change colormap as needed
plt.title('Somme des tranches du cube')
plt.axis('off')
plt.show()

# Affichage de la somme après homographie
homography_summed_slice = np.sum(homography_cube, axis=0)
plt.imshow(homography_summed_slice, cmap='gray')  # Assuming grayscale, change colormap as needed
plt.title('Somme des tranches après homographie')
plt.axis('off')
plt.show()