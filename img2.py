import cv2
import numpy as np
from sklearn.cluster import DBSCAN


# Load image
image = cv2.imread('image.png', cv2.IMREAD_COLOR)


# Convert image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply GaussianBlur to reduce noise and improve circle detection
blur = cv2.GaussianBlur(gray, (9, 9), 2)

# Detect circles using Hough Circle Transform
circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, dp=1, minDist=1, param1=20, param2=50, minRadius=10, maxRadius=1000)

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
        if mean_intensity < 40:
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
            if in_center_counts[(x, y)]>1:
                print((x, y),in_center_counts[(x, y)])
            if (x, y) == most_common_in_center and in_center_counts[(x, y)]>1:
                print(most_common_in_center)
                # Draw circle with the most common center for the pipe
                cv2.circle(image, (x, y), r, (0, 255, 0), 4)
                break
                
        
    if out_center_counts !={} :
        most_common_out_center = max(out_center_counts, key=out_center_counts.get)
        for (x, y, r) in outer_circles:
            if out_center_counts[(x, y)]>1:
                print((x, y),out_center_counts[(x, y)])
            if (x, y) == most_common_out_center and out_center_counts[(x, y)]>1:
                print(most_common_out_center)
                # Draw circle with the most common center for the pipe
                cv2.circle(image, (x, y), r, (255, 0, 0), 4)
                break
                
    # Show the detected circles
    cv2.imshow("Detected Circles", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No circles detected.")
