import cv2

def getVideoCapture(number):
    capture = cv2.VideoCapture(0)
    if not capture.isOpened():
        print(f'Camera {number} could not be opened.')
        exit()
    print(f'Accessed Capture {number}.')
    return capture