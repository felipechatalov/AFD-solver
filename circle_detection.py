import cv2
import numpy as np

import os

IMG_TEST_FOLDER = "images/"

WIDTH_CAP = 1635
HEIGHT_CAP = 920
def try_resize_to_fit_screen(img):
    if img.shape[0] > WIDTH_CAP or img.shape[1] > HEIGHT_CAP:
        h_proportion = img.shape[0] / img.shape[1]
        w_proportion = img.shape[1] / img.shape[0]

        h = img.shape[0]
        w = img.shape[1]


        while w > WIDTH_CAP:
            w -= 1
            h -= h_proportion
        
        while h > HEIGHT_CAP:
            h -= 1
            w -= w_proportion
        
        h = int(h)
        w = int(w)

        print('Resizing image to fit screen: {}x{} -> {}x{}'.format(img.shape[0], img.shape[1], h, w))

        img = cv2.resize(img, (w, h))
    return img

def test_data():
    for file in os.listdir(os.path.join(os.getcwd(), IMG_TEST_FOLDER)):
        
        img = cv2.imread(os.path.join(os.getcwd(), IMG_TEST_FOLDER, file), cv2.IMREAD_GRAYSCALE)
        
        img_preprocess = pre_process(img)
        img_circles = detect_circles(img_preprocess)

        big_img = np.concatenate((img, img_preprocess, img_circles), axis=1)

        cv2.imshow(file, try_resize_to_fit_screen(big_img))
        # checks if any key was pressed or the 'X' button in the window was pressed
        while cv2.getWindowProperty(file, cv2.WND_PROP_VISIBLE) > 0:
            if cv2.waitKey(100) > 0:
                break
        cv2.destroyAllWindows()

def pre_process(img):
    # remove noise
    #img = cv2.medianBlur(img, 5)

    # increase contrast
    img = cv2.addWeighted(img, 2.0, np.zeros(img.shape, img.dtype), 0, 25) 

    # another way to increase contrast
    #img = cv2.equalizeHist(img)

    # yet another way to increase contrast
    img = cv2.convertScaleAbs(img, alpha=1.5, beta=10)

    # threshold the image
    # below 230 is black, above 230 is white
    img = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY)[1]

    # more blur
    #img2 = cv2.GaussianBlur(img2, (5, 5), 0)
    
    return img

def detect_circles(img):
    # detect circles    
    output = img.copy()
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=0.7, minDist=30, param1=25, param2=25, maxRadius=100, minRadius=10)

    # if we find circles we draw them on top of the copy of the image
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        print(circles)
        for (x, y, r) in circles:
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
    return output

def main():

    test_data()



main()