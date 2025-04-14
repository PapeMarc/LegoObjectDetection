import cv2
import numpy as np
from utils import imageConverter as ic
from models.dataclasses import LegoColor
from models.dataclasses import ShapeType

# Perform morphological opening and closing operations on a binary mask
def morphology_open_and_close(img, mask, kernalSize):
    # Create a rectangular kernel for morphological operations
    morphKernal = cv2.getStructuringElement(cv2.MORPH_RECT, (kernalSize, kernalSize))
    
    # Apply opening to remove small noise in the mask
    mask_opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morphKernal)
    
    # Apply closing to fill small gaps in the mask
    mask_closing = cv2.morphologyEx(mask_opening, cv2.MORPH_CLOSE, morphKernal)
    
    # Combine the cleaned mask with the original image
    result = cv2.bitwise_and(img, img, mask=mask_closing)
    return result

# Segment colors in an image using HSV thresholds and morphological operations
def colorSegmentation(img, kernalSize, lower, higher):
    '''lower / higher: [Hue, Sat, Val]'''
    # Convert the image to HSV color space for easier color segmentation
    hsv = ic.convertToHSV(img)
    
    # Create a binary mask based on HSV thresholds
    mask = cv2.inRange(hsv, lower, higher)
    
    # Clean the mask using opening and closing operations
    result = morphology_open_and_close(img, mask, kernalSize)

    return mask, result

# Extract regions of interest (ROIs) for each color from segmented images
def get_color_rois(masked_blue, masked_green, masked_red, masked_yellow):
    # Convert each color-segmented image to grayscale for contour detection
    images_gray = np.array([ic.convertToGray(masked_blue.copy()),
                            ic.convertToGray(masked_green.copy()),
                            ic.convertToGray(masked_red.copy()),
                            ic.convertToGray(masked_yellow.copy())])
    
    # Initialize a dictionary to store ROIs for each LEGO color
    roi_dict = {LegoColor.BLUE: [], LegoColor.GREEN: [], LegoColor.RED: [], LegoColor.YELLOW: []}
    roi_keys = list(roi_dict)

    # Iterate through each color's grayscale image to detect contours
    for i in range(len(roi_dict)):
        gray = images_gray[i]
    
        # Detect external contours in the grayscale image
        contours, _ = cv2.findContours(
           gray, 
           cv2.RETR_EXTERNAL, 
           cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Iterate through detected contours and calculate bounding boxes (ROIs)
        for i2, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            roi_dict[roi_keys[i]].append((x, y, w, h))

    return roi_dict

# Determine the positions of shapes within a normalized unit square
def determineShapePositions(shapes, image):
    h, w = image.shape[:2]
    length = min(h, w)  # Use the smallest dimension to normalize positions

    for shape in shapes:
        x, y, w, h = shape.roi
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Normalize coordinates within the unit square
        unit_square_x = center_x / length
        unit_square_y = center_y / length
        
        shape.pos = (unit_square_x, unit_square_y)  # Save normalized position

    return shapes

# Filter out shapes with pixel counts below a specified threshold
def filterShapesByPixelCount(shapes, pixelCount):
    filtered = []
    
    for shape in shapes:
        _, _, w, h = shape.roi
        shapePixelCount = w * h
    
        # Include shapes above the threshold
        if shapePixelCount > pixelCount:
            filtered.append(shape)

    return filtered

# Determine the types of shapes based on their aspect ratios and bounding boxes
def determineShapeTypes(coloredShapes, color_masks):  
      
    for coloredShape in coloredShapes:
        # Cut out the ROI from the mask with an offset for better analysis
        roi_mask = ic.tryCutRoiWithOffset(coloredShape.roi, 25, color_masks[coloredShape.color])
        
        # Get the smallest bounding box (MBB) and corrected angle for the ROI mask
        _, mbb_size, angle = getMinBBox(roi_mask)  
        
        if mbb_size is None or angle is None:
            continue # Skip if no bounding box is found
        
        mbb_w, mbb_h = mbb_size
        
        # Save corrected angle into shape object
        coloredShape.angle = angle

        # Identify the most likely type based on aspect ratio and color
        if coloredShape.color in [LegoColor.BLUE, LegoColor.YELLOW]:
            ratio = max(mbb_w, mbb_h) / min(mbb_w, mbb_h)
            identifiedType = None
            
            if ratio > 3.19:
                identifiedType = ShapeType.ONE_X_FOUR
            elif ratio > 2.4: 
                identifiedType = ShapeType.ONE_X_THREE
                
        else:
            ratio = max(mbb_w, mbb_h) / min(mbb_w, mbb_h)
            
            if ratio > 1.8:
                identifiedType = ShapeType.TWO_X_FOUR
            elif ratio > 0.9: 
                identifiedType = ShapeType.TWO_X_TWO
        
        if identifiedType is None:
            coloredShape.shapeType = ShapeType.UNDEFINED
        else:
            coloredShape.shapeType = identifiedType
            
    return coloredShapes

# Calculate the smallest bounding box around a contour and its corrected angle
def getMinBBox(roi_mask):
    
    contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
    best_contour = None
    max_area = 0
            
    for contour in contours:
        contour_area = cv2.contourArea(contour)

        # Skip small contours below area threshold
        if contour_area < 1000:
            continue
        
        # Update largest contour found so far
        if contour_area > max_area:
            max_area = contour_area
            best_contour = contour
        
    # Return None if no valid contour is found
    if best_contour is None:
        return None, None, None
        
    # Get bounding box
    center, size, angle = cv2.minAreaRect(best_contour)
    
    w, h = size
    
    correctedAngle = angle - 90 if w < h else angle % 180
    
    # Handle degenerate cases where width or height is zero
    if w == 0 or h == 0:
        return None, None, correctedAngle
    
    return center, size, correctedAngle  
