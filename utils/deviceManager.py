import cv2
import os
from utils.consoleWriter import writeMessage

# ChatGPT gefragt: Wie schaffe ich es, dass ich mein Video Capture schneller finde? 
# Ich verwende im Moment videocapture(1).

def getVideoCapture(number, deviceWidth, deviceHeight):
    '''Opens a new VideoCapture on the requested Video Device.\n 
       Assuming that windows is the OS. Otherwise it will return None.'''
        
    if os.name != 'nt':
        return None
    
    capture = cv2.VideoCapture(number, cv2.CAP_DSHOW)
    
    if not capture.isOpened():
        print(f'Camera {number} could not be opened.')
        exit()
    
    writeMessage(f'Accessed Capture {number}.')
    
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, deviceWidth)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, deviceHeight)
    
    return capture