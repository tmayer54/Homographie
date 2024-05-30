#!/usr/bin/env python3.8
"""
@author: tmayer
"""
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
from PIL import Image


# load the images -- the original, the original + contrast

first_path = 'dect1_0/images_dect1_0_Si_K'
second_path = 'output'
img_ext = '.tiff'

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between each pixel of the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err

def compare_images(imageA, imageB, title):
	# compute the mean squared error and structural similarity
	# index for the images
	m = mse(imageA, imageB)
	s = ssim(imageA, imageB)
	
	# setup the figure
	fig = plt.figure(title)
	plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
	
	# show first image
	ax = fig.add_subplot(1, 2, 1)
	plt.imshow(imageA, cmap = plt.cm.gray)
	plt.axis("off") 
	
	# show the second image
	ax = fig.add_subplot(1, 2, 2)
	plt.imshow(imageB, cmap = plt.cm.gray)
	plt.axis("off")
	
	# show the images
	plt.show()
	

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

original = cv2.imread(first_path + img_ext)
#original = original[300:600, 200:500]
contrast = cv2.imread(second_path + img_ext)
#contrast = contrast[300:600, 200:500]

# convert the images to grayscale
original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)

# initialize the figure
fig = plt.figure("Images")
images = ("Original", original), ("Contrast", contrast)
# loop over the images
for (i, (name, image)) in enumerate(images):
	# show the image
	ax = fig.add_subplot(1, 3, i + 1)
	ax.set_title(name)
	plt.imshow(image, cmap = plt.cm.gray)
	plt.axis("off")
# show the figure
plt.show()
# compare the images
#compare_images(original, original, first_path + " vs. " + first_path)
compare_images(original, contrast, first_path +" vs. "  + second_path)

diff_image = image_difference(first_path + img_ext, second_path + img_ext)
diff_image.show()
diff_image.save('diff.tif')
plt.imshow(diff_image, cmap = plt.cm.gray)
plt.axis("off")
plt.show()