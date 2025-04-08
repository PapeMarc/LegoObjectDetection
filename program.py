import cv2
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
        import os
        os.system("cls")
        print("\nProgram initialized.\n")

    def exit(self):
        print(f"\nProgram exited.\n")
        exit()

    def main(self, args):

        try:
            capture = deviceManager.getVideoCapture(0)

            while True:
                frameAvailable, frame = capture.read()
                if not frameAvailable:
                    print("Frame not available.")
                    break

                # Cropping the Image to a Square
                frame_cropped = imageConverter.getImageCenterSquare(frame)
                cv2.imshow("Original", frame_cropped)

                # Opening and Closing for replacing pixels 
                # with a Saturation below 70 with black
                color_seperated = alg.colorSegmentation(
                    frame_cropped, 5,
                    np.array([0, 75, 0]), 
                    np.array([255, 255, 255])
                )
                cv2.imshow("Color seperated", color_seperated)

                # Using color specific Segmentation for later identifying the ROIs
                blue_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([105, 100, 0]), 
                    np.array([170, 255, 255])
                )
                green_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([50, 27, 0]), 
                    np.array([100, 255, 131])
                )

                # Perplexity AI gefragt:
                # Wie kann ich unter zuhilfenahme der OpenCV Bibliothek in der Programmiersprache Python, 
                # zwei von maskierte Bilder zusammenführen?
                red_seperated_hue_upper = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([140, 0, 0]), 
                    np.array([255, 255, 255])
                )
                red_seperated_hue_lower = alg.colorSegmentation(
                    color_seperated, 1,
                    np.array([0, 0, 0]), 
                    np.array([3, 255, 255])
                )
                red_seperated = cv2.add(red_seperated_hue_upper, 
                                        red_seperated_hue_lower)
                
                # Opening and Closing again on the seperated image to get rid of the flickering
                red_seperated = alg.colorSegmentation(
                    red_seperated, 5,
                    np.array([0, 0, 0]), 
                    np.array([255, 255, 255])
                )


                yellow_seperated = alg.colorSegmentation(
                    color_seperated, 3,
                    np.array([11, 50, 0]), 
                    np.array([30, 255, 255])
                )

                combined = ui.combineImages(np.array([blue_seperated, green_seperated]), 
                                    np.array([red_seperated, yellow_seperated]), 3) 
                cv2.imshow("Color Segmentation", combined)

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
                shapes = alg.determineShapeTypes(shapes, frame_cropped)

                # Write Shape-informations to the console
                consoleWriter.writeShapeListToConsole(shapes)

                # Draw bounding boxes around ROIs
                frame_marked = ui.drawBoundingBoxes(frame_cropped, shapes, [0,255,0], 1)

                # Draw Shape Positions
                frame_marked = ui.drawBBoxCenters(frame_marked, shapes, [0,255,0], 1, 7)

                #cv2.putText(
                #    image, f"{coloredShape.color}, {coloredShape.shapeType}", 
                #    (x, y-20), 
                #    cv2.FONT_ITALIC, 
                #    0.8, 
                #    ui_color, ui_thickness
                #)

                cv2.imshow('Result', frame_marked)



                key = cv2.waitKey(1000)
                if key >= 0:
                    break
        finally:
            capture.release()
            print("Capture closed.")
            cv2.destroyAllWindows()