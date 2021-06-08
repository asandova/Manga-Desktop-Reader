#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ScrollableFrame.py                                            #
#description     :Defines a Scrollable Frame widget for tkinter                 #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :Defines a scrollable frame widget                             #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

from tkinter import Tk, Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, N, W, S, E, Label, Grid, Button
try:
    from DynamicCanvas import DynamicCanvas
except:
    from tk.DynamicCanvas import DynamicCanvas
try:
    from tkinter import Tk, Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, N, W, S, E, Label, Grid, Button, NONE
    from tkinter.ttk import Scrollbar
except:
    from Tkinter import Tk, Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, N, W, S, E, Label, Grid, Button, NONE
    from Tkinter.ttk import  Scrollbar
#from tkinter.ttk import *

import platform, logging, os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/" + __name__ + ".log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class ScrollableFrame(Frame):
    
    def __init__(self, master, vscrollside="right", hscrollside="bottom", anchor="c",*args, **kwargs):
        Frame.__init__(self, master=master, *args, **kwargs)
        self.__ScrollFrame = None
        self.__VScroll = None
        self.__HScroll = None
        self.__Canvas = None
        self.__Anchor = anchor
        #initializes internal widgets

        #position arrays, stores the position for all widgets withing the parent frames grid
        #[row, col]
        self.__CanvasPos= [0,0]
        self.__VScrollPos=[0,1]
        self.__HScrollPos=[1,0]

        if vscrollside == "right":
            self.__CanvasPos[1]  = 0
            self.__VScrollPos[1] = 1 
            self.__HScrollPos[1] = 0

        elif vscrollside == "left":
            self.__CanvasPos[1]  = 1
            self.__VScrollPos[1] = 0 
            self.__HScrollPos[1] = 1

        else:
            self.__CanvasPos[1]  = 0
            self.__VScrollPos[1] = -1 
            self.__HScrollPos[1] = 0
            
        if hscrollside == "bottom":
            self.__CanvasPos[0]  = 0
            self.__HScrollPos[0] = 1
            self.__VScrollPos[0] = 0
            
        elif hscrollside == "top":
            self.__CanvasPos[0]  = 1
            self.__HScrollPos[0] = 0
            self.__VScrollPos[0] = 1

        else:
            self.__CanvasPos[0]  = 1
            self.__HScrollPos[0] = 0
            self.__VScrollPos[0] = 1

        self.bind("<Enter>", self.__on_enter)
        self.bind("<Leave>", self.__on_leave)

        if platform.system() == "Windows":
            self.bind_all("<MouseWheel>", self.__on_mousewheel)
            self.bind_all("<Shift-MouseWheel>", self.__on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.bind_all("<Button-4>",self.__on_mousewheel)
            self.bind_all("<Button-5>",self.__on_mousewheel)
            self.bind_all("<Shift-Button-4>",self.__on_shift_mousewheel)
            self.bind_all("<Shift-Button-5>",self.__on_shift_mousewheel)

    def _build(self):
        self.__VScroll = Scrollbar(master=self, orient="vertical" )
        self.__HScroll = Scrollbar(master=self, orient="horizontal")
        self.__Canvas = DynamicCanvas(master=self, highlightthickness=0,
                                        yscrollcommand = self.__VScroll.set,
                                        xscrollcommand = self.__HScroll.set)
        self.__ScrollFrame = Frame(master=self.__Canvas)
        
        Grid.rowconfigure(self, self.__CanvasPos[0], weight=1)
        Grid.columnconfigure(self,self.__CanvasPos[1],weight=1)

        self.__Canvas.grid(row=self.__CanvasPos[0], column=self.__CanvasPos[1],sticky=N+S+E+W)

        placement_x = None
        placement_y = None
        if "n" in self.__Anchor:
            placement_y = 0
            placement_x = (self.__Canvas.width/2) + (self.__ScrollFrame["width"] / 2)
        if "w" in self.__Anchor:
            placement_x = 0
            placement_y = (self.__Canvas.height/2) + (self.__ScrollFrame["height"] / 2)
        else:
            placement_x = (self.__Canvas.width/2) + (self.__ScrollFrame["width"] / 2) 
            placement_y = (self.__Canvas.height/2) + (self.__ScrollFrame["height"] / 2)
        FrameDimentions = ( self.__ScrollFrame["width"], self.__ScrollFrame["height"] )
        CanvasDimentions = (self.__Canvas.winfo_width(), self.__Canvas.winfo_height() )
        logger.info(f"Scroll Frame Dimentions: W,H: {FrameDimentions }")
        logger.info(f"Canvas Dimentions: W,H: {CanvasDimentions}")
        logger.info(f"Canvas Dimentions: W: {self.__Canvas.width}, H: {self.__Canvas.height}")
        logger.info(f"Canvas Window Placement: X: {placement_x}, Y: {placement_y}, W: {self.__Canvas.width}, H: {self.__Canvas.height}")


        self.__Canvas.create_window(placement_x ,
                                    placement_y,
                                    window=self.__ScrollFrame, 
                                    anchor=self.__Anchor)

        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))
        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)

        self.__VScroll.config(command = self.__Canvas.yview)
        self.__HScroll.config(command = self.__Canvas.xview)
        self.__HScroll.grid(row=self.__HScrollPos[0], column=self.__HScrollPos[1], sticky=E+W)
        self.__VScroll.grid(row=self.__VScrollPos[0], column=self.__VScrollPos[1], sticky=N+S)

        self.__ScrollFrame.bind("<Configure>", self.scrollregion_change)

    def pack(self, **kwargs): 
        self._build()
        Frame.pack(self, **kwargs)

    def grid(self, **kwargs):
        self._build()
        Frame.grid(self, **kwargs)

    def scrollregion_change(self,event):
        self.__ScrollFrame.unbind("<Configure>")
        self.__Canvas.configure(
            scrollregion=self.__Canvas.bbox("all")
        )
        logger.info( f"Canvas Dimentions updated - X: {self.__Canvas.winfo_rootx()}, Y: {self.__Canvas.winfo_rooty()}, width: {self.__Canvas.winfo_width()}, Height: {self.__Canvas.winfo_height()}" )
        verticalBounds = self.__VScroll.get()
        horizontalBounds = self.__HScroll.get()
        if verticalBounds == (0.0, 1.0):
            if self.__VScroll.winfo_ismapped():
                if self.__VScroll.winfo_manager() == "grid":
                    self.__VScroll.grid_forget()
        elif verticalBounds != (0.0, 1.0):
            if self.__VScroll.winfo_ismapped() == False:
                self.__VScroll.grid(row=self.__VScrollPos[0], column=self.__VScrollPos[1],sticky=N+S)

        if horizontalBounds == (0.0, 1.0):
            if self.__HScroll.winfo_ismapped():
                if self.__HScroll.winfo_manager() == "grid":
                    self.__HScroll.grid_forget()
        elif horizontalBounds != (0.0, 1.0):
            if self.__HScroll.winfo_ismapped() == False:
                self.__HScroll.grid(row=self.__HScrollPos[0], column=self.__HScrollPos[1],sticky=E+W)

        self.__ScrollFrame.bind("<Configure>", self.scrollregion_change)

    def get_attach_point(self):
        """returns a tkinter widget reference for attaching other widgets to this frame
        """
        return self.__ScrollFrame

    def grid_rowconfigure(self, index, weight):
        """Configure a row at index for internal widgets in the scroll frame
        """
        self.__ScrollFrame.grid_rowconfigure(index=index, weight=weight)

    def grid_columnconfigure(self, index, weight):
        """Configure a Column at index for internal widgets in the scroll frame
        """
        print("In grid_columnconfig")
        self.__ScrollFrame.grid_columnconfigure(index=index, weight=weight)

    # Signal callback methods ---------------------------------------------------------------#

    def __on_enter(self, event):
        if platform.system() == "Windows":
            self.bind_all("<MouseWheel>", self.__on_mousewheel)
            self.bind_all("<Shift-MouseWheel>", self.__on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.bind_all("<Button-4>",self.__on_mousewheel)
            self.bind_all("<Button-5>",self.__on_mousewheel)
            self.bind_all("<Shift-Button-4>",self.__on_shift_mousewheel)
            self.bind_all("<Shift-Button-5>",self.__on_shift_mousewheel)

    def __on_leave(self,event):
        if platform.system() == "Windows":
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Shift-MouseWheel>")
        elif platform.system() == "Linux":
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
            self.unbind_all("<Shift-Button-4>")
            self.unbind_all("<Shift-Button-5>")
            
    def __on_mousewheel(self,event):
        delta = event.delta
        if self.__VScroll.get() != (0.0, 1.0):
            if platform.system() == "Linux":
                if event.num == 5:
                    delta = -1
                elif event.num == 4:
                    delta = 1
                self.__Canvas.yview_scroll( int(-1 * delta), "units" )
            else:       
                self.__Canvas.yview_scroll( int(-1 * (event.delta/120)), "units" )

    def __on_shift_mousewheel(self,event):
        delta = event.delta
        if self.__HScroll.get() != (0.0, 1.0):
            if platform.system() == "Linux":
                if event.num == 5:
                    delta = -1
                elif event.num == 4:
                    delta = 1
                self.__Canvas.xview_scroll( int(-1 * delta), "units" )
            else:       
                self.__Canvas.xview_scroll( int(-1 * (event.delta/120)), "units" )


if __name__ == "__main__":
    main = Tk()
    main.minsize(30,30)
    test = ScrollableFrame(master=main, anchor="nw")
    test.pack(side=LEFT,fill=BOTH, expand=1)
    test.grid_columnconfigure(0, weight=1)
    for i in range(25):
        label = Label(master=test.get_attach_point(), text=str(i))
        label["bg"] = "red"
        label.grid(row=i, column=i, sticky=E+W)

        
    main.mainloop()