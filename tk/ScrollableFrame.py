#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import Tk, Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH, N, W, S, E, Label
#from tkinter.ttk import *

class ScrollableFrame(Frame):
    def __init__(self, master, vscrollside="right", hscrollside="bottom", *args, **kwargs):
        Frame.__init__(self, master=master, *args, **kwargs)
        self.grid()
        self.grid_propagate(True)
        #initializes internal widgets
        self.__Canvas = Canvas(master=self)
        self.__ScrollFrame = Frame(master=self.__Canvas)
        self.__VScroll = Scrollbar(master=self, orient="vertical"  ,command=self.__Canvas.yview)
        self.__HScroll = Scrollbar(master=self, orient="horizontal",command=self.__Canvas.xview)
        
        self.__Canvas["bg"] = "red"
        self.__ScrollFrame["bg"] = "green"
        #position arrays, stores the position for all widgets withing the parent frames grid
        #[row, col]
        self.__CanvasPos= [0,0]
        self.__VScrollPos=[0,1]
        self.__HScrollPos=[1,0]

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)


        if vscrollside == "right":
            #self.grid_columnconfigure(0, weight=1)
            #self.grid_columnconfigure(1, weight=0)
            self.__CanvasPos[1]  = 0
            self.__VScrollPos[1] = 1 
            self.__HScrollPos[1] = 0

        elif vscrollside == "left":
            #self.grid_columnconfigure(0, weight=0)
            #self.grid_columnconfigure(1, weight=1)
            self.__CanvasPos[1]  = 1
            self.__VScrollPos[1] = 0 
            self.__HScrollPos[1] = 1
            
        if hscrollside == "bottom":
            #self.grid_rowconfigure(0, weight=1)
            #self.grid_rowconfigure(1, weight=0)
            self.__CanvasPos[0]  = 0
            self.__HScrollPos[0] = 1
            self.__VScrollPos[0] = 0
            
        elif hscrollside == "top":
            #self.grid_rowconfigure(0, weight=0)
            #self.grid_rowconfigure(1, weight=1)
            self.__CanvasPos[0]  = 1
            self.__HScrollPos[0] = 0
            self.__VScrollPos[0] = 1

        self.__ScrollFrame.bind(
            "<Configure>",
            lambda e: self.__Canvas.configure(
                scrollregion=self.__Canvas.bbox("all")
            )
        )

        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        #self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))

        self.__Canvas.grid( row=self.__CanvasPos[0], column=self.__CanvasPos[1], sticky=N+S+E+W)
        self.__VScroll.grid(row=self.__VScrollPos[0],column=self.__VScrollPos[1],sticky=N+S+E+W)
        self.__HScroll.grid(row=self.__HScrollPos[0],column=self.__HScrollPos[1],sticky=N+S+E+W)

        self.__Canvas.create_window( (0,0), window=self.__ScrollFrame, anchor="nw" )
        #self.__ScrollFrame.pack(fill=BOTH, expand=1)
        

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

class ScrollableFramePack(Frame):
    def __init__(self, master ,*args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.__toprowContainer = Frame(master=self)
        self.__bottomrowContainer = Frame(master=self)
        self.__toprowContainer.pack(side=TOP, expand=1,fill=BOTH)
        self.__bottomrowContainer.pack(side=TOP, expand=0,fill=X)

        self.__Coner = Frame(master=self.__bottomrowContainer)
        self.__Coner["width"] = 13
        self.__Coner["height"] = 13
        self.__Canvas = Canvas(master=self.__toprowContainer)
        self.__Canvas["bg"] = "red"
        self.__ScrollFrame = Frame(master=self.__Canvas)
        self.__VScroll = Scrollbar(master=self.__toprowContainer, orient="vertical",command=self.__Canvas.yview)
        self.__HScroll = Scrollbar(master=self.__bottomrowContainer, orient="horizontal",command=self.__Canvas.xview)

        self.__ScrollFrame.bind(
            "<Configure>",
            lambda e: self.__Canvas.configure(
                scrollregion=self.__Canvas.bbox("all")
            )
        )

        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        self.__Canvas.pack(side=LEFT,expand=1,fill=BOTH)
        self.__VScroll.pack(side=LEFT,expand=0,fill=Y)
        self.__Coner.pack(side=RIGHT,expand=0)
        self.__HScroll.pack(side=RIGHT, expand=1,fill=X)

        self.__Canvas.create_window((0,0), window=self.__ScrollFrame, anchor="nw")
        self.__ScrollFrame.pack(fill=BOTH,expand=1)
        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))

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
    main.minsize(500,500)
    test = ScrollableFramePack(master=main)
    test["bg"] = "blue"
    test.pack(side=LEFT,fill=BOTH, expand=1)
    for i in range(50):
        Label(master=test.get_attach_point(), text=str(i)).pack()
    #test.grid(row=0, column=0, sticky=N+E+S+W  )
    #main.grid_columnconfigure(0, weight=1)
    #main.grid_rowconfigure(0, weight=1)
    main.mainloop()