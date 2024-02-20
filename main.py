import cv2
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import easyocr


import interface


# https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html


# TODO check if img is bigger than some value, if true resize it to fit screen

IMG_TEST_FOLDER = "images/"

TEST_TRANSITIONS = [[1, 2]]

WIDTH_CAP = 1280
HEIGHT_CAP = 720



def show_image(img):
    img = cv2.resize(img, (WIDTH_CAP, HEIGHT_CAP))
    cv2.imshow("image", img)
    # checks if any key was pressed or the 'X' button in the window was pressed
    while cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE) > 0:
        if cv2.waitKey(100) > 0:
            break
    cv2.destroyAllWindows()
    return 0


def detect_letters_tesseract(img: cv2.Mat):
    import pytesseract


    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    hImg, wImg, _ = img.shape
    boxes = pytesseract.image_to_boxes(img)
    print(boxes)
    for b in boxes.splitlines():
        b = b.split(' ')
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x, wImg-y), (w, hImg-h), (0, 0, 255), 1)
        cv2.putText(img, b[0], (x, hImg-y+25), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 2)
    show_image(img)
    return 0

def detect_letters_easyocr(img):
    reader = easyocr.Reader(['en'])
    #img = cv2.imread(img_path)
    result = reader.readtext(img)
    return result

def detect_features(img_path: str) -> int:
    # read image
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("Image not found")
        return 0
    img = cv2.resize(img, (WIDTH_CAP, HEIGHT_CAP))

    # pre process image to detect contours    
    processed_img = pre_process(img)
    circles = detect_circles(processed_img)
    # try some letters/transitions detection
    #text_easyocr = detect_letters_easyocr(img)
    #text_tesseract = detect_letters_tesseract(img)

    #detect_transitions(img)
    
    

    # instanciate the interface
    app = interface.create_window()

    # draw image then states

    app.show_image(img_path)
    app.show_circles_at(circles)

    # draw text detected and square arround it
    # need to be after img and circles because it redraws everything on screen
    #for t in text_easyocr:
    #    app.draw_square_text_at(t[0], t[1])

    # run the interface
    app.master.mainloop()
    return 0

def pre_process(img: cv2.Mat) -> cv2.Mat:
    img_copy = img.copy()
    new_img = cv2.cvtColor(np.zeros(img_copy.shape, np.uint8), cv2.COLOR_GRAY2RGB)

    threshold_img = cv2.adaptiveThreshold(img_copy, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2 )
    threshold_img = cv2.bitwise_not(threshold_img)

    contours = detect_contours(threshold_img)

    new_img_contours = draw_contours(new_img, contours, (255, 255, 255))

    #output_img = dilate(new_img_contours)

    output_img = cv2.cvtColor(new_img_contours, cv2.COLOR_RGB2GRAY)
    
    return output_img
  

def draw_circles(img, circles):
    output = img.copy()

    if circles is not None:
        for (x, y, r) in circles:
            x, y, r = int(x), int(y), int(r)
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        print(f"drawn {len(circles)} circles")
    return output

def detect_circles(img: cv2.Mat) -> list:
    circles = []  
    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, dp=1, minDist=30, 
                                param1=75, param2=20, maxRadius=50, minRadius=25)
    if circles is not None:
        print(f"detected {len(circles[0])} circles")
        circles = circles[0]
        print(circles)
    else:
        print("No circles found")
    return circles

def detect_transitions(img):
    img_copy = img.copy()

    img_copy = cv2.GaussianBlur(img_copy, (5, 5), 0)

    edges = cv2.Canny(img_copy, 50, 150)

    rho = 1
    theta = np.pi/180
    threshold = 15
    min_line_length = 150
    max_line_gap = 40
    line_image = img.copy()

    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                                min_line_length, max_line_gap)
    
    
    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(line_image,(x1,y1),(x2,y2),60,5)    

    lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    #show_image(lines_edges)

    return lines


def detect_lines(img):
    cont, hier = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    lines = []

    for c in cont:
        x, y, w, h = cv2.boundingRect(c)
        if w > 50 or h > 50:
            lines.append((x, y, w, h))

    print(f"detected {len(lines)} lines")
    return lines


def detect_contours(img: cv2.Mat) -> list:
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
    cv2.drawContours(new_img, contours, -1, color, 2)
    return new_img


def run_all_dir(dir_path: str) -> int:
    for img in os.listdir(dir_path):
        img_path = os.path.join(dir_path, img)
        detect_features(img_path)
    return 0

def main():
    if len(sys.argv) > 4:
        print("Usage: python main.py <image_path>")
        return 0
    if sys.argv[1] == "-d":
        run_all_dir(sys.argv[2])
        return 0
    
    img_path = sys.argv[1]
    if not os.path.isfile(img_path):
        print("File not found")
        return 0
    detect_features(img_path) 

    return 0



main()