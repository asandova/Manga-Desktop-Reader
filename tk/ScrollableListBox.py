#!/usr/bin/python3
try:
    from Tkinter import *
    from Tkinter.ttk import *
except ImportError:
    from tkinter import *
    from tkinter.ttk import *


class ScrollableListbox(Frame):
    def __init__(self, master, vscrollside="right", hscrollside="bottom",*args, **kwargs):
        Frame.__init__(self, master=master, *args, **kwargs)
        self.grid()
        self.__HScroll = Scrollbar(master=self, orient="horizontal")
        self.__VScroll = Scrollbar(master=self, orient="vertical")
        self.__ListBox = Listbox(master=self,yscrollcommand=self.__VScroll.set, xscrollcommand=self.__HScroll.set)
        self.__listpos = [0,0]
        self.__VScrollPos = [0,1]
        self.__HScrollPos = [1,0]

        if vscrollside == "right":
            self.grid_columnconfigure(0,weight=1)
            self.grid_columnconfigure(1,weight=0)
            self.__listpos[1] = 0
            self.__VScrollPos[1] = 1 
            self.__HScrollPos[1] = 0

        elif vscrollside == "left":
            self.grid_columnconfigure(0,weight=0)
            self.grid_columnconfigure(1,weight=1)
            self.__listpos[1] = 1
            self.__VScrollPos[1] = 0 
            self.__HScrollPos[1] = 1
            
        if hscrollside == "bottom":
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1,weight=0)
            self.__listpos[0] = 0
            
        elif hscrollside == "top":
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1,weight=1)
            self.__listpos[0] = 1


        self.__VScroll.grid(row=self.__VScrollPos[0],column=self.__VScrollPos[1],sticky=N+S)    
        self.__HScroll.grid(row=self.__HScrollPos[0],column=self.__HScrollPos[1],sticky=E+W)
        self.__ListBox.grid(row=self.__listpos[0],column=self.__listpos[1],sticky=E+W+S+N)



    def add_entry(self):
        pass
    def remove_entry(self):
        pass
if __name__ == "__main__":
    main = Tk()
    test = ScrollableListbox(master=main)
    test.pack(side=LEFT, expand=1,fill=BOTH)
    main.mainloop()