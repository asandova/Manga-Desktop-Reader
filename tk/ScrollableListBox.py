#!/usr/bin/python3
try:
    from Tkinter import Tk, Frame, Scrollbar, Listbox ,LEFT, RIGHT, TOP, BOTTOM, BOTH, N, E, S ,W
    from Tkinter.ttk import Style
except ImportError:
    from tkinter import Tk, Frame, Scrollbar, Listbox ,LEFT, RIGHT, TOP, BOTTOM, BOTH, N, E, S ,W
    from tkinter.ttk import Style


class ScrollableListboxPack(Frame):
    pass
    #def add_entry(self):
    #    pass
    #def remove_entry(self):
    #    pass


class ScrollableListboxGrid(Frame):
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
            self.__HScrollPos[0] = 1
            self.__VScrollPos[0] = 0
            
        elif hscrollside == "top":
            self.grid_rowconfigure(0, weight=0)
            self.grid_rowconfigure(1,weight=1)
            self.__listpos[0] = 1
            self.__HScrollPos[0] = 0
            self.__VScrollPos[0] = 1

        self.__VScroll.grid(row=self.__VScrollPos[0],column=self.__VScrollPos[1],sticky=N+S)    
        self.__HScroll.grid(row=self.__HScrollPos[0],column=self.__HScrollPos[1],sticky=E+W)
        self.__ListBox.grid(row=self.__listpos[0],column=self.__listpos[1],sticky=E+W+S+N)

    def insert(self, position, text):
        self.__ListBox.insert(position, text)
    def remove_entry(self):
        pass


if __name__ == "__main__":
    main = Tk()
    test = ScrollableListboxGrid(master=main,hscrollside="top")
    #test.pack(side=LEFT, expand=1,fill=BOTH)
    main.mainloop()