import cv2

def getImageCenterSquare(image):
    h, w = image.shape[0:2]
    crop_length = min(h, w)
    
    crop_x = (w - crop_length) // 2
    crop_y = (h - crop_length) // 2
    
    centeredSquare = image[crop_y:crop_y + crop_length, crop_x:crop_x + crop_length]
    
    return centeredSquare

def convertToHSV(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv

def convertToGray(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray