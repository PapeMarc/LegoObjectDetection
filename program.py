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
    def __init__(self):
        os.system("cls")
        print("\nProgram initialized.\n")

    def exit(self):
        print(f"\nProgram exited.\n")
        exit()

    def main(self, args):

        cv2.namedWindow('Control Panel')
        cv2.resizeWindow('Control Panel', 600, 200)
        cv2.createTrackbar('Refresh Rate','Control Panel', 
                           int(int(args[0]['DEF_REFRESH_RATE']) / 100), 
                           int(int(args[0]['MAX_REFRESH_RATE']) / 100), 
                           lambda placeholder: None)
        cv2.createTrackbar('Win_O','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Win_CS','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Win_CC','Control Panel', 0, 1, lambda placeholder: None)
        cv2.createTrackbar('Win_R','Control Panel', 1, 1, lambda placeholder: None)
        
        min_refresh_rate = int(args[0]['MIN_REFRESH_RATE'])

        try:
            capture = deviceManager.getVideoCapture(1)

            capture.set(cv2.CAP_PROP_FRAME_WIDTH, float(args[0]['CAMERA_WIDTH']))
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, float(args[0]['CAMERA_HEIGHT']))
            imshow_scale = float(args[0]['IMSHOW_SCALE'])

            while True:
                frameAvailable, frame = capture.read()
                if not frameAvailable:
                    print("Frame not available.")
                    break

                # Get Trackbar Values
                refresh_rate = cv2.getTrackbarPos('Refresh Rate','Control Panel') * 100
                if refresh_rate == 0:
                    refresh_rate = min_refresh_rate

                show_original = cv2.getTrackbarPos('Win_O','Control Panel') == 1
                show_color_seperated = cv2.getTrackbarPos('Win_CS','Control Panel') == 1
                show_color_channels = cv2.getTrackbarPos('Win_CC','Control Panel') == 1
                show_result = cv2.getTrackbarPos('Win_R','Control Panel') == 1

                # Cropping the Image to a Square
                frame_cropped = imageConverter.getImageCenterSquare(frame)
                if show_original:
                    cv2.imshow("Original", imageConverter.resizeImage(frame_cropped, imshow_scale))
                elif cv2.getWindowProperty("Original", cv2.WND_PROP_VISIBLE) > 0:
                    cv2.destroyWindow("Original")  

                # Opening and Closing for replacing pixels 
                # with a Saturation below 70 with black
                _, color_seperated = alg.colorSegmentation(
                    frame_cropped, 5,
                    np.array([0, 75, 0]), 
                    np.array([255, 255, 255])
                )
                if show_color_seperated:
                    cv2.imshow("Color seperated", imageConverter.resizeImage(color_seperated, imshow_scale))
                elif cv2.getWindowProperty("Color seperated", cv2.WND_PROP_VISIBLE) > 0:
                    cv2.destroyWindow("Color seperated")  

                # Using color specific Segmentation for later identifying the ROIs
                blue_mask, blue_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([105, 100, 0]), 
                    np.array([170, 255, 255])
                )
                green_mask, green_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([50, 27, 0]), 
                    np.array([100, 255, 131])
                )

                # Perplexity AI gefragt:
                # Wie kann ich unter zuhilfenahme der OpenCV Bibliothek in der Programmiersprache Python, 
                # zwei von maskierte Bilder zusammenführen?
                _, red_seperated_hue_upper = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([140, 0, 0]), 
                    np.array([255, 255, 255])
                )
                _, red_seperated_hue_lower = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([0, 0, 0]), 
                    np.array([3, 255, 255])
                )
                red_seperated = cv2.add(red_seperated_hue_upper, 
                                        red_seperated_hue_lower)
                
                # Opening and Closing again on the seperated image to get rid of the flickering
                red_mask, red_seperated = alg.colorSegmentation(
                    red_seperated, 5,
                    np.array([0, 0, 0]), 
                    np.array([255, 255, 255])
                )


                yellow_mask, yellow_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([11, 50, 0]), 
                    np.array([30, 255, 255])
                )

                color_masks = {LegoColor.BLUE: blue_mask, LegoColor.GREEN: green_mask, 
                         LegoColor.RED: red_mask, LegoColor.YELLOW: yellow_mask}

                combined = ui.combineImages(np.array([blue_seperated, green_seperated]), 
                                    np.array([red_seperated, yellow_seperated]), 3) 
                if show_color_channels:
                    cv2.imshow("Color Segmentation", imageConverter.resizeImage(combined, imshow_scale))
                elif cv2.getWindowProperty("Color Segmentation", cv2.WND_PROP_VISIBLE) > 0:
                    cv2.destroyWindow("Color Segmentation")  
                    
                # extracting the color-specifc ROIs
                roi_dict = alg.get_color_rois(blue_seperated,
                                            green_seperated,
                                            red_seperated,
                                            yellow_seperated)

                # Converting ROIs into dataclass ColoredShape
                shapes = fileConverter.convertRoiDictIntoShapeList(roi_dict)

                # Filtering out all Shapes with a total pixel Count of 300
                shapes = alg.filterShapesByPixelCount(shapes, 300)

                # determining the Shapes positions in the unit square
                shapes = alg.determineShapePositions(shapes, frame_cropped)

                # identifying the Shape Types
                shapes = alg.determineShapeTypes(shapes, frame_cropped, color_masks)

                # Write Shape-informations to the console
                consoleWriter.writeShapeListToConsole(shapes)

                # Draw bounding boxes around ROIs
                frame_marked = ui.drawBoundingBoxes(frame_cropped, shapes, [0,255,0], 2)

                # Draw Shape Positions
                frame_marked = ui.drawBBoxCenters(frame_marked, shapes, [0,255,0], 2, 10)

                #cv2.putText(
                #    image, f"{coloredShape.color}, {coloredShape.shapeType}", 
                #    (x, y-20), 
                #    cv2.FONT_ITALIC, 
                #    0.8, 
                #    ui_color, ui_thickness
                #)
                
                if show_result:
                    cv2.imshow('Result', imageConverter.resizeImage(frame_marked, imshow_scale))
                elif cv2.getWindowProperty("Result", cv2.WND_PROP_VISIBLE) > 0:
                    cv2.destroyWindow("Result")  
                    
                key = cv2.waitKey(refresh_rate)
                if key >= 0:
                    break
        finally:
            capture.release()
            print("Capture closed.")
            cv2.destroyAllWindows()