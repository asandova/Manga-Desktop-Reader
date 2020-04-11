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
        self.__EntryList = []
        self.__HScroll= None
        self.__VScroll = None
        self.__ListBox = None
        self.__listpos = [0,0]
        self.__VScrollPos = [0,1]
        self.__HScrollPos = [1,0]

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

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
        self.scrollregion_change()

    def delete(self, entry):
        """Removes the title from from the listbox
        
        Arguments:
            title {string or int} -- the title to be removed
        
        Returns:
            bool -- returns 1 if title is not in list, else 0
        """
        if type(entry) == str:
            for i in range(0, len(self.__EntryList)):
                if self.__EntryList[i] == entry:
                    self.__EntryList.remove(entry)
                    self.__ListBox.delete(i)
                    return 0
        elif type(entry) == int:
            self.__EntryList.remove(self.__EntryList[entry])
            self.__ListBox.delete(entry)
            return 0
        return 1

    def get_list(self):
        return self.__EntryList

    def remove_all(self):
        """Removes all entries in the list
        """
        self.__EntryList = []
        self.__ListBox.delete(0,self.__ListBox.size())

    def __find_insertion_point(self, text):
        """Finds the current alphabetical placement of the title
        
        Arguments:
            text {string} -- string being entered
        
        Returns:
            int -- index the title should be placed, -1 is end of list
        """
        l = self.__EntryList
        l.append(text)
        l.sort()
        for i in range(0, len(l)):
            if l[i] == text:
                return i
        return -1

    def _build(self):
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

        if self.__HScroll.get() != (0.0, 1.0):
            self.__HScroll.grid(row=self.__HScrollPos[0], column=self.__HScrollPos[1],sticky=E+W)
        if self.__VScroll.get() != (0.0, 1.0):
            self.__VScroll.grid(row=self.__VScrollPos[0], column=self.__VScrollPos[1],sticky=N+S)

        Grid.grid_columnconfigure(self, self.__listpos[1], weight=1)
        Grid.grid_rowconfigure(self, self.__listpos[0], weight=1)

        self.__ListBox.grid( row=self.__listpos[0],    column=self.__listpos[1],    sticky=E+W+S+N)
        self.__ListBox.bind("<Configure>", self.scrollregion_change)

    def grid(self, **kwargs):
        self._build()
        Frame.grid(self, **kwargs)

    def pack(self, **kwargs):
        self._build()        
        Frame.pack(self,**kwargs)

    def scrollregion_change(self, event=None):
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
        if self.__VScroll.get() != (0.0, 1.0):
            if self.__VScroll.winfo_ismapped() == False:
                self.__VScroll.grid(row=self.__VScrollPos[0], column=self.__VScrollPos[1],sticky=N+S)
            
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
        if self.__HScroll.get() != (0.0, 1.0):
            if self.__HScroll.winfo_ismapped() == False:
                self.__HScroll.grid(row=self.__HScrollPos[0], column=self.__HScrollPos[1],sticky=E+W)

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
        if self.command != None:
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