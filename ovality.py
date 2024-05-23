import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview

cv2.startWindowThread()

picam2 = Picamera2()

picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1296, 972)}))

picam2.start()

while True:
    image = picam2.capture_array()

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve circle detection
    blur = cv2.GaussianBlur(gray, (9, 9), 2)

    # Draw an oval using the edges of the leftmost and rightmost inner circles
    cv2.ellipse(image, ((left_circle[0] + right_circle[0]) // 2, (left_circle[1] + right_circle[1]) // 2),
                ((right_circle[0] - left_circle[0]) // 2, right_circle[2]),
                0, 0, 360, (0, 255, 0), 4)

    # Show the detected circles
    cv2.imshow("Detected Circles", image)
    time.sleep(1)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord('q'):
        break

# Release the VideoCapture object and close all windows
picam2.stop_preview()
cv2.destroyAllWindows()
