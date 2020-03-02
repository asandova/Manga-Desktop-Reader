#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :popups.py                                                     #
#description     :contains custom tkinter toplevel windows                      #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-2-1                                                      #
#version         :0.1                                                           #
#usage           :defines mulitple custom tkinter toplevel windows              #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
try:
    from tkinter import Tk, Toplevel, Label, Button, Frame, Canvas, Grid, X,Y,E,W,N,S, BOTH,TOP, StringVar, Text, END
    from tkinter.ttk import *
except:
    from Tkinter import Tk, Toplevel, Label, Button, Frame, Canvas, Grid, X,Y,E,W,N,S, BOTH,TOP, StringVar, Text,END
    from Tkinter.ttk import *

try:
    from ScrollableFrame import ScrollableFrame
except:
    from tk.ScrollableFrame import ScrollableFrame

class add_Window(Toplevel):
    def __init__(self, master=None,OKCommand=None, CancelCommand=None,**kw):
        Toplevel.__init__(self, master=master, **kw)
        self.transient(master)
        self.title("Add title")
        self.result = None
        self.minsize(200,80)
        self.AcceptCommand = OKCommand
        self.CancelCommand = CancelCommand
        self.Value = StringVar()
        self.__Frame = LabelFrame(master=self, text="Enter URL")
        self.__Entry = Entry(master=self.__Frame, textvariable = self.Value)
        self.__Accept = Button(master=self.__Frame, command=self.Accept, text="OK")
        self.__Cancel = Button(master=self.__Frame, command=self.Cancel, text="Cancel")

        self.__Frame.pack(fill=BOTH,expand=1, pady=2, padx=2)
        self.__Entry.grid(row=0, column=0, columnspan=3, sticky=E+W)
        self.__Accept.grid(row=1, column=1, padx=2, pady=2)
        self.__Cancel.grid(row=1, column=2, padx=2, pady=2)
        Grid.grid_columnconfigure(self.__Frame, 0, weight=1)
        self.resizable(1,0)

    def Accept(self):
        print("Accept button pressed")
        print( "\"" + self.Value.get()+ "\"")
        if self.AcceptCommand != None:
            self.AcceptCommand(self.Value.get())
        self.destroy()

    def Cancel(self):
        print("Cancel Button pressed")
        if self.CancelCommand != None:
            self.CancelCommand()
        self.destroy()

class about_dialog(Toplevel):
    Verdana_Normal_10 = ("verdana", 10, "normal")
    Verdana_Bold_10 = ("verdana", 10, "bold")
    def __init__(self, master=None, **kw):
        Toplevel.__init__(self, master=master,**kw)
        self.transient(master)
        self.title("About")
        self.minsize(350,200)
        self.maxsize(500,500)
        self.frame = Frame(master=self)
        self.frame.pack(fill=BOTH, expand=1)
        self.show = False
        Grid.grid_columnconfigure(self.frame,0, weight=1)
        Grid.grid_rowconfigure(self.frame,5, weight=1)
        self.info = {
            "version" : StringVar(),
            "Notice" : StringVar(),
            "Name" : StringVar(),
            "Copyright" : StringVar(),
            "License" : StringVar()
        }
        self.info["version"].set("Version 0.1b1")
        self.info["Notice"].set("NOTICE:\nAll Manga/Comics viewed within this application\nbelong to their respective owner(s).")
        self.info["Name"].set("Manga Reader")
        self.info["Copyright"].set("Copyright (c) 2020 August B. Sandoval")
        self.info["License"].set("MIT License\n\nCopyright (c) 2020 August B. Sandoval\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")


        self.Icon = Canvas(master=self.frame, width=50, height=50)
        self.versionLabel = Label(master=self.frame,textvariable=self.info["version"], font=about_dialog.Verdana_Normal_10)
        self.NoticeLabel = Label(master=self.frame, textvariable=self.info["Notice"], font=about_dialog.Verdana_Normal_10)
        self.NoticeLabel["justify"] = "center"
        self.NameLabel = Label(master=self.frame, textvariable=self.info["Name"], font=about_dialog.Verdana_Bold_10)
        self.copyright = Label(master=self.frame, textvariable=self.info["Copyright"], font=about_dialog.Verdana_Normal_10)
        self.licence = Text(master=self.frame, font=about_dialog.Verdana_Normal_10)
        self.licence["wrap"] = "word"
        self.licence.insert(END, self.info["License"].get())
        self.licence["state"] = "disabled"
        self.closeButton = Button(master=self.frame,command=self.close,text="Close")
        self.licenseButton = Button(master=self.frame, command=self.showLicense, text="License")

        self.Icon.grid(         row=0,column=0,columnspan=3)
        self.NameLabel.grid(    row=1,column=0,columnspan=3)
        self.versionLabel.grid( row=2,column=0,columnspan=3)
        self.NoticeLabel.grid(  row=3,column=0,columnspan=3)
        self.copyright.grid(    row=4,column=0,columnspan=3)
        #self.licence.grid(      row=5,column=0,columnspan=3,sticky=W+E+N+S)
        self.closeButton.grid(  row=6,column=2)
        self.licenseButton.grid(  row=6,column=1)
    
    def close(self):
        self.destroy()

    def showLicense(self):
        self.show = not self.show
        if self.show:
            self.licence.grid( row=5,column=0,columnspan=3,sticky=W+E+N+S)
        else:
            self.licence.grid_forget()

if __name__ == "__main__":
    root = Tk()
    root.style = Style()
    root.style.theme_use("clam")
    about = about_dialog(master=root)
    root.mainloop()