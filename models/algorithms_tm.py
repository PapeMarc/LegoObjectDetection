import cv2
import numpy as np
import os

from algorithms import getMinBBox
from dataclasses import LegoColor, ShapeType
from utils import imageConverter

# Template Matching
def determineShapeTypesWithTemplateMatching(coloredShapes, image, color_masks):
    for coloredShape in coloredShapes:

            # cutting out the roi with an offset when possible
            roi = imageConverter.tryCutRoiWithOffset(coloredShape.roi, 25, image)
            roi_mask = imageConverter.tryCutRoiWithOffset(coloredShape.roi, 25, color_masks[coloredShape.color])
            
            mbb_size, correctedAngle = getMinBBox(roi_mask) # (inverted angle for reversing rotation of the ROI)
            
            if mbb_size != None:
                mbb_w, mbb_h = mbb_size
            else:
                mbb_w = 1
                mbb_h = 1
            
            coloredShape.angle = correctedAngle

            # identifying the most likely Type for the Shape
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
            
            # saving the identified Type into the Shape
            if identifiedType is None:
                coloredShape.shapeType = ShapeType.UNDEFINED
            else:
                coloredShape.shapeType = identifiedType
                
    return coloredShapes

def applyTemplateMatching(roi, path_to_template, threshold, angle):
    
    # Load Template and convert both to Grayscale
    template = cv2.imread(path_to_template, cv2.IMREAD_GRAYSCALE)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    
    rotated_roi = rotate_image(roi_gray, angle)
    padded_roi = pad_roi_if_needed(rotated_roi, template)
    
    cv2.imshow('TEMPLATE', template)
    cv2.imshow('ROI', padded_roi)
    
    result = cv2.matchTemplate(padded_roi, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]
    
    print(f'{path_to_template.split('/')[-1]} - Max Value: {max_val}')

    # determine the boolean Value
    return max_val >= threshold

def pad_roi_if_needed(roi, template):
    """Adds black pixels to the ROI, in case that the Template is bigger than the ROI."""
    roi_h, roi_w = roi.shape[:2]
    template_h, template_w = template.shape[:2]

    # Calculate necessary Padding-Sizes
    pad_h = max(0, template_h - roi_h)
    pad_w = max(0, template_w - roi_w)

    # Fill ROI with black pixels (top/bottom/left/right)
    padded_roi = cv2.copyMakeBorder(
        roi,
        top=pad_h // 2,
        bottom=pad_h - pad_h // 2,
        left=pad_w // 2,
        right=pad_w - pad_w // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=0  # Black
    )
    
    return padded_roi

def rotate_image(image, angle):
    h, w = image.shape
    center = (w // 2, h // 2)
    
    # Calculate the rotation Matrix
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Sort Template with Padding (avoids trimming)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    M[0, 2] += (new_w - w) // 2
    M[1, 2] += (new_h - h) // 2
    
    # Apply Rotation-Matrix
    return cv2.warpAffine(image, M, (new_w, new_h), flags=cv2.INTER_CUBIC)

def getMostLikelyType(color, typeA, typeB, roi, angle):

    greatest_type = max(typeA, typeB)
    path = os.path.join('assets', 'd02_templates_s')

    match greatest_type:
        case ShapeType.TWO_X_FOUR:

            # Specifying the threshold-value for the Colors Red and Green
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

            # Specifying the threshold-value for the Colors Blue and Yellow
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
        
