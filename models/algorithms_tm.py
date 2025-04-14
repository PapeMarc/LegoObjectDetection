import cv2
import numpy as np
import os

from algorithms import getMinBBox
from dataclasses import LegoColor, ShapeType
from utils import imageConverter

# Template Matching: Determine shape types for colored shapes using template matching
def determineShapeTypesWithTemplateMatching(coloredShapes, image, color_masks):
    for coloredShape in coloredShapes:

            # Cut out the region of interest (ROI) with an offset for better matching
            roi = imageConverter.tryCutRoiWithOffset(coloredShape.roi, 25, image)
            roi_mask = imageConverter.tryCutRoiWithOffset(coloredShape.roi, 25, color_masks[coloredShape.color])
            
            mbb_size, correctedAngle = getMinBBox(roi_mask) # Corrected angle is used to reverse ROI rotation
            
            # Set default dimensions if MBB size is not available
            if mbb_size != None:
                mbb_w, mbb_h = mbb_size
            else:
                mbb_w = 1
                mbb_h = 1
            
            # Store the corrected angle in the shape object
            coloredShape.angle = correctedAngle

            # Identify the most likely shape type based on color and aspect ratio
            if coloredShape.color in [LegoColor.BLUE, LegoColor.YELLOW]:
                identifiedType = getMostLikelyType(coloredShape.color, ShapeType.ONE_X_FOUR, 
                                                   ShapeType.ONE_X_THREE, roi, correctedAngle)
                if identifiedType is None:
                    ratio = max(mbb_w, mbb_h) / min(mbb_w, mbb_h)
                    if ratio > 3.5:
                        identifiedType = ShapeType.ONE_X_FOUR
                    elif ratio > 2.5: 
                        identifiedType = ShapeType.ONE_X_THREE
            else:
                identifiedType = getMostLikelyType(coloredShape.color, ShapeType.TWO_X_FOUR, 
                                                   ShapeType.TWO_X_TWO, roi, correctedAngle)
                if identifiedType is None:
                    ratio = max(mbb_w, mbb_h) / min(mbb_w, mbb_h)
                    if ratio > 1.5:
                        identifiedType = ShapeType.TWO_X_FOUR
                    elif ratio > 0.5: 
                        identifiedType = ShapeType.TWO_X_TWO
            
            # Save the identified shape type or set it to undefined if no match is found
            if identifiedType is None:
                coloredShape.shapeType = ShapeType.UNDEFINED
            else:
                coloredShape.shapeType = identifiedType
                
    return coloredShapes

# Perform template matching to check if a given ROI matches a specific template
def applyTemplateMatching(roi, path_to_template, threshold, angle):
    
    # Load the template and convert both ROI and template to grayscale
    template = cv2.imread(path_to_template, cv2.IMREAD_GRAYSCALE)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    
    # Rotate and pad the ROI to align it with the template
    rotated_roi = rotate_image(roi_gray, angle)
    padded_roi = pad_roi_if_needed(rotated_roi, template)
    
    # Display the template and padded ROI for debugging purposes
    cv2.imshow('TEMPLATE', template)
    cv2.imshow('ROI', padded_roi)
    
    # Perform template matching and retrieve the highest match value
    result = cv2.matchTemplate(padded_roi, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]
    
    print(f'{path_to_template.split('/')[-1]} - Max Value: {max_val}')

    # Return True if the match value exceeds the threshold; otherwise False
    return max_val >= threshold

# Pad an ROI with black pixels if the template is larger than the ROI
def pad_roi_if_needed(roi, template):
    """Adds black pixels to the ROI, in case that the Template is bigger than the ROI."""
    roi_h, roi_w = roi.shape[:2]
    template_h, template_w = template.shape[:2]

    # Calculate padding sizes for height and width
    pad_h = max(0, template_h - roi_h)
    pad_w = max(0, template_w - roi_w)

    # Add black padding around the ROI (top/bottom/left/right)
    padded_roi = cv2.copyMakeBorder(
        roi,
        top=pad_h // 2,
        bottom=pad_h - pad_h // 2,
        left=pad_w // 2,
        right=pad_w - pad_w // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=0 # Black pixels for padding
    )
    
    return padded_roi

# Rotate an image by a specified angle while preserving its full content with padding
def rotate_image(image, angle):
    h, w = image.shape
    center = (w // 2, h // 2)
    
    # Calculate the rotation matrix for rotating around the center of the image
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Compute new dimensions to ensure no content is cropped after rotation
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust translation to center the rotated image within its new dimensions
    M[0, 2] += (new_w - w) // 2
    M[1, 2] += (new_h - h) // 2
    
    # Apply the rotation matrix to the image using cubic interpolation for quality
    return cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_CUBIC)

# Determine the most likely shape type based on color and predefined templates
def getMostLikelyType(color, typeA, typeB, roi, angle):

    greatest_type = max(typeA, typeB)
    path = os.path.join('assets', 'd02_templates_s')

    match greatest_type:
        case ShapeType.TWO_X_FOUR:

            # Define thresholds for red and green LEGO bricks
            match color:
                case LegoColor.RED:
                    thresh_2x4 = 0.17
                    thresh_2x2 = 0.17
                case LegoColor.GREEN:
                    thresh_2x4 = 0.19
                    thresh_2x2 = 0.17

            filename = f'2x4_{color.__str__().lower()}.jpg'
            match = applyTemplateMatching(roi, os.path.join(path, filename), thresh_2x4, angle)

            if match:
                return ShapeType.TWO_X_FOUR

            filename = f'2x2_{color.__str__().lower()}.jpg'
            match = applyTemplateMatching(roi, os.path.join(path, filename), thresh_2x2, angle)

            if match:
                return ShapeType.TWO_X_TWO

            return None

        case ShapeType.ONE_X_FOUR:

            # Define thresholds for blue and yellow LEGO bricks
            match color:
                case LegoColor.YELLOW:
                    thresh_1x4 = 0.221
                    thresh_1x3 = 0.25
                case LegoColor.BLUE:
                    thresh_1x4 = 0.3
                    thresh_1x3 = 0.27

            filename = f'1x4_{color.__str__().lower()}.jpg'
            match = applyTemplateMatching(roi, os.path.join(path, filename), thresh_1x4, angle)

            if match:
                return ShapeType.ONE_X_FOUR

            filename = f'1x3_{color.__str__().lower()}.jpg'
            match = applyTemplateMatching(roi, os.path.join(path, filename), thresh_1x3, angle)

            if match:
                return ShapeType.ONE_X_THREE
            
            return None
        
        case _:
            return None
        
