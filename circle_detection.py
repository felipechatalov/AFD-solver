import cv2
import numpy as np
# https://www.tensorflow.org/guide/keras/training_with_built_in_methods

img = cv2.imread("caderno4.jpeg")
output = img.copy()
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# image input, mothod, 
# how it was
# circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=0.7, minDist=19, param1=30, param2=50, maxRadius=100, minRadius=10)
circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=0.7, minDist=19, param1=30, param2=50, maxRadius=100, minRadius=10)

if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    print(circles)

    for (x, y, r) in circles:
        cv2.circle(output, (x, y), r, (0, 255, 0), 2)



cv2.imshow("Image", output)
# checks if any key was pressed or the 'X' button in the window was pressed
while cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) > 0:
    if cv2.waitKey(100) > 0:
        break
cv2.destroyAllWindows()
