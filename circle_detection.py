import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html

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


def test_data(files):
    for file in files:
        test_image(file)
    return 0


# read and process image passing its path
def test_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img_colored = cv2.imread(img_path, cv2.IMREAD_COLOR)

    img_preprocess = pre_process(img)

    circles = detect_circles(img_preprocess)
    contours = detect_contours(img_preprocess)

    img_colored_contours = draw_contours(img_colored, contours)

    img_colored_contours_circles = draw_circles(img_colored_contours, circles)
    # img_preprocess_circles = draw_circles(img_preprocess, circles)

    new_img = cv2.cvtColor(np.zeros(img.shape, np.uint8), cv2.COLOR_GRAY2RGB)
    new_img_contours = draw_contours(new_img, contours, (255, 255, 255))

    new_img = pre_process2(new_img_contours)

    new_img = cv2.cvtColor(new_img, cv2.COLOR_RGB2GRAY)

    circles2 = detect_circles(new_img)
    
    new_img = cv2.cvtColor(new_img, cv2.COLOR_GRAY2RGB)
    new_img = draw_circles(new_img, circles2)
    
        
    big_img = np.concatenate((img_colored_contours_circles, image_gray_to_rgb(img_preprocess)), axis=1)

    show_comparison(new_img, big_img)
        
    return 0

def remove_colliding_circles(circles):
    new_circles = []
    print(circles)
    for c1 in circles:
        col = False
        for c2 in circles:
            if c1[0] != c2[0] and c1[1] != c2[1]:
                if is_circle_colliding(c1, c2):
                    col = True
                    break
        if not col:
            new_circles.append(c1)
    return new_circles

def is_circle_colliding(c1, c2):
    x1, y1, r1 = c1
    x2, y2, r2 = c2

    dist = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    if dist < r1 + r2:
        return True
    return False

def pre_process2(img):
    output_img = img.copy()

    
    kernel = np.ones((3,3),np.uint8)
    output_img = cv2.dilate(output_img, kernel, iterations = 1)
    
    #output_img = cv2.medianBlur(output_img, 5)

    return output_img

# ideia: use board detection to enrance the image
def pre_process(img):
    output_img = img.copy()
    # remove noise
    #output_img = cv2.medianBlur(output_img, 5)
    #output_img = cv2.GaussianBlur(output_img, (9, 9), 2)

    # threshold the image
    output_img = cv2.adaptiveThreshold(output_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2 )

    return output_img

def draw_circles(img, circles):
    output = img.copy()

    # if we find circles we draw them on top of the copy of the image
    if circles is not None:
        for (x, y, r) in circles:
            x, y, r = int(x), int(y), int(r)
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        print(f"drawn {len(circles)} circles")
    return output

def detect_circles(img):
    # detect circles  
    circles = []  
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1, minDist=30, 
                                param1=75, param2=20, maxRadius=50, minRadius=10)
    if circles is not None:
        print(f"detected {len(circles[0])} circles")
        #print(circles)
        #print(circles[0])
        circles = circles[0]
    else:
        print("No circles found")
    return circles


def detect_contours(img):


    #edges = cv2.Canny(img, 50, 200)
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    contours_final = []
    #conts = np.array(contours).reshape((-1,1,2)).astype(np.int32)

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
        test_image(user_path)
        return 0

    to_test = read_data()
    test_data(to_test)
    

    return 0



main()