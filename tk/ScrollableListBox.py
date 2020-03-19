#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ScrollableListBox.py                                          #
#description     :Defines a acrollable Listbox widget for tkinter               #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :Defines a acrollable Listbox widget                           #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

try:
    from Tkinter import Tk, Frame, Scrollbar, Listbox ,LEFT, RIGHT, TOP, BOTTOM, BOTH, N, E, S ,W, Grid, SINGLE, END
    from Tkinter.ttk import *
except ImportError:
    from tkinter import Tk, Frame, Scrollbar, Listbox ,LEFT, RIGHT, TOP, BOTTOM, BOTH, N, E, S ,W, Grid, SINGLE, END
    from tkinter.ttk import *
    
import platform

class ScrollableListbox(Frame):
    def __init__(self, master, vscrollside="right", hscrollside="bottom", selectmode=SINGLE,command=None,*args, **kwargs):
        Frame.__init__(self, master=master, *args, **kwargs)
        self.mode = selectmode
        self.command = command
        self.__TitleList = []
        self.__HScroll= None
        self.__VScroll = None
        self.__ListBox = None
        self.__listpos = [0,0]
        self.__VScrollPos = [0,1]
        self.__HScrollPos = [1,0]

        if vscrollside == "right":
            self.__listpos[1] = 0
            self.__VScrollPos[1] = 1 
            self.__HScrollPos[1] = 0

        elif vscrollside == "left":
            self.__listpos[1] = 1
            self.__VScrollPos[1] = 0 
            self.__HScrollPos[1] = 1
            
        if hscrollside == "bottom":
            self.__listpos[0] = 0
            self.__HScrollPos[0] = 1
            self.__VScrollPos[0] = 0
            
        elif hscrollside == "top":
            self.__listpos[0] = 1
            self.__HScrollPos[0] = 0
            self.__VScrollPos[0] = 1

    def insert(self, title):
        """Inserts title into the listbox
        
        Arguments:
            title {string} -- the string to be display into the list
        """
        position = self.__find_insertion_point(title)
        if position == -1:
            position = END
        self.__ListBox.insert(position, title)

    def delete(self, title):
        """Removes the title from from the listbox
        
        Arguments:
            title {string} -- the title to be removed
        
        Returns:
            bool -- returns 1 if title is not in list, else 0
        """
        for i in range(0, len(self.__TitleList)):
            if self.__TitleList[i] == title:
                self.__TitleList.remove(title)
                self.__ListBox.delete(i)
                return 0
        return 1
        
    def remove_all(self):
        """Removes all entries in the list
        """
        self.__TitleList = []
        self.__ListBox.delete(0,self.__ListBox.size())

    def __find_insertion_point(self, text):
        """Finds the current alphabetical placement of the title
        
        Arguments:
            text {string} -- string being entered
        
        Returns:
            int -- index the title should be placed, -1 is end of list
        """
        l = self.__TitleList
        l.append(text)
        l.sort()
        for i in range(0, len(l)):
            if l[i] == text:
                return i
        return -1

    def grid(self, **kwargs):
        self.__HScroll = Scrollbar(master=self, orient="horizontal")
        self.__VScroll = Scrollbar(master=self, orient="vertical")
        self.__ListBox = Listbox(   master=self, 
                                    yscrollcommand=self.__VScroll.set, 
                                    xscrollcommand=self.__HScroll.set
                                    )
        self.__ListBox["selectmode"] = self.mode
        self.__ListBox.bind(
            '<<ListboxSelect>>', self._on_select
        )
        self.__VScroll.config(command=self.__ListBox.yview)
        self.__HScroll.config(command=self.__ListBox.xview)
        Grid.grid_columnconfigure(self, self.__listpos[1], weight=1)
        Grid.grid_rowconfigure(self, self.__listpos[0], weight=1)

        self.__VScroll.grid( row=self.__VScrollPos[0], column=self.__VScrollPos[1], sticky=N+S)    
        self.__HScroll.grid( row=self.__HScrollPos[0], column=self.__HScrollPos[1], sticky=E+W)
        self.__ListBox.grid( row=self.__listpos[0],    column=self.__listpos[1],    sticky=E+W+S+N)
        
        self.__ListBox.bind("<Enter>", self._on_enter)
        self.__ListBox.bind("<Leave>", self._on_leave)

        if platform.system() == "Windows":
            self.__ListBox.bind("<MouseWheel>", self._on_mousewheel)
            self.__ListBox.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.__ListBox.bind("<Button-4>",self._on_mousewheel)
            self.__ListBox.bind("<Button-5>",self._on_mousewheel)
            self.__ListBox.bind("<Shift-Button-4>",self._on_shift_mousewheel)
            self.__ListBox.bind("<Shift-Button-5>",self._on_shift_mousewheel)
        
        Frame.grid(self, **kwargs)

    def pack(self, **kwargs):
        self.__ScrollRow = Frame(master=self)
        self.__ListRow = Frame(master=self)

        self.__VScroll = Scrollbar( master=self.__ListRow, orient="vertical")
        self.__HScroll = Scrollbar( master=self.__ScrollRow, orient="horizontal")
        self.__ListBox = Listbox(   master=self.__ListRow, 
                                    yscrollcommand=self.__VScroll.set,
                                    xscrollcommand=self.__HScroll.set
                                )

        self.__ListBox.bind(
            '<<ListboxSelect>>', self._on_select
        )
        self.__ListBox["selectmode"] = self.mode
        self.__VScroll.config(command=self.__ListBox.yview)
        self.__HScroll.config(command=self.__ListBox.xview)
        self.__Coner = Frame(master=self.__ScrollRow)
        self.__Coner["width"] = 14
        self.__Coner["height"] = 14

        if self.__listpos[0] == 1:
            self.__ScrollRow.pack(side=TOP,fill="x",expand=0)
            self.__ListRow.pack(side=TOP, fill=BOTH, expand=1)
        else:
            self.__ListRow.pack(side=TOP, fill=BOTH, expand=1)
            self.__ScrollRow.pack(side=TOP,fill="x",expand=0)

        if self.__listpos[1] == 1:
            self.__VScroll.pack(side=LEFT, fill="y", expand=0)
            self.__ListBox.pack(side=LEFT, fill=BOTH, expand=1)

            self.__Coner.pack(side=LEFT, fill="none", expand=0)
            self.__HScroll.pack(side=LEFT, fill="x", expand=1)
        else:
            self.__ListBox.pack(side=LEFT, fill=BOTH, expand=1)
            self.__VScroll.pack(side=RIGHT, fill="y", expand=0)

            self.__HScroll.pack(side=LEFT, fill="x", expand=1)
            self.__Coner.pack(side=LEFT, fill="none", expand=0)

        self.__ListBox.bind("<Enter>", self._on_enter)
        self.__ListBox.bind("<Leave>", self._on_leave)

        if platform.system() == "Windows":
            self.__ListBox.bind("<MouseWheel>", self._on_mousewheel)
            self.__ListBox.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.__ListBox.bind("<Button-4>",self._on_mousewheel)
            self.__ListBox.bind("<Button-5>",self._on_mousewheel)
            self.__ListBox.bind("<Shift-Button-4>",self._on_shift_mousewheel)
            self.__ListBox.bind("<Shift-Button-5>",self._on_shift_mousewheel)        

        Frame.pack(self,**kwargs)

    # Signal callback methods ---------------------------------------------------------------#

    def _on_enter(self, event):
        """Signal catcher of mouse enter event
        
        Arguments:
            event {tkinter event} -- tkinter mouse enter event
        """
        if platform.system() == "Windows":
            self.__ListBox.bind("<MouseWheel>", self._on_mousewheel)
            self.__ListBox.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        elif platform.system() == "Linux":
            self.__ListBox.bind("<Button-4>",self._on_mousewheel)
            self.__ListBox.bind("<Button-5>",self._on_mousewheel)
            self.__ListBox.bind("<Shift-Button-4>",self._on_shift_mousewheel)
            self.__ListBox.bind("<Shift-Button-5>",self._on_shift_mousewheel)

    def _on_leave(self,event):
        """Signal catcher of mouse exit event
        
        Arguments:
            event {tkinter event} -- tkinter mouse exit event
        """
        if platform.system() == "Windows":
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Shift-MouseWheel>")
        elif platform.system() == "Linux":
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
            self.unbind_all("<Shift-Button-4>")
            self.unbind_all("<Shift-Button-5>")

    def _on_mousewheel(self,event):
        """Signal catcher for mousewheel event
        
        Arguments:
            event {tkinter event} -- tkinter mousewheel event
        """
        delta = event.delta
        if platform.system() == "Linux":
            if event.num == 5:
                delta = -1
            elif event.num == 4:
                delta = 1
            self.__ListBox.yview_scroll( int(-1 * delta), "units" )
        else:       
            self.__ListBox.yview_scroll( int(-1 * (event.delta/120)), "units" )

    def _on_shift_mousewheel(self,event):
        """Signal catcher for shift mousewheel event
        
        Arguments:
            event {tkinter event} -- tkinter shift mousewheel event
        """
        delta = event.delta
        if platform.system() == "Linux":
            if event.num == 5:
                delta = -1
            elif event.num == 4:
                delta = 1
            self.__ListBox.xview_scroll( int(-1 * delta), "units" )
        else:       
            self.__ListBox.xview_scroll( int(-1 * (event.delta/120)), "units" )


    def _on_select(self, event):
        """Signal catcher for listbox selection event
        
        Arguments:
            event {tkinter event} -- tkinter listbox selection event
        """
        if len(self.__ListBox.curselection()) > 0:
            index = int(self.__ListBox.curselection()[0])
            value = self.__ListBox.get(index)
            self.command( (index, value) )

if __name__ == "__main__":
    main = Tk()
    test = ScrollableListbox(master=main, hscrollside="top")
    #test.grid(row=0, column=0, sticky=N+E+S+W)
    #main.grid_rowconfigure(0, weight=1)
    #main.grid_columnconfigure(0, weight=1)
    test.pack(side=LEFT, expand=1,fill=BOTH)
    for i in range(50):
        test.insert(str(i))
    main.mainloop()