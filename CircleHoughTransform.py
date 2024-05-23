#!/usr/bin/python3

import cv2
import numpy as np
from picamera2 import Picamera2

# Function to adjust brightness and contrast
def adjust_brightness_contrast(image, alpha=1.3, beta=40):
    """
    Adjusts the brightness and contrast of the image.
    :param image: Input image
    :param alpha: Contrast control (1.0-3.0)
    :param beta: Brightness control (0-100)
    :return: Adjusted image
    """
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1296, 972)}))
picam2.start()

while True:
    # Capture a frame
    frame = picam2.capture_array()

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply binary thresholding
    # _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    adjusted_frame = adjust_brightness_contrast(gray, alpha=3.0, beta=100)

    # Apply edge detection using Canny
    edges = cv2.Canny(adjusted_frame, 50, 150)

    # Detect circles using Hough Circle Transform
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=3, minDist=20, param1=1, param2=500, minRadius=10, maxRadius=1000)

    # If circles are detected
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            # Draw the circle in the output image
            cv2.circle(frame, (x, y), r, (0, 255, 0), 4)

    # Display the original frame with detected circles
    cv2.imshow("Detected Circles on Frame", frame)
    # Display the edge-detected image with detected circles
    cv2.imshow("Detected Circles on Edges", edges)

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
