from models.dataclasses import ColoredShape

def convertRoiDictIntoColoredShapeList(dict):
    coloredShapes = []
    for color, rois in dict.items():
        for roi in rois:
            x, y, w, h = roi
            newShape = ColoredShape(None, roi, color, None, None)
            coloredShapes.append(newShape)
    return coloredShapes