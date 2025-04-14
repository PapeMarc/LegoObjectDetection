from models.dataclasses import ColoredShape

# Convert a dictionary of ROIs into a list of ColoredShape objects
def convertRoiDictIntoColoredShapeList(dict):
    coloredShapes = []
    
    # Iterate through the dictionary, where keys represent colors and values are lists of ROIs
    for color, rois in dict.items():
        for roi in rois:
            
            # Create a new ColoredShape object with default values for position, shapeType, and angle
            newShape = ColoredShape(None, roi, color, None, None)
            
            # Add the new shape to the list
            coloredShapes.append(newShape)
    
    return coloredShapes  # Return the list of ColoredShape objects
