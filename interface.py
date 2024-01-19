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
        self.aux_rm_transition = None
        self.InitialState = None
        self.FinalState = None
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
    def set_cmd_IS(self):
        self.command_state = "InitialState"
        print(f"command state set to {self.command_state}")
        return
    def set_cmd_FS(self):
        self.command_state = "FinalState"
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
        
        # extra circle for initial state
        print(self.InitialState)
        if self.InitialState is not None:
            ix, iy, ir = circles[self.InitialState]
            self.canvas.create_oval(ix-ir+5, iy-ir+5, ix+ir-5, iy+ir-5, outline="#ffaa50", width=2, tags="state")
            self.canvas.create_text(ix, iy+20, text="Inicial", fill="#0000ff", font=("Arial", 24), tags="state")
        
        # extra circle for final state
        if self.FinalState is not None:
            fx, fy, fr = circles[self.FinalState]
            self.canvas.create_oval(fx-fr+5, fy-fr+5, fx+fr-5, fy+fr-5, outline="#ff50aa", width=2, tags="state")
            self.canvas.create_text(fx, fy+20, text="Final", fill="#0000ff", font=("Arial", 24), tags="state")

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
            if self.aux_rm_transition is None:
                self.aux_rm_transition = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
                print(f"aux_rm_transition set to {self.aux_rm_transition}")
            else:
                aux = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
                print(f"aux is {aux}")
                if self.aux_rm_transition is not None and aux is not None:
                    print(f"removing first transition from S{self.aux_rm_transition} to S{aux}")
                    self.rm_transition(self.aux_rm_transition, aux)
                    self.aux_rm_transition = None



        elif self.command_state == "InitialState":
            self.InitialState = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
            #print(f"initial state set to {self.InitialState}")
            self.redraw_circles(self.circles_holder)
        elif self.command_state == "FinalState":
            self.FinalState = self.is_inside_any_circle(event.x, event.y, self.circles_holder)
            #print(f"final state set to {self.FinalState}")
            self.redraw_circles(self.circles_holder)
        return        

    def rm_transition(self, t1, t2):
        for transition in self.transitions_holder:
            if t1 == transition[0] and t2 == transition[1]:
                #print(f"removing transition {transition}")
                if len(transition[2]) == 1:
                    self.transitions_holder.remove(transition)
                else:
                    transition[2].pop(len(transition[2])-1)
                break
        self.redraw_transitions(self.transitions_holder)
        


    def add_transition(self, t1, t2):
        sec_window = tk.Toplevel(self.master)
        sec_window.title("Transition")
        sec_window.geometry("300x100")
        entry = tk.Entry(sec_window)
        entry.pack()


        def add_text_and_close2():
            values = entry.get()

            if values == "":
                print("Transition cant be empty")
                return

            for transition in self.transitions_holder:
                if t1 == transition[0] and t2 == transition[1]:
                    transition[2].append(values)
                    self.aux_add_transition = None
                    self.redraw_transitions(self.transitions_holder)
                    sec_window.destroy()
                    return
            
            self.transitions_holder.append((t1, t2, [values]))

            self.aux_add_transition = None
            #self.show_transitions(self.transitions_holder)
            self.redraw_transitions(self.transitions_holder)
            sec_window.destroy()
            return

        quitbutton = tk.Button(sec_window, text="OK", command=add_text_and_close2)
        quitbutton.pack()
        
    def is_any_transition_with(self, t1, t2, values):
        for transition in self.transitions_holder:
            if t1 == transition[0] and t2 == transition[1] and (values == "" or values == transition[2]):
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

        
        self.btaddState = tk.Button(self.optionsHolder, 
                                    command = self.set_cmd_AS,
                                    text="Add State", 
                                    width=16, height=2, 
                                    bg="green", fg="white")
        self.btaddState.pack()

        self.btRmState = tk.Button(self.optionsHolder, 
                                    command = self.set_cmd_RS,
                                    text="Remove State", 
                                    width=16, height=2, 
                                    bg="red", fg="white")
        self.btRmState.pack()

        self.btAddTransition = tk.Button(self.optionsHolder, 
                                       command = self.set_cmd_AT,
                                       text="Add Transition", 
                                       width=16, height=2, 
                                       bg="green", fg="white")
        self.btAddTransition.pack()

        self.btRmTransition = tk.Button(self.optionsHolder, 
                                      command = self.set_cmd_RT,
                                      text="Remove Transition", 
                                      width=16, height=2, 
                                      bg="red", fg="white")
        self.btRmTransition.pack()

        self.btInitialState = tk.Button(self.optionsHolder,
                                        command = self.set_cmd_IS,
                                        text="Initial State", 
                                        width=16, height=2, 
                                        bg="green", fg="white")
        self.btInitialState.pack()

        self.btFinalState = tk.Button(self.optionsHolder,
                                        command = self.set_cmd_FS,
                                        text="Final State", 
                                        width=16, height=2, 
                                        bg="red", fg="white")
        self.btFinalState.pack()

        self.btSave = tk.Button(self.optionsHolder,
                                command = self.save,
                                text="Save", 
                                width=16, height=2, 
                                bg="blue", fg="white")
        self.btSave.pack()

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


        if t1 == t2:
            self.canvas.create_arc(t1x-t1r, t1y-t1r-30, t1x+t1r, t1y+t1r, 
                                outline="#ff0000", width=2, tags="transition", 
                                start=0, extent=180, style=tk.ARC)
            return


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

        self.canvas.create_line(t1x, t1y, final[0], final[1], t2x, t2y, 
                                fill="#f11", width=2, smooth=1, tags="transition", 
                                arrow=tk.LAST, arrowshape=(20, 25, 10))
        return

    def show_transitions(self, transitions):
        if transitions == []:
            return
        for transition in transitions:
            self.show_transition(transition)
            #self.draw_transition_text(transition)
        return

    def redraw_transitions(self, transitions):
        self.canvas.delete("transition")
        self.show_transitions(transitions)

        for transition in transitions:
            self.draw_transition_text(transition)

        return

    def draw_transition_text(self, transition):
        t1, t2, _text = transition

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

        #print('number of transitions beetween', t1, t2, self.number_of_transitions_beetween(t1, t2))

        index = 0
        #print("size of _text", len(_text), _text)
        #print("transitions", self.transitions_holder)

        if t1 == t2:
            final = self.circles_holder[t1][0], self.circles_holder[t1][1]-45

        for t in _text:
            self.canvas.create_text(final[0], final[1]-30*(index-1), text=t, fill="#0000ff", font=("Arial", 24), tags="transition")
            print("adicionado texto em ", final[0], final[1]+30*(index-1))
            index +=1



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

    def create_xml(self):
        xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n"""
        xml += """\t<structure>\n"""
        xml += """\t<type>fa</type>\n"""
        xml += """\t<automaton>"""
        xml = self.states_to_xml(xml, self.circles_holder)
        xml = self.transitions_to_xml(xml, self.transitions_holder)
        xml += """\t</automaton>\n"""
        xml += """</structure>\n"""
        return xml

    def save(self):
        xml = self.create_xml()
        with open("output.jff", "w") as f:
            f.write(xml)
        return

    def states_to_xml(self, xml, states):
        '''
        <state id="3" name="q3">&#13;
			<x>318.0</x>&#13;
			<y>213.0</y>&#13;
		</state>&#13;
        ''' 

        index = 0
        for state in states:
            x, y = state[0], state[1]

            # used to limit values to 300x300 inside simulator
            #x = x * 300 / 1280
            #y = y * 300 / 720

            xml += f"""
            \t<state id="{index}" name="S{index}">
            \t\t<x>{x}</x>
            \t\t<y>{y}</y>
            \t</state>"""
            index += 1
        return xml

    def transitions_to_xml(self, xml, transitions):
        '''
        <transition>&#13;
			<from>2</from>&#13;
			<to>3</to>&#13;
			<read>eaaaa</read>&#13;
		</transition>&#13;
        '''

        for transition in transitions:
            for value in transition[2]:
                xml += f"""
                <transition>
                \t<from>{transition[0]}</from>
                \t<to>{transition[1]}</to>
                \t<read>{value}</read>
                </transition>"""
        return xml

def create_window():
    return Interface(ROOT)

def main():
    return 0

if __name__ == "__main__":
    main()

                       