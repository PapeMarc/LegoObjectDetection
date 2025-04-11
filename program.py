import cv2
import os
import sys
import numpy as np
from datetime import datetime

from utils import deviceManager
from utils import imageConverter
from utils import ui
from utils import consoleWriter
from models.dataclasses import LegoColor
from models.dataclasses import ShapeType
from models.dataclasses import ColoredShape
import models.fileConverter as fileConverter
import models.algorithms as alg

class Program:
    
    def __init__(self, args):
        os.system('cls')
        
        # Load environment Values
        self.default_refresh_rate = int(args[0]['DEF_REFRESH_RATE'])
        self.max_refresh_rate = int(args[0]['MAX_REFRESH_RATE'])
        self.min_refresh_rate = int(args[0]['MIN_REFRESH_RATE'])
        self.device_width = float(args[0]['CAMERA_WIDTH'])
        self.device_height = float(args[0]['CAMERA_HEIGHT'])
        self.imshow_scale = float(args[0]['IMSHOW_SCALE'])
        
        consoleWriter.writeStatus('Program initialized.')

    def exit(self):
        consoleWriter.writeStatus('Program exited.')
        exit()

    def main(self):
        
        # Create Control Panel Window and Trackbars
        cv2.namedWindow('Control Panel')
        cv2.resizeWindow('Control Panel', 600, 200)
        
        # https://www.w3schools.com/python/python_lambda.asp
        cv2.createTrackbar('Refresh Rate','Control Panel', 
                           int(self.default_refresh_rate / 100), 
                           int(self.max_refresh_rate / 100), 
                           lambda placeholder: None)
        
        cv2.createTrackbar('Original','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Colors','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Channels','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Result','Control Panel', 1, 1, lambda placeholder: None)
        
        try:
            
            # When no fast refresh rate is needed, the CAP_DSHOW 
            # Windows Backend is used to locate the Video Caputre Device
            fast_mode = True
            if self.min_refresh_rate < 1000:
                fast_mode = False
            
            # getting Video Capture
            capture = deviceManager.getVideoCapture(1, self.device_width, self.device_height, fast_mode)

            # Running through Frames
            while True:
                frameAvailable, frame = capture.read()
                if not frameAvailable:
                    consoleWriter.writeError('Frame not available.')
                    break

                # Reading Trackbar Values
                refresh_rate = cv2.getTrackbarPos('Refresh Rate','Control Panel') * 100
                show_original = cv2.getTrackbarPos('Original','Control Panel') == 1
                show_color_seperated = cv2.getTrackbarPos('Colors','Control Panel') == 1
                show_color_channels = cv2.getTrackbarPos('Channels','Control Panel') == 1
                show_result = cv2.getTrackbarPos('Result','Control Panel') == 1
                
                if refresh_rate == 0:
                    refresh_rate = self.min_refresh_rate

                # Cropping the Frame to the max possible inner Square
                frame_cropped = imageConverter.getImageCenterSquare(frame)
                
                # Showing the Original Image if enabled
                ui.showImage(frame_cropped, 'Original', self.imshow_scale, show_original)

                # Seperating the colors from the Background using Color Segmentation
                # and opening and closing
                color_seperated_mask, color_seperated = alg.colorSegmentation(
                    frame_cropped, 5,
                    np.array([0, 75, 0]), 
                    np.array([255, 255, 255])
                )
                
                # Showing the color seperated Image if enabled
                ui.showImage(color_seperated, 'Color seperated', self.imshow_scale, show_color_seperated)

                # Using color specific Segmentation
                # Filtering out blue Pixels
                blue_mask, blue_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([105, 100, 0]), 
                    np.array([170, 255, 255])
                )
                # Filtering out green Pixels
                green_mask, green_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([50, 27, 0]), 
                    np.array([100, 255, 131])
                )

                # Perplexity AI gefragt:
                # Wie kann ich unter zuhilfenahme der OpenCV Bibliothek in der Programmiersprache Python, 
                # zwei maskierte Bilder zusammenführen?
                
                # Filtering out red Pixels
                red_seperated_mask_upper, red_seperated_upper = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([140, 0, 0]), 
                    np.array([255, 255, 255])
                )

                red_seperated_mask_lower, red_seperated_lower = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([0, 0, 0]), 
                    np.array([3, 255, 255])
                )
                red_seperated = cv2.add(red_seperated_upper, 
                                        red_seperated_lower)
                
                # https://medium.com/featurepreneur/performing-bitwise-operations-on-images-using-opencv-6fd5c3cd72a7
                # Adding the black pixels from the mask_lower to the color_mask, to
                # remove the other colored areas.
                red_mask = cv2.bitwise_and(color_seperated_mask, red_seperated_mask_lower)
                # Adding the white pixels from the upper mask to get the full 
                # color spectrum of red.
                red_mask = cv2.bitwise_or(red_mask, red_seperated_mask_upper)
                
                # Opening and Closing again on the seperated image to get rid of the flickering
                _, red_seperated = alg.colorSegmentation(
                    red_seperated, 5,
                    np.array([0, 0, 0]), 
                    np.array([255, 255, 255])
                )
                
                # Filtering out yellow Pixels
                yellow_mask, yellow_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([11, 50, 0]), 
                    np.array([30, 255, 255])
                )

                # Save color-specific masks for later shape detection
                color_masks = { 
                    LegoColor.BLUE: blue_mask, 
                    LegoColor.GREEN: green_mask, 
                    LegoColor.RED: red_mask, 
                    LegoColor.YELLOW: yellow_mask
                }

                # Combine color seperated Images with a divider
                combined = ui.combineImages(np.array([blue_seperated, green_seperated]), 
                                            np.array([red_seperated, yellow_seperated]), 3) 
                
                # Show color seperated Image when enabled
                ui.showImage(combined, 'Color Segmentation', self.imshow_scale, show_color_channels)
                    
                # extracting color-specifc ROIs
                roi_dict = alg.get_color_rois(blue_seperated,
                                              green_seperated,
                                              red_seperated,
                                              yellow_seperated)

                # Converting ROIs into dataclass ColoredShape
                coloredShapes = fileConverter.convertRoiDictIntoColoredShapeList(roi_dict)

                # Filtering out all Shapes with a total pixel Count of 750
                coloredShapes = alg.filterShapesByPixelCount(coloredShapes, 750)

                # determining the Shapes positions in the unit square
                coloredShapes = alg.determineShapePositions(coloredShapes, frame_cropped)

                # identifying the Shape Types
                coloredShapes = alg.determineShapeTypes(coloredShapes, color_masks)

                # Write Shape-informations to the console
                consoleWriter.writeShapeListToConsole(coloredShapes)

                # Draw bounding boxes around ROIs
                frame_marked = ui.drawBBoxes(frame_cropped, coloredShapes, [0,255,0], 2)

                # Draw Shape Positions
                frame_marked = ui.drawBBoxCenters(frame_marked, coloredShapes, [0,255,0], 2, 10)

                # Draw Shape Information above BBoxes
                frame_marked = ui.drawInfo(frame_marked, coloredShapes, [0,255,0], 2) 
                    
                # Show Result when enabled
                ui.showImage(frame_marked, 'Result', self.imshow_scale, show_result)
                    
                # Quit on User keydown
                key = cv2.waitKey(refresh_rate)
                if key >= 0:
                    break
                
        finally:
            capture.release()
            consoleWriter.loop_active = False
            consoleWriter.writeStatus('Capture closed.')
            cv2.destroyAllWindows()