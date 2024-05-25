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

    # Adjust brightness and contrast

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    adjusted_frame = adjust_brightness_contrast(gray, alpha=3.0, beta=0)

    # Apply GaussianBlur to reduce noise and improve circle detection
    blur = cv2.GaussianBlur(adjusted_frame, (9, 9), 2)



    # Apply binary thresholding
    # _, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

    # Apply edge detection using Canny
    edges = cv2.Canny(blur, 50, 150)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    i = 0
    in_dm = 0
    out_dm = 0
    for contour in contours:
        # Fit an ellipse to the contour if there are enough points
        if len(contour) >= 400:
            i=i+1
            ellipse = cv2.fitEllipse(contour)
            (x, y), (major_axis, minor_axis), angle = ellipse

            # Calculate and display ovality
            ovality = major_axis / minor_axis
            
            if ovality<0.8:
                continue

            # Draw the ellipse
            cv2.ellipse(frame, ellipse, (0, 255, 0), 2)

            diameter_cm = (minor_axis / 1296) * 20.48

            if i==1:
                cv2.putText(frame, f"Diameter: {diameter_cm:.2f}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
                in_dm = diameter_cm
            else:
                if in_dm>diameter_cm:
                    out_dm = in_dm
                    in_dm = diameter_cm
                else:
                    out_dm = diameter_cm

                thinkness = out_dm-in_dm

                if thinkness > 0.2:
                    cv2.putText(frame, f"inner Diameter: {in_dm:.2f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"outer Diameter: {out_dm:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"Thickness: {thinkness:.2f}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 1, cv2.LINE_AA)
                else:
                    i=i-1
                    out_dm = 0

            cv2.putText(frame, f"Ovality: {ovality:.2f}", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)



    # Display the original frame with detected ellipses and ovality
    cv2.imshow("Detected Ellipses", frame)
    cv2.imshow("Detected2", edges)
    cv2.imshow("Detected1", blur)
    cv2.imshow("Detected0", adjusted_frame)



    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cv2.destroyAllWindows()
picam2.stop()
