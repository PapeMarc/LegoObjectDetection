import cv2
import numpy as np
import os
import time
from datetime import datetime, timedelta

from utils import deviceManager
from utils import imageConverter
from utils import ui
from utils import consoleWriter
from models.dataclasses import LegoColor
import models.fileConverter as fileConverter
import models.algorithms as alg

class Program:
    
    def __init__(self, args):
        # Clear the console
        os.system('cls')
        
        # Load environment values
        self.default_refresh_rate = int(args[0]['DEF_REFRESH_RATE'])
        self.max_refresh_rate = int(args[0]['MAX_REFRESH_RATE'])
        self.min_refresh_rate = int(args[0]['MIN_REFRESH_RATE'])
        self.device_width = float(args[0]['CAMERA_WIDTH'])
        self.device_height = float(args[0]['CAMERA_HEIGHT'])
        self.imshow_scale = float(args[0]['IMSHOW_SCALE'])
        self.capture_number = int(args[0]['CAPTURE_NUM'])
        
        # Log program initialization status
        consoleWriter.writeStatus('Program initialized.')

    def exit(self):
        # Check if the capture device is open and release it if necessary
        if self.capture.isOpened():
            # Release the capture device
            self.capture.release()
            
        # Close all OpenCV windows
        cv2.destroyAllWindows()

        # Log program exit status
        consoleWriter.writeStatus('Program exited.')

        # Terminate the program
        exit()

    def main(self):
        
        # Create the Control Panel window and set its size
        cv2.namedWindow('Control Panel')
        cv2.resizeWindow('Control Panel', 600, 225)
        
        # Create trackbars for user interaction in the Control Panel
        cv2.createTrackbar('Refresh Rate','Control Panel', 
                           int(self.default_refresh_rate / 100), 
                           int(self.max_refresh_rate / 100), 
                           lambda placeholder: None)
        cv2.createTrackbar('Console','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Original','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Colors','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Channels','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Result','Control Panel', 1, 1, lambda placeholder: None)
        
        try:
            
            # Use the CAP_DSHOW Windows Backend to locate the video capture
            # device when no fast refresh rate is required
            fast_mode = self.min_refresh_rate >= 100
            
            # Initialize the video capture device
            self.capture = deviceManager.getVideoCapture(self.capture_number, self.device_width, self.device_height, fast_mode)

            # Initialize variables for execution timing and refresh rate
            last_exec = None
            refresh_rate = self.default_refresh_rate
            refresh_rate_timedelta = timedelta(milliseconds=refresh_rate)

            # Running through Frames
            while True:
                
                # Set the initial execution timestamp if not already set
                if last_exec is None:
                    last_exec = datetime.now()
                    consoleWriter.writeStatus('Initial execution.')
                
                # Calculate the time difference since the last execution
                exec_diff = datetime.now() - last_exec
                
                # Wait if the refresh rate interval has not yet passed
                if exec_diff < refresh_rate_timedelta:
                    # Time to wait before the next frame
                    time_to_sleep = refresh_rate_timedelta - exec_diff
                    time.sleep(time_to_sleep.total_seconds())
                    continue # Skip to the next iteration after waiting
                else:
                    # Update the timestamp for the current execution
                    last_exec = datetime.now()
                
                # Capture a frame from the video stream
                frameAvailable, frame = self.capture.read()

                # Check if a frame is available; exit loop if not
                if not frameAvailable:
                    consoleWriter.writeError('Frame not available.')
                    break
                
                # Reading Trackbar Values
                refresh_rate = cv2.getTrackbarPos('Refresh Rate','Control Panel') * 100
                refresh_rate_timedelta = timedelta(milliseconds=refresh_rate)
                show_console = cv2.getTrackbarPos('Console','Control Panel') == 1
                show_original = cv2.getTrackbarPos('Original','Control Panel') == 1
                show_color_separated = cv2.getTrackbarPos('Colors','Control Panel') == 1
                show_color_channels = cv2.getTrackbarPos('Channels','Control Panel') == 1
                show_result = cv2.getTrackbarPos('Result','Control Panel') == 1

                # Ensure refresh rate is not zero; set to minimum refresh rate if needed
                if refresh_rate == 0:
                    refresh_rate = self.min_refresh_rate
                    refresh_rate_timedelta = timedelta(milliseconds=refresh_rate)

                # Cropping the frame to the largest possible inner square
                frame_cropped = imageConverter.getImageCenterSquare(frame)
                
                # Showing the original image if the option is enabled
                ui.showImage(frame_cropped, 'Original', self.imshow_scale, show_original)

                # Separating colors from the background using color segmentation with 
                # morphological operations (opening and closing)
                color_separated_mask, color_separated = alg.colorSegmentation(
                    frame_cropped, 5,
                    np.array([0, 75, 0]), 
                    np.array([255, 255, 255])
                )
                
                # Showing the color-separated image if enabled
                ui.showImage(color_separated, 'Color seperated', self.imshow_scale, show_color_separated)

                # Using color-specific segmentation
                # Filtering out blue pixels
                blue_mask, blue_seperated = alg.colorSegmentation(
                    color_separated, 3,
                    np.array([100, 100, 0]), 
                    np.array([170, 255, 255])
                )
                # Filtering out green pixels
                green_mask, green_seperated = alg.colorSegmentation(
                    color_separated, 3,
                    np.array([50, 27, 0]), 
                    np.array([100, 255, 131])
                )
                
                # Filtering out red pixels (upper range)
                red_seperated_mask_upper, red_seperated_upper = alg.colorSegmentation(
                    color_separated, 1,
                    np.array([140, 0, 0]), 
                    np.array([255, 255, 255])
                )

                # Filtering out red pixels (lower range)
                red_seperated_mask_lower, red_seperated_lower = alg.colorSegmentation(
                    color_separated, 1,
                    np.array([0, 0, 0]), 
                    np.array([10, 255, 255])
                )
                # Combining the upper and lower red segments to form the complete red-separated image
                red_seperated = cv2.add(red_seperated_upper, 
                                        red_seperated_lower)
                
                # Adding the black pixels from the lower mask to the color mask
                # to remove other colored areas
                red_mask = cv2.bitwise_and(color_separated_mask, red_seperated_mask_lower)
                # Adding the white pixels from the upper mask to include the full 
                # color spectrum of red
                red_mask = cv2.bitwise_or(red_mask, red_seperated_mask_upper)
                
                # Applying morphological operations (opening and closing) on the 
                # separated red image to reduce flickering
                _, red_seperated = alg.colorSegmentation(
                    red_seperated, 5,
                    np.array([0, 0, 0]), 
                    np.array([255, 255, 255])
                )
                
                # Filtering out yellow pixels using color segmentation
                yellow_mask, yellow_seperated = alg.colorSegmentation(
                    color_separated, 3,
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

                # Combine color-separated images with a divider for visualization
                combined = ui.combineImages(np.array([blue_seperated, green_seperated]), 
                                            np.array([red_seperated, yellow_seperated]), 3) 
                
                # Show the combined color-separated image if the option is enabled
                ui.showImage(combined, 'Color Segmentation', self.imshow_scale, show_color_channels)
                    
                # Extract color-specific regions of interest (ROIs) for further processing
                roi_dict = alg.get_color_rois(blue_seperated,
                                              green_seperated,
                                              red_seperated,
                                              yellow_seperated)

                # Converting ROIs into dataclass ColoredShape
                coloredShapes = fileConverter.convertRoiDictIntoColoredShapeList(roi_dict)

                # Filtering out all shapes with a total pixel count below 750
                coloredShapes = alg.filterShapesByPixelCount(coloredShapes, 750)

                # Determining the shapes' positions in the unit square
                coloredShapes = alg.determineShapePositions(coloredShapes, frame_cropped)

                # Identifying the shape types based on color-specific masks
                coloredShapes = alg.determineShapeTypes(coloredShapes, color_masks)

                # Write shape information to the console
                console_height, console_width = 500, 900
                # Create a blank console image
                console_image = np.zeros((console_height, console_width, 3), dtype=np.uint8)
                console_image = consoleWriter.writeShapeListToConsole(coloredShapes, show_console, console_image)
                ui.showImage(console_image, 'Console', 1, show_console)

                # Draw bounding boxes around ROIs
                frame_marked = ui.drawBBoxes(frame_cropped, coloredShapes, [0,255,0], 2)

                # Draw shape positions as centers of bounding boxes
                frame_marked = ui.drawBBoxCenters(frame_marked, coloredShapes, [0,255,0], 2, 10)

                # Draw shape information (ID) above bounding boxes
                frame_marked = ui.drawInfo(frame_marked, coloredShapes, [0,255,0], 2) 
                    
                # Show the final result if enabled
                ui.showImage(frame_marked, 'Result', self.imshow_scale, show_result)
                    
                # Quit on user keydown
                key = cv2.waitKey(1)
                if key >= 0:
                    break
                
        finally:
            # Release the video capture device
            self.capture.release()
            
            # Notify the console writer that the loop is no longer active
            consoleWriter.loop_active = False

            # Log that the capture has been closed
            consoleWriter.writeStatus('Capture closed.')
            
            # Close all OpenCV windows
            cv2.destroyAllWindows()