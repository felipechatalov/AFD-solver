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
        self.transitions_holder = []
        self.image_holder = None
        self.master = master
        self.master.title("Interface")
        self.master.geometry("1430x720")
        self.aux_add_transition = None
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
        elif self.command_state == "AddTransition":

            if self.aux_add_transition is None:
                self.aux_add_transition = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
                print(f"aux_add_transition set to {self.aux_add_transition}")
            else:
                aux = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
                print(f"aux is {aux}")
                if self.aux_add_transition is not None and aux is not None:
                    print(f"adding transition from S{self.aux_add_transition} to S{aux}")
                    
                    self.add_transition(self.aux_add_transition, aux)
                
        elif self.command_state == "RmTransition":
            pass
        else:
            pass
        return        

    def add_transition(self, t1, t2):
        sec_window = tk.Toplevel(self.master)
        sec_window.title("Transition")
        sec_window.geometry("300x100")
        entry = tk.Entry(sec_window)
        entry.pack()

        def add_text_and_close():
            values = entry.get()

            if self.is_any_transition_with(t1, t2, values):
                print("existing transition")
                return


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

            pmedio = ((t1x + t2x)/2, (t1y + t2y)/2)

            vetor = ((t2x - t1x), (t2y - t1y))

            vetordeslocado = -vetor[1]*0.4, vetor[0]*0.4

            final = (pmedio[0] + vetordeslocado[0], pmedio[1] + vetordeslocado[1])


            number = self.number_of_transitions_beetween(t1, t2)

            self.canvas.create_text(final[0], final[1]+30*(number-1), text=values, fill="#0000ff", font=("Arial", 24), tags="transition")
            self.transitions_holder.append((t1, t2, values))
            self.aux_add_transition = None
            self.show_transitions(self.transitions_holder)


            sec_window.destroy()
            return

        quitbutton = tk.Button(sec_window, text="OK", command=add_text_and_close)
        quitbutton.pack()
        
    def is_any_transition_with(self, t1, t2, values):
        for transition in self.transitions_holder:
            if t1 == transition[0] and t2 == transition[1] and values == transition[2]:
                return True
        return False

    def number_of_transitions_beetween(self, t1, t2):
        count = 0
        for transition in self.transitions_holder:
            if t1 == transition[0] and t2 == transition[1]:
                count += 1
        return count

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
        t1, t2, _ = transition
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

        pmedio = ((t1x + t2x)/2, (t1y + t2y)/2)

        vetor = ((t2x - t1x), (t2y - t1y))

        vetordeslocado = -vetor[1]*0.4, vetor[0]*0.4

        final = (pmedio[0] + vetordeslocado[0], pmedio[1] + vetordeslocado[1])






        self.canvas.create_line(t1x, t1y, final[0], final[1], t2x, t2y, fill="#f11", width=2, smooth=1, tags="transition")
        
        
        

    
        
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
        if circles is None:
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

        img = img.resize((1280, 720))
        pimg = ImageTk.PhotoImage(img)
        #self.image_holder = pimg

        self.canvas.create_image(0, 0, anchor=tk.NW, image=pimg)
        self.canvas.image = pimg 

def create_window():
    return Interface(ROOT)

def main():
    return 0

if __name__ == "__main__":
    main()

                       