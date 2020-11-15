#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :QueueWindow.py                                                #
#description     :Defines a QueueWindow widget for tkinter                      #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :Defines a QueueWindow Widget for tkinter                      #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

try:
    from tkinter import Toplevel, Button, Frame, Label, StringVar, Grid
    from tkinter import LEFT, RIGHT, DISABLED, NORMAL, E, W, S, N, X, BOTH, TOP
    from tkinter import font
    from tkinter.ttk import Button, Frame, Label,Notebook

except:
    from tkinter import Toplevel, Button, Frame, Label, StringVar, Grid
    from tkinter import LEFT, RIGHT, DISABLED, NORMAL, E, W, S, N, X, BOTH, TOP
    from tkinter import font
    from tkinter.ttk import Button, Frame, Label,Notebook

import logging, os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/QueueWindow.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class QueueWindow(Toplevel):
    instance = None

    CHAPTER_QUEUE = 0
    UPDATE_QUEUE = 1

    def __init__(self, master=None,**kw):
        if QueueWindow.instance != None:
            logger.info("User tried to create another window")
        else:
            super().__init__(master=master,**kw)
            self.Queues = [self.master.ChapterQueue,self.master.UpdateTitleQueue]
            self.transient(master)
            self.protocol("WM_DELETE_WINDOW",self.__on_exit)
            self.minsize(200,300)
            self.signal_id = {}
            self.Widgets = {}

            self.Widgets["main frame"] = Frame(master=self)
            self.Widgets["Queue Notebook"] = Notebook(master=self.Widgets["main frame"])
            self.Widgets["Close Button"] = Button(master=self.Widgets["main frame"], text="Close")

            self.Widgets["Chapter Frame"] = Frame(master=self.Widgets["Queue Notebook"])
            self.Widgets["Update Frame"] = Frame(master=self.Widgets["Queue Notebook"])
            self._build()
            QueueWindow.instance = self

    def _build(self):
        #Update top Queue list
        self.update_queue(queue_id=QueueWindow.CHAPTER_QUEUE)
        self.Widgets["Queue Notebook"].grid(row=0,column=0,sticky=N+E+S+W)
        self.Widgets["Chapter Frame"].pack(fill=BOTH, expand=1)
        self.Widgets["Chapter Frame"]["relief"] = "sunken"
        self.Widgets["Update Frame"].pack(fill=BOTH, expand=1)
        self.Widgets["Close Button"].grid(row=1,column=1, sticky=E)
        self.Widgets["main frame"].pack(fill=BOTH, expand=1)
        self.Widgets["Close Button"].config(command=self.__on_exit)
        self.Widgets["Queue Notebook"].add(self.Widgets["Chapter Frame"], text="Chapter Downloads", compound=TOP)
        self.Widgets["Queue Notebook"].add(self.Widgets["Update Frame"], text="Title Updates")

    def __on_exit(self):
        QueueWindow.instance = None
        self.destroy()

    def update_queue(self, queue_id):
        if queue_id == QueueWindow.CHAPTER_QUEUE:
            if len( self.Queues[0] ) == 0:
                test = Label(master=self.Widgets["Chapter Frame"], text="No Active Downloads")
                test.grid(row=0, column=0, sticky="EW")
            else:
                for chapter in self.Queues[0]:
                    print(chapter[2].get_chapter_name())            
        elif queue_id == QueueWindow.UPDATE_QUEUE:
            pass
        else:
            pass

    class Queue_Task(Frame):
        def __init__(self, master=None, Title="Unknown", Status="Pending...", **kw):
            super().__init__(master=master, **kw)
            
            self.Status = StringVar()
            self.Status.set(Status)
            self.Widgets["Title"] = Label(master=self)
            self.Widgets["Status_Label"] = Label(master=self, textvariable=self.Status)
            self.Widgets["Cancel"] = Button(master=self)
            self._build()

        def _build(self):
            self.Widgets["Title"].grid(row=0,col=0,sticky="ew",fill=0, expand=1)
            self.Widgets["Statuc_Label"].grid(row=0,col=1)
            self.Widgets["Cancel"].grid(row=0,col=2,sticky="w",fill=0, expand=1)
