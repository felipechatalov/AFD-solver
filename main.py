import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

import interface

#from tkinter import Tk

# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html

#ROOT = Tk()

IMG_TEST_FOLDER = "images/"


WIDTH_CAP = 1635
HEIGHT_CAP = 920
def try_resize(img):
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

        #print('Resizing image to fit screen: {}x{} -> {}x{}'.format(img.shape[0], img.shape[1], h, w))

        img = cv2.resize(img, (w, h))
    return img

def show_image(img):
    cv2.imshow("image", try_resize(img))
    # checks if any key was pressed or the 'X' button in the window was pressed
    while cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE) > 0:
        if cv2.waitKey(100) > 0:
            break
    cv2.destroyAllWindows()
    return 0

def show_comparison(initial_img, img):

    full_img = np.concatenate((initial_img, img), axis=1)

    cv2.imshow("image", try_resize(full_img))
    # checks if any key was pressed or the 'X' button in the window was pressed
    while cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE) > 0:
        if cv2.waitKey(100) > 0:
            break
    cv2.destroyAllWindows()
    return 0

def read_data():
    test_files = []
    for file in os.listdir(os.path.join(os.getcwd(), IMG_TEST_FOLDER)):
        test_files.append(os.path.join(os.getcwd(), IMG_TEST_FOLDER, file))
    return test_files

def image_gray_to_rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

def show_comparison_4x4(img_c, img_cc, img_p, img_pc):
    colored_circles = np.concatenate((img_cc, img_c), axis=1)
    preprocessed_circles = np.concatenate((img_pc, img_p), axis=1)
    big_img = np.concatenate((colored_circles, preprocessed_circles), axis=0)

    show_image(big_img)
    return 0


def test_image_interface(img_path):
    app = interface.get_window()

    img = cv2.imread(os.path.join(IMG_TEST_FOLDER, img_path), cv2.IMREAD_GRAYSCALE)

    processed_img = pre_process(img)
    circles = detect_circles(processed_img)

    app.show_image(os.path.join(IMG_TEST_FOLDER, img_path))
    app.show_circles_at(circles)


    app.master.mainloop()
    return 0

def test_data(files):
    for file in files:
        test_image_step_by_step(file)
    return 0


def pre_process(img):
    img_copy = img.copy()
    new_img = cv2.cvtColor(np.zeros(img_copy.shape, np.uint8), cv2.COLOR_GRAY2RGB)

    threshold_img = cv2.adaptiveThreshold(img_copy, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2 )

    contours = detect_contours(threshold_img)

    new_img_contours = draw_contours(new_img, contours, (255, 255, 255))

    output_img = dilate(new_img_contours)

    output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2GRAY)
    
    return output_img
  

# read and process image passing its path
def test_image_step_by_step(img_path):
    # open source img in grayscale, colored and blank image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img_colored = cv2.imread(img_path, cv2.IMREAD_COLOR)
    new_img = cv2.cvtColor(np.zeros(img.shape, np.uint8), cv2.COLOR_GRAY2RGB)

    # pre process
    img_preprocess = pre_process(img)

    # detect circles
    circles = detect_circles(new_img)

    # draw circles in blank image
    new_img = cv2.cvtColor(new_img, cv2.COLOR_GRAY2RGB)
    new_img = draw_circles(new_img, circles)
    
    # draw circles in colored image
    img_colored_circles = draw_circles(img_colored, circles)

    # concatenate images
    big_img = np.concatenate((img_colored_circles, cv2.cvtColor(img_preprocess, cv2.COLOR_GRAY2RGB)), axis=1)

    # show images
    show_comparison(new_img, big_img)
    return 0

def dilate(img, kernel_size=3, it=1):
    output_img = img.copy()

    
    kernel = np.ones((kernel_size,kernel_size),np.uint8)
    output_img = cv2.dilate(output_img, kernel, iterations = it)
    
    #output_img = cv2.medianBlur(output_img, 5)

    return output_img

def draw_circles(img, circles):
    output = img.copy()

    if circles is not None:
        for (x, y, r) in circles:
            x, y, r = int(x), int(y), int(r)
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        print(f"drawn {len(circles)} circles")
    return output

def detect_circles(img):
    circles = []  
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1, minDist=30, 
                                param1=75, param2=20, maxRadius=50, minRadius=10)
    if circles is not None:
        print(f"detected {len(circles[0])} circles")
        circles = circles[0]
        print(circles)
    else:
        print("No circles found")
    return circles


def detect_contours(img):


    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    contours_final = []

    for contour in contours:
        apprx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)
        if len(apprx) > 8 and area > 75 and not cv2.isContourConvex(contour):
            contours_final.append(contour)
    print(f"detected {len(contours_final)} contours")
    return contours_final

def draw_contours(img, contours, color = (0, 0, 255)):
    new_img = img.copy()
    if contours == []:
        print("No contours found")
        return new_img
    #ctr = np.array(contours).reshape((-1,1,2)).astype(np.int32)
    cv2.drawContours(new_img, contours, -1, color, 2)
    return new_img

def main():
    if len(sys.argv) > 1:
        user_path = sys.argv[1]
        test_image_interface(user_path)
        return 0

    to_test = read_data()
    test_data(to_test)
    

    return 0



main()