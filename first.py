#!/usr/bin/python3

# Normally the QtGlPreview implementation is recommended as it benefits
# from GPU hardware acceleration.

import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview

cv2.startWindowThread()

picam2 = Picamera2()

# preview_config = picam2.create_preview_configuration()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1296, 972)}))
# picam2.configure(preview_config)

picam2.start()

# Constants
focal_length = 3.04  # mm
distance_to_object = 500  # mm (0.5 meter)


# Set desired frame rate (fps)
# desired_fps = 1
# interval = 1.0 / desired_fps

while True:
    
    # Record start time
#     start_time = time.time()
    
    im = picam2.capture_array()
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
   # Detect circles using HoughCircles
    circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=200, param2=30, minRadius=10, maxRadius=500)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(im, (x, y), r, (0, 255, 0), 4)

    
    cv2.imshow("Camera", im)
    
    # Wait for the remaining time to meet the desired fps
#     elapsed_time = time.time() - start_time
#     remaining_time = interval - elapsed_time
#     if remaining_time > 0:
#         time.sleep(remaining_time)

    
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord('q'):
        break

# Release the VideoCapture object and close all windows
picam2.stop_preview()
cv2.destroyAllWindows()