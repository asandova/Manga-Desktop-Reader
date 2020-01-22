#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import Frame, Canvas, Scrollbar, LEFT, RIGHT, TOP, BOTTOM, X, Y, BOTH
#from tkinter.ttk import *

class ScrollableFrame_grid(Frame):
    def __init__(self, master ,*args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.grid()
        self.Widgets = {}
        self.__Canvas = Canvas(master=self)
        #self.__Canvas["bg"] = "red"
        self.__ScrollFrame = Frame(master=self.__Canvas)
        self.__VScroll = Scrollbar(master=self, orient="vertical",command=self.__Canvas.yview)
        self.__HScroll = Scrollbar(master=self, orient="horizontal",command=self.__Canvas.xview)

        self.grid_columnconfigure(0,weight=1)
        self.grid_columnconfigure(1,weight=0)
        self.grid_rowconfigure(1,weight=0)
        self.grid_rowconfigure(0,weight=1)
        self.__Canvas.grid(row=0, column=0,sticky="nwse")

        self.__ScrollFrame.bind(
            "<Configure>",
            lambda e: self.__Canvas.configure(
                scrollregion=self.__Canvas.bbox("all")
            )
        )

        self.__Canvas.configure(yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        self.__VScroll.grid(row=0,column=1,sticky="nsw")
        self.__HScroll.grid(row=1,column=0,sticky="swe")

        self.__Canvas.create_window( (0,0), window=self.__ScrollFrame, anchor="nw" )
        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))

    def get_attach_point(self):
        return self.__ScrollFrame

class ScrollableFrame_pack(Frame):
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
        self.__Canvas.configure(scrollregion=self.__Canvas.bbox("all"))

    def get_attach_point(self):
        return self.__ScrollFrame