'''
-  x for abort readings and close the program
-  q for quit program in preview
-  r for start capturing readings after setting pipe in preview
'''

import cv2
import csv
import os
from collections import Counter
from picamera2 import Picamera2

window_and_detection_width = 1296 # max 3280 
window_and_detection_height = 972 # max 2464
distance_from_camare = 20.48

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

def filtered_image(frame):

    # Adjust brightness and contrast
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    adjusted_frame = adjust_brightness_contrast(gray, alpha=3.0, beta=0)

    # Apply GaussianBlur to reduce noise and improve circle detection
    blur = cv2.GaussianBlur(adjusted_frame, (9, 9), 2)

    # Apply edge detection using Canny
    edges = cv2.Canny(blur, 50, 150)

    return edges

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (window_and_detection_width, window_and_detection_height)}))
picam2.start()

while True:

    if os.path.exists('readings.csv'):

        # Open the file in read mode first to count existing rows

        with open('readings.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            index = sum(1 for row in reader)  # Count existing rows
    
    else:
        index = 1

    inner_diameters = []
    outer_diameters = []
    
    inner_ovals_ovality = []
    outer_ovals_ovality = []

    thicknesses = []
    readings = []
    readings_count = 0

    while True:

        # Capture a frame
        frame = picam2.capture_array()

        # Find contours in the edge-detected image
        contours, _ = cv2.findContours(filtered_image(frame), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        i = 0

        in_dm = 0
        out_dm = 0

        in_o = 0
        out_o = 0

        should_continue = False
        skip = False

        while True:
            main_i=0
            for contour in contours:
                main_i += 1
                # Fit an ellipse to the contour if there are enough points
                if len(contour) >= 400:
                    pre_view = frame
                    ellipse = cv2.fitEllipse(contour)
                    (x, y), (major_axis, minor_axis), angle = ellipse

                    # Calculate and display ovality
                    ovality = major_axis / minor_axis
                    
                    if ovality < 0.8:
                        continue

                    i += 1

                    # Draw the ellipse
                    cv2.ellipse(pre_view, ellipse, (0, 255, 0), 2)
                    print("main")

                    diameter_cm = (minor_axis / window_and_detection_width) * distance_from_camare
                    cv2.putText(pre_view, f"Ovality: {ovality:.2f}", (10, 300+i*50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)
                    if i == 1:
                        in_dm = diameter_cm
                        in_o = ovality
                    else:
                        if in_dm > diameter_cm:

                            out_dm = in_dm
                            in_dm = diameter_cm

                            out_o = in_o
                            in_o = ovality

                        else:
                            out_dm = diameter_cm

                            out_o = ovality

                        thickness = out_dm - in_dm

                        if thickness > 0.2:

                            inner_ovals_ovality.append(in_o)
                            outer_ovals_ovality.append(out_o)

                            inner_diameters.append(in_dm)
                            outer_diameters.append(out_dm)

                            thicknesses.append(thickness)

                            readings.append(str(in_dm)+str(out_dm)+str(thickness))

                            cv2.putText(frame, f"inner Diameter: {in_dm:.2f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)
                            cv2.putText(frame, f"outer Diameter: {out_dm:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1, cv2.LINE_AA)
                            cv2.putText(frame, f"Thickness: {thickness:.2f}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 1, cv2.LINE_AA)
                            should_continue = True
                            print("for")
                            break
                        else:
                            cv2.imshow("Detected Ellipses", pre_view)
                            print("conti")
                            i -= 1
            print("while 2")
            cv2.imshow("Detected Ellipses", frame)

            if should_continue :
                break

            if len(contours) == main_i:
                skip = True
                break
            
        if skip:
            continue

        print("hello",readings_count)

        # Display the original frame with detected ellipses and ovality
        cv2.imshow("Detected Ellipses", frame)

        # Save images
        cv2.imwrite(f"images/image_{readings_count}.jpg", frame)

        readings_count += 1

        # Collect 10 readings
        if readings_count > 20:
            break

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('x'):

            # Release resources
            cv2.destroyAllWindows()
            picam2.stop()
            exit()


    # Save readings to result.csv
    if os.path.exists('readings.csv'):
        mode = 'a'
    else:
        mode = 'w'

    # Save most frequent reading to CSV
    frequent_reading_index = Counter(readings).most_common(1)[0][0]

    with open('readings.csv', mode=mode, newline='') as file:

        writer = csv.writer(file)

        if mode == 'w':
            writer.writerow(['Index','Inner Diameter', 'Outer Diameter','Inner Oval\'s Ovality','Outer Oval\'s Ovality', 'Thickness'])

        for i in range(len(inner_diameters)):
            if readings[i] == frequent_reading_index:
                writer.writerow([index, round(inner_diameters[i], 2), round(outer_diameters[i], 2), round(inner_ovals_ovality[i], 2), round(outer_ovals_ovality[i], 2), round(thicknesses[i], 2)])

    # Move most frequent image to a separate folder
    if not os.path.exists('results'):
        os.makedirs('results')

    frequent_image_index = readings.index(frequent_reading_index)
    os.rename(f"images/image_{frequent_image_index}.jpg", f"results/pipe_{index}.jpg")

    while True:

        frame = picam2.capture_array()

        # Find contours in the edge-detected image
        contours, _ = cv2.findContours(filtered_image(frame), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if len(contour) >= 400:
                ellipse = cv2.fitEllipse(contour)

                (x, y), (major_axis, minor_axis), angle = ellipse

                # Calculate and display ovality
                ovality = major_axis / minor_axis

                if ovality < 0.8:
                    continue

                # Draw the ellipse
                cv2.ellipse(frame, ellipse, (0, 255, 0), 2)
        
        cv2.imshow("Detected Ellipses", frame)

        key = cv2.waitKey(1)
        # Exit on 'q' key press
        if  key & 0xFF == ord('q'):

            # Release resources
            cv2.destroyAllWindows()
            picam2.stop()
            exit()

        if key & 0xFF == ord('r'):
            break