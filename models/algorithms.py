import os
import cv2
import numpy as np
from utils import imageConverter as ic
from models.dataclasses import LegoColor
from models.dataclasses import ShapeType

def openAndClose(img, mask, kernalSize):

    morphKernal = cv2.getStructuringElement(cv2.MORPH_RECT, (kernalSize, kernalSize))
    mask_opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, morphKernal)
    mask_closing = cv2.morphologyEx(mask_opening, cv2.MORPH_CLOSE, morphKernal)
    
    result = cv2.bitwise_and(img, img, mask=mask_closing)
    return result

def colorSegmentation(img, kernalSize, lower, higher):
    hsv = ic.convertToHSV(img)
    mask = cv2.inRange(hsv, lower, higher)
    result = openAndClose(img, mask, kernalSize)

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

def determineShapeTypes(coloredShapes, image, color_masks):
    for coloredShape in coloredShapes:
        
        # Getting the ROI from the original Image
        x, y, w, h = coloredShape.roi
        img_h, img_w = image.shape[:2]

        # calculating and applying the offset if possible
        offset = 25
        if x >= offset & x <= img_w - offset:
            x_minus_offset = x - offset
            x_plus_offset = x + offset

        if y >= offset & y <= img_h-offset:
            y_minus_offset = y - offset
            y_plus_offset = y + offset

        if (not x_minus_offset is None) & (not y_minus_offset is None):
            roi = image[y_minus_offset:y_plus_offset+h, x_minus_offset:x_plus_offset+w]
            roi_mask = color_masks[coloredShape.color][y_minus_offset:y_plus_offset+h, x_minus_offset:x_plus_offset+w]

        roi = image[y:y+h, x:x+w]
        roi_mask = color_masks[coloredShape.color][y:y+h, x:x+w]
        angle = getMinBBoxAngle(roi_mask) # (inverted angle for reversing rotation of the ROI)
        coloredShape.angle = angle

        # identifying the most likely Type for the Shape
        if coloredShape.color in [LegoColor.BLUE, LegoColor.YELLOW]:
            identifiedType = getMostLikelyType(coloredShape.color, ShapeType.ONE_X_FOUR, ShapeType.ONE_X_THREE, roi, angle)
        else:
            identifiedType = getMostLikelyType(coloredShape.color, ShapeType.TWO_X_FOUR, ShapeType.TWO_X_TWO, roi, angle)
        
        # saving the identified Type into the Shape
        if identifiedType is None:
            coloredShape.shapeType = ShapeType.UNDEFINED
        else:
            coloredShape.shapeType = identifiedType
            
    return coloredShapes

def getMostLikelyType(color, typeA, typeB, roi, angle):

    greatest_type = max(typeA, typeB)
    path = os.path.join('assets', 'd02_templates_s')

    match greatest_type:
        case ShapeType.TWO_X_FOUR:

            # Specifying the threshold-value for the Colors Red and Green
            match color:
                case LegoColor.RED:
                    thresh_2x4 = 0.4
                    thresh_2x2 = 0.3
                case LegoColor.GREEN:
                    thresh_2x4 = 0.34
                    thresh_2x2 = 0.29

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
                    thresh_1x4 = 0.47
                    thresh_1x3 = 0.45
                case LegoColor.BLUE:
                    thresh_1x4 = 0.4
                    thresh_1x3 = 0.4

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
    
# Perplexity AI gefragt: 
# 1. "Was ist Template Matching und wie funktioniert es in OpenCV?" und
# 2.(Folgefrage) "Wie kann ich für eine ROI Template Matching anwenden, 
#   sodass ein Wahrheitswert entsteht, ob das Template im Bild vorkommt oder nicht?"
# 3. "Wie kann ich beim Template Matching Rotation berücksichtigen?" (Methode applyTemplateMatching angehangen)
# def applyTemplateMatching(roi, path_to_template):
#     # Load Template and convert ROI and the Template to a Grayscale Image
#     roi_gray = ic.convertToGray(roi)
#     template_gray = cv2.imread(path_to_template, cv2.IMREAD_GRAYSCALE)

#     # Apply TemplateMatching
#     result = cv2.matchTemplate(roi_gray, template_gray, cv2.TM_CCOEFF_NORMED)

#     # Determine if there was something found
#     threshold = 0.8
#     max_val = cv2.minMaxLoc(result)[1] # Returns: min_val, max_val, min_loc, max_loc
#     found_something = max_val >= threshold

#     return found_something
# 4. Ich habe folgendes Problem: Wenn ich mein Objekt in der ROI drehe, kann es passieren, 
#    dass das Template (rotiert oder nicht) größer, bzw. kleiner ist als die ROI. Da Template 
#    Matching nur funktioniert, wenn das Bild in dem das Template gesucht wird größer ist als 
#    das Template selbst, möchte ich das Problem wie folgt lösen: Ich möchte wenn die größe des 
#    Templates die größe des ROI-Ausschnitts überschreitet, das ROI so mit schwarzen Pixeln auffüllen, 
#    dass die Größe des Templates wieder kleiner bzw. gleich groß ist. Folgende Frage an dich: kann 
#    das hinsichtlich des template-matchings funktionieren?

def applyTemplateMatching(roi, path_to_template, threshold, angle):
    
    # Load Template and convert both to Grayscale
    template = cv2.imread(path_to_template, cv2.IMREAD_GRAYSCALE)
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi
    
    rotated_roi = rotate_image(roi_gray, angle)
    padded_roi = pad_roi_if_needed(rotated_roi, template)
    
    h, w = padded_roi.shape[0:2]
    
    result = cv2.matchTemplate(padded_roi, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]
    
    #print(f'Max Value: {max_val}')

    # determine the boolean Value
    return max_val >= threshold

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

# Perplexity AI gefragt:
# 1. Wie kann ich diesen Winkel in einen repräsentativen Winkel 
#    zur rotation meines templates für template matching bekommen?

def getMinBBoxAngle(roi_mask):
    
    contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
    for contour in contours:
        contour_area = cv2.contourArea(contour)

        if(contour_area < 400):
            continue
        
    _, (w_rect, h_rect), angle = cv2.minAreaRect(contour)
    
    angle -= 90
    
    if w_rect < h_rect:
        angle += 90
    
    angle = angle % 180
    
    return angle