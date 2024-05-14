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


# Main loop
while True:
    # start_time = time.time()
    
    im = picam2.capture_array()
    
    # Convert frame to grayscale
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    gray_blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
   # Detect circles using HoughCircles
    circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, dp=1, minDist=10,
                               param1=300, param2=35, minRadius=10, maxRadius=1000)
  
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw circle
            cv2.circle(im, (x, y), r, (0, 255, 0), 4)
            
            # Calculate real-world radius
            real_radius = (focal_length * r) / distance_to_object
            
            # Calculate diameter
            diameter = 2 * real_radius 
            
            # Draw diameter text
            cv2.putText(im, f"Diameter: {diameter:.2f} mm", (x - r, y - r - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
            # Edge detection to estimate thickness
            edges = cv2.Canny(gray, 50, 150)
            # Find contours
            contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # Filter contours that are approximately circular and close to the circle
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 10:  # Skip small contours
                    continue
                # Fit a circle to the contour
                (x_contour, y_contour), radius_contour = cv2.minEnclosingCircle(contour)
                # Check if the contour is close to the detected circle
                if abs(radius_contour - r) < 5:  # Adjust this threshold as needed
                    # Calculate thickness as the difference between the two radii
                    thickness = abs(r - radius_contour)
                    # Convert thickness to centimeters
                    thickness_cm = thickness / 10  # Convert from mm to cm
                    # Draw thickness text
                    cv2.putText(im, f"Thickness: {thickness_cm:.2f} cm", (x - r, y + r + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    break  # Assuming only one contour matches the criteria
    
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
