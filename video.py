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


while True:
    
    image = picam2.capture_array()
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve circle detection
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, dp=1, minDist=1, param1=20, param2=40, minRadius=10, maxRadius=1000)

    # Ensure circles were found
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
    
        # Separate inner and outer circles
        inner_circles = []
        outer_circles = []
    
        for (x, y, r) in circles:
            # Calculate the average intensity within the circle
            mean_intensity = np.mean(gray[y - r:y + r, x - r:x + r])
        
            # If the intensity is lower, consider it as an inner circle (dark pipe)
            if mean_intensity < 55:
                inner_circles.append((x, y, r))
            else:
                outer_circles.append((x, y, r))
    
        # Draw circles on the original image
        for (x, y, r) in inner_circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
        for (x, y, r) in outer_circles:
            cv2.circle(image, (x, y), r, (255, 0, 0), 4)
    
    # Show the detected circles
    cv2.imshow("Detected Circles", image)
    
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord('q'):
        break

# Release the VideoCapture object and close all windows
picam2.stop_preview()
cv2.destroyAllWindows()
