import cv2
import os
from utils.consoleWriter import writeMessage

# Function to open a video capture device with specified settings
def getVideoCapture(number, deviceWidth, deviceHeight, fastMode):
    '''
    Opens a new VideoCapture on the requested video device.
    Parameters:
        number (int): The index of the video capture device (e.g., 0 for the default camera).
        fastMode (bool): If True, uses the DirectShow backend (CAP_DSHOW) for faster access 
                        (Windows OS required).
    Returns:
        cv2.VideoCapture: An OpenCV VideoCapture object if successful.
        None: If fastMode is enabled but the operating system is not Windows.
    '''
    
    # Use DirectShow backend for fast mode if running on Windows
    if fastMode:
        # Check if the OS is not Windows
        if os.name != 'nt':
            return None
        capture = cv2.VideoCapture(number, cv2.CAP_DSHOW)
    else:
        # Open the video capture device with default backend
        capture = cv2.VideoCapture(number)
    
    # Check if the video capture device was successfully opened
    if not capture.isOpened():
        print(f'Camera {number} could not be opened.')
        exit()  # Exit the program if the camera cannot be accessed
    
    # Log a message indicating successful access to the capture device
    writeMessage(f'Accessed Capture {number}.')
    
    # Set the desired width and height for the video frames
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, deviceWidth)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, deviceHeight)
    
    return capture