# Lego Object Detection  

This project enables **real-time detection of LEGO bricks in a live camera feed**.  
Using **OpenCV**, colors and shapes are segmented, classified, and displayed visually.  

## Features  
- Live video capture from a connected camera  
- Color segmentation for LEGO colors: **Blue, Green, Red, Yellow**  
- Shape and size analysis to distinguish different LEGO brick types:  
  - 1x3, 1x4, 2x2, 2x4  
- ROI extraction (Region of Interest) with bounding boxes  
- Console with real-time object overview (incl. position & rotation angle)  
- Template matching for more accurate classification (optional)  
- Control panel with trackbars to adjust:  
  - Refresh rate  
  - Display of original frame, color segmentation, channels, and results  

## Project Structure  
```
├── main.py                # Entry point of the program
├── program.py             # Main loop (camera, segmentation, UI)
├── algorithms.py          # Color and shape algorithms
├── algorithms_tm.py       # Template matching algorithms
├── dataclasses.py         # Definition of LEGO colors, shapes, and data structures
├── fileConverter.py       # Helper functions to convert ROIs
├── consoleWriter.py       # Console output & logging
├── deviceManager.py       # Camera handling
├── imageConverter.py      # Image transformations (HSV, cropping, ROI)
├── ui.py                  # Visualization, bounding boxes, overlays
├── .env                   # Project configuration (e.g. camera settings)
```

## Installation  

### Requirements  
- Python 3.9+  
- Installed dependencies (OpenCV, NumPy, python-dotenv)  

### Setup  
1. Clone the repository:  
   ```bash
   git clone https://github.com/PapeMarc/LegoObjectDetection.git
   cd LegoObjectDetection
   ```
2. Create and activate a virtual environment (optional but recommended).  
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
4. Create and configure a `.env` file (example):  
   ```
   PROJECT_DIR=C:/Users/.../LegoObjectDetection
   CAMERA_WIDTH=640
   CAMERA_HEIGHT=480
   DEF_REFRESH_RATE=200
   MIN_REFRESH_RATE=100
   MAX_REFRESH_RATE=1000
   IMSHOW_SCALE=1
   CAPTURE_NUM=0
   ```

## Usage  
Run the project with:  
```bash
python main.py
```

You will see:  
- A **Control Panel** with trackbars  
- Windows for the original frame, color analysis, results, and console  

The trackbars allow you to control which outputs are visible and the refresh rate.  

## Possible Extensions  
- Support for additional LEGO colors and brick types  
- Save detection results to files (CSV, JSON)  
- Train a machine learning model for improved recognition  
