import cv2

from utils.consoleWriter import writeMessage

def getVideoCapture(number, deviceWidth, deviceHeight):
    capture = cv2.VideoCapture(number)
    
    if not capture.isOpened():
        print(f'Camera {number} could not be opened.')
        exit()
    
    writeMessage(f'Accessed Capture {number}.')
    
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, deviceWidth)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, deviceHeight)
    
    return capture