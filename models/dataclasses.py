from enum import Enum

# Enum class to represent LEGO colors
class LegoColor(Enum):
    BLUE = 1
    GREEN = 2
    RED = 3
    YELLOW = 4

    def __str__(self):
        # Return the name of the color without the Enum prefix
        return super.__str__(self).split('.')[1].split(':')[0]


# Enum class to represent different LEGO shape types
class ShapeType(Enum):
    UNDEFINED = 1
    ONE_X_THREE = 2  # Smallest possible logical value
    ONE_X_FOUR = 3
    TWO_X_TWO = 4
    TWO_X_FOUR = 5  # Greatest possible logical value

    def __str__(self):
        # Convert the shape type name into a more readable format (e.g., "1x4")
        name_upper = super.__str__(self).split('.')[1].split(':')[0]
        name_replaced = name_upper.replace('ONE', '1')
        name_replaced = name_replaced.replace('TWO', '2')
        name_replaced = name_replaced.replace('THREE', '3')
        name_replaced = name_replaced.replace('FOUR', '4')
        name_replaced = name_replaced.replace('_', '')
        name_lower = name_replaced.lower()

        return name_lower

    def __lt__(self, other):
        # Compare shape types based on their logical value
        if other.__class__ is ShapeType:
            return self.value < other.value
        return -1


# Class to represent a colored LEGO shape with its properties
class ColoredShape:

    def __init__(self, pos, roi, color: LegoColor, shapeType: ShapeType, angle):
        self.pos = pos
        self.roi = roi
        self.color = color
        self.shapeType = shapeType
        self.angle = angle

    def __str__(self):
        # Format the color name with consistent spacing for alignment
        size = 6 - (len(self.color.__str__()) - 1)
        colorName = ' ' + self.color.__str__()
        for i in range(size - 1):
            colorName += ' '
        colorName += '  |'
            
        # Format the shape type with consistent spacing for alignment
        if self.shapeType is ShapeType.UNDEFINED:
            shape_type = ' ' + self.shapeType.__str__() + '  |'
        else:
            shape_type = ' ' + self.shapeType.__str__() + '        |'
            
        if self.pos is not None:
            x, y = self.pos
            if self.angle is not None:
                # Return formatted string with position and angle information
                return f'{colorName} {shape_type}  ({x:.2f}, {y:.2f})  |  {self.angle:.2f}{chr(176)}'
            # Return formatted string with position but no angle information
            return f'{colorName} {shape_type}  ({x:.2f}, {y:.2f})  |  '
        else:
            if self.angle is not None:
                # Return formatted string with angle but no position information
                return f'{colorName} {shape_type} {self.angle:.2f}{chr(176)}'
            else:
                # Return formatted string indicating undefined position and rotation
                return f'{colorName} {shape_type} undefined Position and Rotation'
