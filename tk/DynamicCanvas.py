#!/usr/bin/python3
# -*- coding: utf-8 -*-

from tkinter import Tk ,Canvas, Frame, BOTH
#from tkinter.ttk import *

class DynamicCanvas(Canvas):
    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self,master=master, *args, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self["highlightthickness"] = 0
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        self.scale("all",0,0,wscale,hscale )

if __name__ == "__main__":
    main = Tk()
    testFrame = Frame(main)
    #testFrame.pack(fill=BOTH, expand=1)
    testFrame.grid(row=0, column=0,sticky="nesw")
    main.grid_columnconfigure(0, weight=1)
    testCanvas = DynamicCanvas(master=testFrame, width=850, height=400, highlightthickness=0)
    testCanvas["bg"] = "orange"
    testCanvas.pack(fill=BOTH, expand=1)
    main.mainloop()