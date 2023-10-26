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

    img = np.concatenate((img, initial_img), axis=1)

    cv2.imshow("image", try_resize(img))
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
        
        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        img_colored = cv2.imread(file, cv2.IMREAD_COLOR)

        img_preprocess = pre_process(img)
        circles = detect_circles(img_preprocess)

        #img_circles_rgb = cv2.cvtColor(img_circles, cv2.COLOR_GRAY2RGB)

        img_colored_circles = draw_circles(img_colored, circles)
        img_preprocess_circles = draw_circles(img_preprocess, circles)

        big_img = np.concatenate((img_colored_circles, image_gray_to_rgb(img_preprocess)), axis=1)

        show_comparison(img_colored, big_img)
        
        #show_comparison_4x4(img_colored, img_colored_circles, 
        #                    image_gray_to_rgb(img_preprocess), image_gray_to_rgb(img_preprocess_circles))
    return 0


# read and process image passing its path
def test_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

    img_preprocess = pre_process(img)
    circles = detect_circles(img_preprocess)

    #img_circles_rgb = cv2.cvtColor(img_circles, cv2.COLOR_GRAY2RGB)

    img_circles = draw_circles(img_preprocess, circles)

    big_img = np.concatenate((img_circles, img_preprocess), axis=1)

    show_comparison(img, big_img)
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


# ideia: use board detection to enrance the image
def pre_process(img):
    # remove noise
    #img = cv2.medianBlur(img, 3)
    img = cv2.GaussianBlur(img, (9, 9), 2)


    # get histogram
    # hist = cv2.calcHist([img],[0],None,[256],[0,256])
    # plt.plot(hist)
    # plt.show()

    # increase contrast
    img = cv2.addWeighted(img, 2.0, np.zeros(img.shape, img.dtype), 0, 25) 

    # another way to increase contrast
    #img = cv2.equalizeHist(img)

    # yet another way to increase contrast
    # img = cv2.convertScaleAbs(img, alpha=1.5, beta=20)

    


    # enhance edges
    edges = cv2.Canny(img, 50, 200)
    #img = cv2.add(img, edges)


    # erode
    kernel = np.ones((5,5),np.uint8)
    img = cv2.erode(img, kernel, iterations = 1)


    # threshold the image
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2 )
    #img = cv2.threshold(img, 254, 255, cv2.THRESH_BINARY)[1]


    # more blur
    #img = cv2.GaussianBlur(img, (9, 9), 0)
    
    return img

def draw_circles(img, circles):
    output = img.copy()

    # if we find circles we draw them on top of the copy of the image
    if circles is not None:
        for (x, y, r) in circles:
            x, y, r = int(x), int(y), int(r)
            cv2.circle(img, (x, y), r, (0, 255, 0), 4)
    
    return output

def detect_circles(img):
    # detect circles    
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=0.7, minDist=30, 
                                param1=100, param2=20, maxRadius=50, minRadius=10)[0]
    # circles = cv2.HoughCircles(
    #     img,               # Input image (grayscale)
    #     cv2.HOUGH_GRADIENT,# Detection method
    #     dp=1,              # Inverse ratio of the accumulator resolution
    #     minDist=50,        # Minimum distance between detected centers
    #     param1=100,        # Upper threshold for edge detection
    #     param2=30,         # Threshold for center detection
    #     minRadius=0,       # Minimum radius
    #     maxRadius=0        # Maximum radius
    #     )

    #circles = remove_colliding_circles(circles)

    return circles

def detect_letters(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18)) 
     
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1) 
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,  
                                                 cv2.CHAIN_APPROX_NONE) 
    im2 = img.copy() 

    for cnt in contours: 
        x, y, w, h = cv2.boundingRect(cnt) 
        
        
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2) 
        
        
        cropped = im2[y:y + h, x:x + w] 
        
        
        file = open("recognized.txt", "a") 
        
        
        text = pytesseract.image_to_string(cropped) 
        
        
        file.write(text) 
        file.write("\n") 
      
    file.close 
    return 0


def main():
    if len(sys.argv) > 1:
        user_path = sys.argv[1]
        test_image(user_path)
        return 0

    to_test = read_data()
    test_data(to_test)
    

    return 0



main()