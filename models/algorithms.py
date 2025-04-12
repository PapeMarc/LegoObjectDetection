import os
import cv2
import numpy as np
from utils import imageConverter as ic
from models.dataclasses import LegoColor
from models.dataclasses import ShapeType

def morphology_open_and_close(img, mask, kernalSize):

    morphKernal = cv2.getStructuringElement(cv2.MORPH_RECT, (kernalSize, kernalSize))
    mask_opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morphKernal)
    mask_closing = cv2.morphologyEx(mask_opening, cv2.MORPH_CLOSE, morphKernal)
    
    result = cv2.bitwise_and(img, img, mask=mask_closing)
    return result

def colorSegmentation(img, kernalSize, lower, higher):
    '''lower / higher: [Hue, Sat, Val]'''
    hsv = ic.convertToHSV(img)
    mask = cv2.inRange(hsv, lower, higher)
    result = morphology_open_and_close(img, mask, kernalSize)

    return mask, result

def get_color_rois(masked_blue, masked_green, masked_red, masked_yellow):
    images_gray = np.array([ic.convertToGray(masked_blue.copy()),
                            ic.convertToGray(masked_green.copy()),
                            ic.convertToGray(masked_red.copy()),
                            ic.convertToGray(masked_yellow.copy())])
    
    roi_dict = {LegoColor.BLUE: [], LegoColor.GREEN: [], LegoColor.RED: [], LegoColor.YELLOW: []}
    roi_keys = list(roi_dict)

    for i in range(len(roi_dict)):
        gray = images_gray[i]
    
        # get all Contours
        contours, _ = cv2.findContours(
           gray, 
           cv2.RETR_EXTERNAL, 
           cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Iterate through Contours
        for i2, contour in enumerate(contours):
            # create ROI and append to Dict
            x, y, w, h = cv2.boundingRect(contour)
            roi_dict[roi_keys[i]].append((x, y, w, h))

    return roi_dict

def determineShapePositions(shapes, image):
    h, w = image.shape[:2]
    length = min(h, w)

    for shape in shapes:
        x, y, w, h = shape.roi
        center_x = x + w // 2
        center_y = y + h // 2
        unit_square_x = center_x / length
        unit_square_y = center_y / length
        shape.pos = (unit_square_x, unit_square_y)

    return shapes

def filterShapesByPixelCount(shapes, pixelCount):
    filtered = []
    for shape in shapes:
        x,y,w,h = shape.roi
        shapePixelCount = w*h
        if shapePixelCount > pixelCount:
            filtered.append(shape)

    return filtered

def determineShapeTypes(coloredShapes, color_masks):  
      
    for coloredShape in coloredShapes:

        # cutting out the roi with an offset when possible
        roi_mask = ic.tryCutRoiWithOffset(coloredShape.roi, 25, color_masks[coloredShape.color])
        
        # getting the smallest possible BBox
        _, mbb_size, angle = getMinBBox(roi_mask) # (inverted angle for reversing rotation of the ROI)
        if mbb_size is None or angle is None:
            continue
        mbb_w, mbb_h = mbb_size
        coloredShape.angle = angle

        # identifying the most likely Type for the Shape
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
        
        # saving the identified Type into the Shape
        if identifiedType is None:
            coloredShape.shapeType = ShapeType.UNDEFINED
        else:
            coloredShape.shapeType = identifiedType
            
    return coloredShapes
    
def getMinBBox(roi_mask):
    
    contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
    best_contour = None
    max_area = 0
            
    for contour in contours:
        contour_area = cv2.contourArea(contour)

        if(contour_area < 1000):
            continue
        
        if contour_area > max_area:
            max_area = contour_area
            best_contour = contour
        
    if best_contour is None:
        return None, None, None
        
    center, size, angle = cv2.minAreaRect(best_contour)
    w, h = size
    
    correctedAngle = angle
    correctedAngle -= 90
    
    if w < h:
        correctedAngle += 90
    
    correctedAngle = correctedAngle % 180
    
    if w == 0 or h == 0:
        return None, None, correctedAngle
    else:
        return center, size, correctedAngle