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
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (648*2, 486*2)}))
# picam2.configure(preview_config)

picam2.start()


while True:
    
    image = picam2.capture_array()
    
    
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve circle detection
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, dp=1, minDist=1, param1=50, param2=70
                               , minRadius=10, maxRadius=1000)

    # Ensure circles were found
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        # Calculate frequency of each center for the pipe
        in_center_counts = {}
        out_center_counts = {}
        
        # Separate inner and outer circles
        inner_circles = []
        outer_circles = []
            
        for (x, y, r) in circles:
            center = (x, y)
                
            # Calculate the average intensity within the circle
            mean_intensity = np.mean(gray[y - r:y + r, x - r:x + r])
        
            # If the intensity is lower, consider it as an inner circle (dark pipe)
            if mean_intensity < 45 :
                inner_circles.append((x, y, r))
                if center in in_center_counts:
                    in_center_counts[center] += 1
                else:
                    in_center_counts[center] = 1
            else:
                outer_circles.append((x, y, r))
                if center in out_center_counts:
                    out_center_counts[center] += 1
                else:
                    out_center_counts[center] = 1

        # Find the most common center
        if in_center_counts != {} :
            most_common_in_center = max(in_center_counts, key=in_center_counts.get)
            for (x, y, r) in inner_circles:
                cv2.circle(blur, (x, y), r, (0, 255, 0), 4)
                if in_center_counts[(x, y)]>1:
                    print((x, y),in_center_counts[(x, y)])
                if (x, y) == most_common_in_center and in_center_counts[(x, y)]>1:
                    print(most_common_in_center)
                    # Draw circle with the most common center for the pipe
                    diameter = r*2
                    diameter_cm = (diameter / 1296) * 20.48
                    cv2.putText(blur, f"Diameter: {diameter_cm:.2f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    break
            
        
        if out_center_counts !={} :
            most_common_out_center = max(out_center_counts, key=out_center_counts.get)
            for (x, y, r) in outer_circles:
                cv2.circle(blur, (x, y), r, (255, 0, 0), 4)
                if out_center_counts[(x, y)]>1:
                    print((x, y),out_center_counts[(x, y)])
                if (x, y) == most_common_out_center and out_center_counts[(x, y)]>1:
                    print(most_common_out_center)
                    # Draw circle with the most common center for the pipe
                    diameter = r*2
                    diameter_cm = (diameter / 1296) * 20.48
                    cv2.putText(blur, f"Diameter: {diameter_cm:.2f} cm", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    break
    
    # Show the detected circles
    cv2.imshow("Detected Circles", blur)

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord('q'):
        break

# Release the VideoCapture object and close all windows
picam2.stop_preview()
cv2.destroyAllWindows()


