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
    
    im = picam2.capture_array()
    
    
    cv2.imshow("Camera", im)
    # Check if the user pressed the 'q' key to quit
    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        # Save the image as "image.jpg"
        cv2.imwrite('image.jpg', im)
        print("Image saved as 'image.jpg'")

# Release the VideoCapture object and close all windows
picam2.stop_preview()
cv2.destroyAllWindows()
