import cv2
import numpy as np

from utils.imageConverter import resizeImage

# Combine two rows of images with separators into a single image
def combineImages(images_top, images_bottom, line_thickness):
    # Define the separator color
    white = (255, 255, 255)  
    
    # Combine the top row of images horizontally with the separator
    top_row = np.hstack((
        images_top[0],
        np.full((images_top[0].shape[0], line_thickness, 3), white, dtype=np.uint8),
        images_top[1]
    ))
    
    # Combine the bottom row of images horizontally with the separator
    bottom_row = np.hstack((
        images_bottom[0],
        np.full((images_bottom[0].shape[0], line_thickness, 3), white, dtype=np.uint8),
        images_bottom[1]
    ))
    
    # Add a vertical separator between the top and bottom rows
    separator = np.full((line_thickness, top_row.shape[1], 3), white, dtype=np.uint8)
    
    # Combine the top row, separator, and bottom row vertically
    combined = np.vstack((top_row, separator, bottom_row))
    
    return combined

# Draw an "X" marker at the center of a region of interest (ROI)
def printROIMarker(image, center_x, center_y, offset, ui_color, ui_thickness):
    # First diagonal line
    cv2.line(
        image, 
        (center_x - offset, center_y - offset), 
        (center_x + offset, center_y + offset), 
        ui_color, 
        ui_thickness
    )
    
    # Secound diagonal line
    cv2.line(
        image, 
        (center_x + offset, center_y - offset), 
        (center_x - offset, center_y + offset), 
        ui_color, 
        ui_thickness
    )

    return image

# Draw bounding boxes around the ROIs in an image
def drawBBoxes(image, shapes, ui_color, ui_thickness):
    
    # Iterate through the list of shapes 
    # and draw rectangles for each ROI
    for shape in shapes:
        x, y, w, h = shape.roi
        
        cv2.rectangle(
            image, 
            (x, y), 
            (x + w, y + h), 
            ui_color,
            ui_thickness
        )

    return image

# Draw markers at the centers of bounding boxes for each shape
def drawBBoxCenters(image, shapes, color, line_thickness, line_length):
    
    for shape in shapes:
        x,y,w,h = shape.roi

        center_x = x + w // 2
        center_y = y + h // 2  

        # Draw an "X" marker at the calculated center coordinates
        image = printROIMarker(image, center_x, center_y, line_length, color, line_thickness)

    return image

# Annotate bounding boxes with index information above each ROI
def drawInfo(image, shapes, color, line_thickness):

    for i in range(len(shapes)):
        
        shape = shapes[i]
        
        x,y,w,h = shape.roi
        
        # Add text annotation with the index number above each ROI
        cv2.putText(
            image,
            f'[{i+1}]',
            (x-5, y-20), 
            cv2.FONT_ITALIC,
            0.8,
            color,
            line_thickness
        )
        
    return image

# Display an image in a window or close it if not enabled
def showImage(image, title, scale, show):
    if show:
        if scale == 1:
            cv2.imshow(title, image)
            return
        
        # Resize and show the image based on the scaling factor
        cv2.imshow(title, resizeImage(image, scale))
        
    # Close the window if it is currently visible but not enabled for display
    elif cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) > 0:
        cv2.destroyWindow(title)
