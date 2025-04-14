import cv2
import numpy as np

# Crop the image to the largest possible centered square
def getImageCenterSquare(image):
    h, w = image.shape[0:2]
    crop_length = min(h, w)
    
    # Calculate the offsets for cropping
    crop_x = (w - crop_length) // 2  
    crop_y = (h - crop_length) // 2
    
    # Crop the image to a centered square
    centeredSquare = image[crop_y:crop_y + crop_length, crop_x:crop_x + crop_length]
    
    return centeredSquare

# Convert an image from BGR color space to HSV color space
def convertToHSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv

# Convert an image from BGR color space to grayscale
def convertToGray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

# Adjust the height of a smaller image to match the height of a larger image
def adjustImageHeights(smaller_image: np.ndarray, larger_image: np.ndarray) -> np.ndarray:
    s_h, s_w = smaller_image.shape[:2]
    l_h, _ = larger_image.shape[:2]
    
    # Calculate scaling factor based on height
    scale_factor = l_h / s_h

    # Resize using area interpolation
    resized_roi = cv2.resize(smaller_image, 
                             (int(s_w * scale_factor), int(s_h * scale_factor)), 
                             interpolation=cv2.INTER_AREA)
    
    return resized_roi

# Resize an image by a given scaling factor
def resizeImage(image, factor) -> np.ndarray:
    if factor <= 0:
        return image
    
    h, w = image.shape[:2]

    # Calculate new dimensions based on scaling factor
    new_h, new_w = h * factor, w * factor
    
    resized = cv2.resize(image, (int(new_w), int(new_h)))
    return resized

# Attempt to cut out a region of interest (ROI) with an offset from an image
def tryCutRoiWithOffset(roi, offset, image):
    x, y, w, h = roi
    img_h, img_w = image.shape[:2]

    # Validate and calculate horizontal offsets for cropping
    if x >= offset & x <= img_w - offset:
        x_minus_offset = x - offset
        x_plus_offset = x + offset

    # Validate and calculate vertical offsets for cropping
    if y >= offset & y <= img_h - offset:
        y_minus_offset = y - offset
        y_plus_offset = y + offset

    # Crop using calculated offsets if valid; otherwise use original ROI bounds
    if (not x_minus_offset is None) & (not y_minus_offset is None):
        return image[y_minus_offset:y_plus_offset+h, x_minus_offset:x_plus_offset+w]
    
    return image[y:y+h, x:x+w]
