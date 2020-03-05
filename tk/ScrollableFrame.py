#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ScrollableFrame.py                                            #
#description     :Defines a Scrollable Frame widget for tkinter                 #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Defines a scrollable frame widget                             #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

from tkinter import Tk, Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, N, W, S, E, Label, Grid, Button
try:
    from DynamicCanvas import DynamicCanvas
except:
    from tk.DynamicCanvas import DynamicCanvas
#from tkinter.ttk import *

import platform

class ScrollableFrame(Frame):
    def __init__(self, master, vscrollside="right", hscrollside="bottom", *args, **kwargs):
        Frame.__init__(self, master=master, *args, **kwargs)
        self.__ScrollFrame = None
        self.__VScroll = None
        self.__HScroll = None
        self.__Canvas = None
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

    def pack(self, **kwargs):
        self.__CanvasFrame = Frame(master=self)
        self.__LesserFrame = Frame(master=self)
        self.__coner = Frame(master=self.__LesserFrame)
        self.__coner["width"] = 14
        self.__coner["height"] = 14
        self.__VScroll = Scrollbar(master=self.__CanvasFrame, orient="vertical" )
        self.__HScroll = Scrollbar(master=self.__LesserFrame, orient="horizontal")
        self.__Canvas = DynamicCanvas(master=self.__CanvasFrame, highlightthickness=0,
                                        yscrollcommand = self.__VScroll.set,
                                        xscrollcommand = self.__HScroll.set)
        self.__ScrollFrame = Frame(master=self.__Canvas)
        self.__VScroll.config(command = self.__Canvas.yview)
        self.__HScroll.config(command = self.__Canvas.xview)

        #self.__Canvas["bg"] = "red"
        #self.__ScrollFrame["bg"] = "green"

        self.__Canvas.pack(fill=BOTH, expand=1)

        if self.__CanvasPos[0] == 1:
            self.__LesserFrame.pack(side=TOP,fill=X,expand=1)
            self.__CanvasFrame.pack(side=TOP,fill=BOTH,expand=1)
        else:
            self.__CanvasFrame.pack(side=TOP,fill=BOTH,expand=1)
            self.__LesserFrame.pack(side=TOP,fill=X,expand=1)
            
        if self.__CanvasPos[1] == 1:
            self.__VScroll.pack(side=LEFT, fill=Y,expand=0)
            self.__Canvas.pack(side=LEFT, fill=BOTH,padx=5,pady=5,expand=1)

            self.__coner.pack(side=LEFT, fill=None, expand=0)
            self.__HScroll.pack(side=LEFT,fill=X,expand=0)
        else:
            self.__Canvas.pack(side=LEFT, fill=BOTH,padx=5,pady=5,expand=1)
            self.__VScroll.pack(side=LEFT, fill=Y,expand=0)
            
            self.__HScroll.pack(side=LEFT, fill=X, expand=1)
            self.__coner.pack(side=LEFT, fill="none", expand=0)

        self.__ScrollFrame.bind("<Configure>", self.scrollregion_change)

        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))
        self.__Canvas.create_window(self.__Canvas.width/2 + self.__ScrollFrame["width"] / 2 ,
                                    self.__Canvas.height/2 + self.__ScrollFrame["height"] / 2 ,
                                    window=self.__ScrollFrame, 
                                    anchor="c")

        Frame.pack(self, **kwargs)

    def grid(self, **kwargs):
        self.__VScroll = Scrollbar(master=self, orient="vertical" )
        self.__HScroll = Scrollbar(master=self, orient="horizontal")
        self.__Canvas = DynamicCanvas(master=self, highlightthickness=0,
                                        yscrollcommand = self.__VScroll.set,
                                        xscrollcommand = self.__HScroll.set)
        self.__ScrollFrame = Frame(master=self.__Canvas)
        self.__VScroll.config(command = self.__Canvas.yview)
        self.__HScroll.config(command = self.__Canvas.xview)

        Grid.rowconfigure(self, self.__CanvasPos[0], weight=1)
        Grid.columnconfigure(self,self.__CanvasPos[1],weight=1)

        self.__HScroll.grid(row=self.__HScrollPos[0], column=self.__HScrollPos[1],sticky=E+W)
        self.__VScroll.grid(row=self.__VScrollPos[0], column=self.__VScrollPos[1],sticky=N+S)
        self.__Canvas.grid(row=self.__CanvasPos[0], column=self.__CanvasPos[1],sticky=N+S+E+W)
        self.__ScrollFrame.bind("<Configure>", self.scrollregion_change)

        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))
        self.__Canvas.create_window(self.__Canvas.width/2 + self.__ScrollFrame["width"] / 2 ,
                                    self.__Canvas.height/2 + self.__ScrollFrame["height"] / 2,
                                    window=self.__ScrollFrame, 
                                    anchor="c")
        Frame.grid(self, **kwargs)

    def scrollregion_change(self,event):
        #print(event)
        self.__Canvas.configure(
            scrollregion=self.__Canvas.bbox("all")
        )

    def __on_enter(self, event):
        #print("Enter event")
        if platform.system() == "Windows":
            self.bind_all("<MouseWheel>", self.__on_mousewheel)
            self.bind_all("<Shift-MouseWheel>", self.__on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.bind_all("<Button-4>",self.__on_mousewheel)
            self.bind_all("<Button-5>",self.__on_mousewheel)
            self.bind_all("<Shift-Button-4>",self.__on_shift_mousewheel)
            self.bind_all("<Shift-Button-5>",self.__on_shift_mousewheel)

    def __on_leave(self,event):
        #print("Leave event")
        if platform.system() == "Windows":
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Shift-MouseWheel>")
        elif platform.system() == "Linux":
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
            self.unbind_all("<Shift-Button-4>")
            self.unbind_all("<Shift-Button-5>")
            
    def __on_mousewheel(self,event):
        #print(event)
        #print( event.delta )
        delta = event.delta
        if platform.system() == "Linux":
            if event.num == 5:
                delta = -1
            elif event.num == 4:
                delta = 1
            self.__Canvas.yview_scroll( int(-1 * delta), "units" )
        else:       
            self.__Canvas.yview_scroll( int(-1 * (event.delta/120)), "units" )

    def __on_shift_mousewheel(self,event):
        #print(event)
        #print( event.delta )
        delta = event.delta
        if platform.system() == "Linux":
            if event.num == 5:
                delta = -1
            elif event.num == 4:
                delta = 1
            self.__Canvas.xview_scroll( int(-1 * delta), "units" )
        else:       
            self.__Canvas.xview_scroll( int(-1 * (event.delta/120)), "units" )

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
        self.__ScrollFrame.grid_columnconfigure(index=index, weight=weight)

if __name__ == "__main__":
    main = Tk()
    main.minsize(30,30)
    test = ScrollableFrame(master=main)
    test.pack(side=LEFT,fill=BOTH, expand=1)
    
    for i in range(10):
        Label(master=test.get_attach_point(), text=str(i)).pack(side=TOP)#.grid(row=i, column=i)
    main.mainloop()