from enum import Enum


class LegoColor(Enum):
    BLUE = 1
    GREEN = 2
    RED = 3
    YELLOW = 4

    def __str__(self):
        return super.__str__(self).split('.')[1].split(':')[0]


class ShapeType(Enum):
    UNDEFINED = 1
    ONE_X_THREE = 2 # smallest possible logical value
    ONE_X_FOUR = 3
    TWO_X_TWO = 4
    TWO_X_FOUR = 5 # greatest possible logical value

    def __str__(self):
        name_upper = super.__str__(self).split('.')[1].split(':')[0]
        name_replaced = name_upper.replace('ONE', '1')
        name_replaced = name_replaced.replace('TWO', '2')
        name_replaced = name_replaced.replace('THREE', '3')
        name_replaced = name_replaced.replace('FOUR', '4')
        name_replaced = name_replaced.replace('_', '')
        name_lower = name_replaced.lower()

        return name_lower
    
        #return super.__str__(self).split('.')[1].split(':')[0]

    def __lt__(self, other):
        if other.__class__ is ShapeType:
            return self.value < other.value
        return -1


class ColoredShape:

    def __init__(self, pos, roi, color: LegoColor, shapeType: ShapeType):
        self.pos = pos
        self.roi = roi
        self.color = color
        self.shapeType = shapeType

    def __str__(self):
        if self.pos is not None:
            x, y = self.pos
            return f'{self.color} {self.shapeType} Brick at ({x:.2f}, {y:.2f})'
        else:
            return f'{self.color} {self.shapeType} Brick at undifined Position'

