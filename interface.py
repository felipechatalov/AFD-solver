import tkinter as tk
from cv2 import imread, IMREAD_GRAYSCALE
from PIL import Image, ImageTk

ROOT = tk.Tk()

CIRCLES_LIST = [[717.5, 651.5, 47.2],
                [838.5, 264.5, 40.5],
                [215.5, 556.5, 42.7],
                [186.5, 252.5, 41.4],
                [842.5, 172.5, 34.3],
                [620.5, 279.5, 32.9],
                [508.5, 499.5, 34.3],
                [ 35.5, 279.5, 37.3]]

class Interface():
    def __init__(self, master):
        #window = tk.Toplevel(master)
        self.master = master
        self.master.title("Interface")
        self.master.geometry("1635x920")
        
        self.create_buttons()
        self.create_canvas(1635, 920)
        #self.show_image("images/cad4_edit.jpeg")
        #self.show_circles_at(CIRCLES_LIST)

        #self.master.mainloop()

    def create_buttons(self):
        self.optionsHolder = tk.Frame(self.master, width=100, height=500, bg="blue", )
        self.optionsHolder.pack(side="left", fill=tk.Y)       
        
        self.addState = tk.Button(self.optionsHolder, text="Add State", width=8, height=2, bg="green", fg="white")
        self.addState.pack()

        self.RmState = tk.Button(self.optionsHolder, text="Remove State", width=8, height=2, bg="red", fg="white")
        self.RmState.pack()

        self.AddTransition = tk.Button(self.optionsHolder, text="Add Transition", width=8, height=2, bg="green", fg="white")
        self.AddTransition.pack()

        self.RmTransition = tk.Button(self.optionsHolder, text="Remove Transition", width=8, height=2, bg="red", fg="white")
        self.RmTransition.pack()
        return

    def create_canvas(self, _width, _height):
        self.canvas = tk.Canvas(self.master, width=_width, height=_height)
        self.canvas.pack()
        return

    def show_circle(self, coords, text):
        
        x, y, r = coords
        self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="#f11", width=2)
        self.canvas.create_text(x, y, text=text, fill="#f11", font=("Arial", 24))
        return

    def show_circles_at(self, circles):
        if circles == []:
            return
        i = 0
        for circle in circles:
            self.show_circle(circle, f"S{i}")
            i += 1
        return


    def show_image(self, path):
        if type(path) == str:
            path = imread(path, IMREAD_GRAYSCALE)

        img = Image.fromarray(path)
        pimg = ImageTk.PhotoImage(img)

        img_w, img_h = img.size

        if img_w > 1635 or img_h > 920:
           scalew = 1635/img_w 
           scaleh = 920/img_h
           pimg.zoom(scalew, scaleh)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=pimg)
        self.canvas.image = pimg 

def get_window():
    return Interface(ROOT)

def main():
    return 0

if __name__ == "__main__":
    main()

                       