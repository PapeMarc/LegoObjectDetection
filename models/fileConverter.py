from models.dataclasses import ColoredShape

def convertRoiDictIntoShapeList(dict):
    shapes = []
    for color, rois in dict.items():
        for roi in rois:
            x, y, w, h = roi
            newShape = ColoredShape(None, roi, color, None, None)
            shapes.append(newShape)
    return shapes