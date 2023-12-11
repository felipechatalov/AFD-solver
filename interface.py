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
    def __init__(self, master, MAX_WIDTH=1280, MAX_HEIGHT=720):
        #window = tk.Toplevel(master)
        self.command_state = "None"
        self.circles_holder = []
        self.trans_holder = []
        self.image_holder = None
        self.master = master
        self.master.title("Interface")
        self.master.geometry(f"{MAX_WIDTH}x{MAX_HEIGHT}")
        self._WIDTH = MAX_WIDTH
        self._HEIGHT = MAX_HEIGHT
        self.create_buttons()
        self.create_canvas(MAX_WIDTH, MAX_HEIGHT)

    def set_cmd_AS(self):
        self.command_state = "AddState"
        print(f"command state set to {self.command_state}")
        return
    def set_cmd_RS(self):
        self.command_state = "RmState"
        print(f"command state set to {self.command_state}")
        return
    def set_cmd_AT(self):
        self.command_state = "AddTransition"
        print(f"command state set to {self.command_state}")
        return
    def set_cmd_RT(self):
        self.command_state = "RmTransition"
        print(f"command state set to {self.command_state}")
        return

    def is_inside_circle(self, x, y, circle):
        x0, y0, r = circle
        return (x-x0)**2 + (y-y0)**2 <= r**2
    def is_inside_any_circle(self, x, y, circles):
        index = 0
        for circle in circles:
            if self.is_inside_circle(x, y, circle):
                return index
            index += 1
        return None

    def redraw_circles(self, circles):
        self.canvas.delete("state")
        i = 0
        for circle in circles:
            self.show_circle(circle, f"S{i}")
            i+=1
        return

    def mouse_click_1(self, event):
        print(f"clicked at {event.x}, {event.y}")
        if self.command_state == "AddState":
            self.show_circle((event.x, event.y, 30), f"S{len(self.circles_holder)}")
            self.circles_holder.append((event.x, event.y, 30))

        elif self.command_state == "RmState":
            # detect if click is inside a circle
            rm = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
            if rm != None:
                # remove circle from list
                self.circles_holder.pop(rm)
                
                # redraw circles
                self.redraw_circles(self.circles_holder)
                pass
            pass
        elif self.command_state == "AddTransition":
            pass
        elif self.command_state == "RmTransition":
            pass
        else:
            pass
        return        

    def create_buttons(self):
        self.optionsHolder = tk.Frame(self.master, width=150, height=self._HEIGHT, bg="white", )
        self.optionsHolder.pack(fill=tk.Y, side=tk.LEFT)
        #self.optionsHolder.place(x=0, y=self._HEIGHT/2, anchor=tk.W)
        self.optionsHolder.pack()

        
        self.addState = tk.Button(self.optionsHolder, 
                                    command = self.set_cmd_AS,
                                    text="Add State", 
                                    width=16, height=2, 
                                    bg="green", fg="white")
        self.addState.pack()

        self.RmState = tk.Button(self.optionsHolder, 
                                    command = self.set_cmd_RS,
                                    text="Remove State", 
                                    width=16, height=2, 
                                    bg="red", fg="white")
        self.RmState.pack()

        self.AddTransition = tk.Button(self.optionsHolder, 
                                       command = self.set_cmd_AT,
                                       text="Add Transition", 
                                       width=16, height=2, 
                                       bg="green", fg="white")
        self.AddTransition.pack()

        self.RmTransition = tk.Button(self.optionsHolder, 
                                      command = self.set_cmd_RT,
                                      text="Remove Transition", 
                                      width=16, height=2, 
                                      bg="red", fg="white")
        self.RmTransition.pack()
        return

    def create_canvas(self, _width, _height):
        self.canvas = tk.Canvas(self.master, width=_width, height=_height)
        self.canvas.bind("<Button-1>", self.mouse_click_1)
        self.canvas.pack()
        return

    def show_transition(self, transition):
        t1, t2 = transition
        t1x, t1y, t1r = self.circles_holder[t1]
        t2x, t2y, t2r = self.circles_holder[t2]

        offsetx1 = t1r * (t2x - t1x) / ((t2x - t1x)**2 + (t2y - t1y)**2)**0.5
        offsety1 = t1r * (t2y - t1y) / ((t2x - t1x)**2 + (t2y - t1y)**2)**0.5
        
        offsetx2 = t2r * (t1x - t2x) / ((t2x - t1x)**2 + (t2y - t1y)**2)**0.5
        offsety2 = t2r * (t1y - t2y) / ((t2x - t1x)**2 + (t2y - t1y)**2)**0.5

        t1x += offsetx1
        t1y += offsety1
        t2x += offsetx2
        t2y += offsety2

        self.canvas.create_line(t1x, t1y, t2x, t2y, fill="#f11", width=2, tags="transition")
        return

    def show_transitions(self, transitions):
        if transitions == []:
            return
        for transition in transitions:
            self.show_transition(transition)
        return

    def show_circle(self, coords, text):
        
        x, y, r = coords
        self.canvas.create_oval(x-r, y-r, x+r, y+r, outline="#f11", width=2, tags="state")
        self.canvas.create_text(x, y, text=text, fill="#f11", font=("Arial", 24), tags="state")
        #print(f"circle shown at {x}, {y}")
        return

    def show_circles_at(self, circles):
        if circles == []:
            return
        i = 0
        for circle in circles:
            self.show_circle(circle, f"S{i}")
            self.circles_holder.append(circle)
            i += 1
        return


    def show_image(self, path):
        if type(path) == str:
            path = imread(path, IMREAD_GRAYSCALE)

        img = Image.fromarray(path)

        img.resize((self._WIDTH, self._HEIGHT))
        pimg = ImageTk.PhotoImage(img)
        self.image_holder = pimg

        self.canvas.create_image(0, 0, anchor=tk.NW, image=pimg)
        self.canvas.image = pimg 

def create_window():
    return Interface(ROOT)

def main():
    return 0

if __name__ == "__main__":
    main()

                       