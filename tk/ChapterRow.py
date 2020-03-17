#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ChapterRow.py                                                 #
#description     :Defines a ChapterRow widget for tkinter                       #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Defines a ChapterRow Widget for tkinter                       #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

try:
    from tkinter import  Button, Frame, Label, StringVar, Grid
    from tkinter import LEFT, RIGHT, DISABLED, NORMAL, E, W, X
    from tkinter import font
    from tkinter.ttk import Button, Frame, Label

except:
    from tkinter import  Button, Frame, Label, StringVar, Grid
    from tkinter import LEFT, RIGHT, DISABLED, NORMAL, E, W, X
    from tkinter import font
    from tkinter.ttk import Button, Frame, Label

import os

class ChapterRow(Frame):
    def __init__(self, title, stream, chapter,masterWindow=None, master=None,removecommand=None, downloadcommand=None,viewcommand=None,**kw):
        Frame.__init__(self, master=master, **kw)
        self.removecommand = removecommand
        self.downloadcommand = downloadcommand
        self.viewcommand = viewcommand
        self.parent = master
        self.parentWindow = masterWindow
        self.downloaded = False
        self.title = title
        self.stream=stream
        self.chapter=chapter
        self.Info = {
            "Remove" : StringVar(),
            "Download" : StringVar(),
            "View" : StringVar()
        }
        self.Info["Remove"].set("Remove")
        self.Info["Download"].set("Download")
        self.Info["View"].set("Veiw")
        self.chapter_path = title.save_location + "/" + title.get_directory() +'/'+ stream.get_directory()
        self.__ChapterNumber= chapter.get_chapter_number()
        self.__chapterLabel = Label(master=self,
                                    text="Chapter " +
                                    str(chapter.get_chapter_number()) + " : " +
                                    chapter.get_chapter_name())
        self.__viewButton = Button(master=self, textvariable=self.Info["View"],command=self.__on_view, width=4)
        self.__downloadButton = Button(master=self, textvariable=self.Info["Download"], command=self.__on_download, width=13)
        self.__removeButton = Button(master=self, textvariable=self.Info["Remove"], command=self.__on_remove, width=8)
    
        if self.chapter.is_downloaded(self.chapter_path) == True:
            self.__removeButton["state"] = NORMAL
            self.__downloadButton["state"] = DISABLED
            self.Info["Download"].set( "Downloaded" )
            self.__viewButton["state"] = NORMAL
        else:
            self.__removeButton["state"] = DISABLED
            self.__downloadButton["state"] = NORMAL
            self.__viewButton["state"] = DISABLED

        if self.parentWindow._current_task["Chapter"] != None:
            if self.parentWindow._current_task["Chapter"][4] == hash(self):
                self.update_state("remove", "Remove" )
                self.update_state("download", "Downloading...")
                self.update_state("view", "View")
            elif self.parentWindow.in_chapter_queue( hash(self) ) == True:
                    self.update_state("remove", "Remove")
                    self.update_state("download", "pending...")
                    self.update_state("view", "View")   


    def __hash__(self):
        return hash( (self.title, self.stream, self.chapter) )

    def __on_view(self):
        """Signal catcher for the view button
        """
        #print("view button pressed")
        if self.viewcommand != None:
            self.viewcommand(self.__ChapterNumber)

    def __on_download(self):
        """Singal catcher for the download button
        """
        #print("download button pressed")
        if self.downloadcommand != None:
            self.__downloadButton["state"] = DISABLED
            if len(self.parentWindow.ChapterQueue) > 0 or self.parentWindow._current_task["Chapter"] != None:
                self.update_state("download", "pending...", False)
            self.downloadcommand(self.title, self.stream, self.chapter, self.chapter_path)

    def __on_remove(self):
        """Signal catcher for the remove button
        """
        #print("remove button pressed")
        if self.removecommand != None:
            self.removecommand(self)
        #self.removecommand(self.__ChapterNumber)

    def update_state(self,button,text=None,active=False):
        """Updates the state and label text of the three main button
        
        Arguments:
            button {String} -- The name of the button to be changed
            text {String or None} -- The text to be displayed on the button, if None current text remains unchanged
        
        Keyword Arguments:
            active {bool} -- The state to change the tkinter button to (default: {False})
        """
        if button == "remove":
            if text != None:
                self.Info["Remove"].set(text)

            if active:
                self.__removeButton["state"] = NORMAL
            else:
                self.__removeButton["state"] = DISABLED
        elif button == "download":
            if text != None:
                self.Info["Download"].set(text)
            if active:
                self.__downloadButton["state"] = NORMAL
            else:
                self.__downloadButton["state"] = DISABLED
        elif button == "view":
            if text != None:
                self.Info["View"].set(text)
            if active:
                self.__viewButton["state"] = NORMAL
            else:
                self.__viewButton["state"] = DISABLED

    def set_is_downloaded(self, is_downloaded=False):
        """Sets the current download status of the chapter
        
        Keyword Arguments:
            is_downloaded {bool} -- The download status to change to (default: {False})
        """
        self.downloaded = is_downloaded

    def is_downloaded(self):
        """Returns the download status of the chapter the row is representing
        
        Returns:
            bool -- The download status
        """
        return self.downloaded

    def grid(self, **kwargs):
        """overloaded method of the grid method for placing the current object
        """
        self.__chapterLabel.grid(   row=0, column=0, columnspan=2,sticky=E+W, padx=2, pady=2)
        Grid.grid_columnconfigure(self, 0, weight=1)
        self.__removeButton.grid(   row=0, column=4, sticky=E, padx=2, pady=2)
        self.__downloadButton.grid( row=0, column=3, sticky=E, pady=2)
        self.__viewButton.grid(     row=0, column=2, sticky=E, pady=2)
        Frame.grid(self, kwargs)

    def pack(self, **kwargs):
        """overloaded method of the pack method for placing the current object
        """
        self.__chapterLabel.pack(side=LEFT, fill=X, expand=1)
        self.__viewButton.pack(side=RIGHT)
        self.__downloadButton.pack(side=RIGHT)
        self.__removeButton.pack(side=RIGHT)
        Frame.pack(self, kwargs)
