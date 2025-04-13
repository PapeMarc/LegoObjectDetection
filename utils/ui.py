import numpy as np
import cv2

from utils.imageConverter import resizeImage

def combineImages(images_top, images_bottom, line_thickness):
    # Combine Images
    white = (255, 255, 255)  
    
    # horizontal
    top_row = np.hstack((
        images_top[0],
        np.full((images_top[0].shape[0], line_thickness, 3), white, dtype=np.uint8),
        images_top[1]
    ))
    bottom_row = np.hstack((
        images_bottom[0],
        np.full((images_bottom[0].shape[0], line_thickness, 3), white, dtype=np.uint8),
        images_bottom[1]
    ))
    
    # Vertical
    separator = np.full((line_thickness, top_row.shape[1], 3), white, dtype=np.uint8)
    combined = np.vstack((top_row, separator, bottom_row))
    
    return combined

def printROIMarker(image, center_x, center_y, offset, ui_color, ui_thickness):
    cv2.line(
        image, 
        (center_x - offset, center_y - offset), 
        (center_x + offset, center_y + offset), 
        ui_color, 
        ui_thickness
    )
    cv2.line(
        image, 
        (center_x + offset, center_y - offset), 
        (center_x - offset, center_y + offset), 
        ui_color, 
        ui_thickness
    )

    return image

def drawBBoxes(image, shapes, ui_color, ui_thickness):
    
    # Iterate through list of rois
    for shape in shapes:

        x, y, w, h = shape.roi
        
        cv2.rectangle(
            image, 
            (x, y), 
            (x + w, y + h), 
            ui_color, ui_thickness
        )

    return image

def drawBBoxCenters(image, shapes, color, line_thickness, line_length):
    
    for shape in shapes:
        x,y,w,h = shape.roi

        # Calculate the center of the ROI
        center_x = x + w // 2
        center_y = y + h // 2  

        # Draw an "X" at the center
        image = printROIMarker(image, center_x, center_y, line_length, color, line_thickness)

    return image

def drawInfo(image, shapes, color, line_thickness):

    for i in range(len(shapes)):
        
        shape = shapes[i]
        
        x,y,w,h = shape.roi
        
        cv2.putText(
            image, f'[{i+1}]', {shape.color}, {shape.shapeType},
            (x-5, y-20), 
            cv2.FONT_ITALIC, 
            0.8, 
            color, line_thickness
        )
        
    return image

def showImage(image, title, scale, show):
    if show:
        if scale == 1:
            cv2.imshow(title, image)
            return
        cv2.imshow(title, resizeImage(image, scale))
    elif cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0:
        cv2.destroyWindow(title)  