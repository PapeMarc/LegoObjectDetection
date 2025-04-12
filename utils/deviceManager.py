import cv2
import os
from utils.consoleWriter import writeMessage

def getVideoCapture(number, deviceWidth, deviceHeight, fastMode):
    '''Opens a new VideoCapture on the requested Video Device.\n 
       When using Fast-Mode windows is required as the OS.\n 
       Otherwise it will return None.'''
    
    if fastMode:
        if os.name != 'nt':
            return None
        capture = cv2.VideoCapture(number, cv2.CAP_DSHOW)
    else:
        capture = cv2.VideoCapture(number)
    
    if not capture.isOpened():
        print(f'Camera {number} could not be opened.')
        exit()
    
    writeMessage(f'Accessed Capture {number}.')
    
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, deviceWidth)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, deviceHeight)
    
    return capture