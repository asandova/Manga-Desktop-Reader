#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :popups.py                                                     #
#description     :contains custom tkinter toplevel windows                      #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :defines mulitple custom tkinter toplevel windows              #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
try:
    from tkinter import Tk, Toplevel, Label, Button, Frame, LabelFrame, Entry, Listbox, Canvas, Grid, X,Y,E,W,N,S, BOTH,TOP, StringVar, Text, END, filedialog, DISABLED
    from tkinter.ttk import Style, Label, Button, Frame, LabelFrame, Notebook, Combobox, Style
except:
    from Tkinter import Tk, Toplevel, Label, Button, Frame, LabelFrame, Entry, Listbox, Canvas, Grid, X,Y,E,W,N,S, BOTH,TOP, StringVar, Text, END, filedialog, DISABLED
    from Tkinter.ttk import Style, Label, Button, Frame, LabelFrame, Notebook, Combobox, Style

try:
    from ScrollableFrame import ScrollableFrame
    from ScrollableListBox import ScrollableListbox
except:
    from tk.ScrollableFrame import ScrollableFrame
    from tk.ScrollableListBox import ScrollableListbox

import os, sys, platform

class add_Window(Toplevel):
    Verdana_Normal_12 = ("verdana", 12, "normal")
    def __init__(self, master=None,OKCommand=None, CancelCommand=None,**kw):
        Toplevel.__init__(self, master=master, **kw)
        self.transient(master)
        self.title("Add Title")
        self.result = None
        self.minsize(300,100)
        self.geometry("345x120+%d+%d" % (
                master.winfo_rootx() + (master.winfo_width()/2 - 125) ,
                master.winfo_rooty() + (master.winfo_height()/2 - 80)
            )
        )
        self.protocol("WM_DELETE_WINDOW",self._on_close)
        self.AcceptCommand = OKCommand
        self.CancelCommand = CancelCommand
        self.Value = StringVar()
        
        self.__Frame = LabelFrame(master=self )
        self.__FrameLabel = Label(master= self.__Frame, text="Enter URL to title page\nSeparate mulitple URLs with comma (\",\")")
        self.__FrameLabel["font"] = add_Window.Verdana_Normal_12
        self.__Frame["labelwidget"] = self.__FrameLabel
        self.__Entry = Entry(master=self.__Frame, textvariable = self.Value)
        self.__Accept = Button(master=self.__Frame, command=self.Accept, text="OK",width=3)
        self.__Cancel = Button(master=self.__Frame, command=self.Cancel, text="Cancel", width=6)

        self.__Frame.pack(fill=BOTH,expand=1, pady=2, padx=2)
        self.__Entry.grid(row=0, column=0, columnspan=3, sticky=E+W)
        self.__Accept.grid(row=1, column=1, padx=2, pady=2)
        self.__Cancel.grid(row=1, column=2, padx=2, pady=2)
        Grid.grid_columnconfigure(self.__Frame, 0, weight=1)
        self.resizable(1,0)

    def _on_close(self):
        self.destroy()

    def Accept(self):
        #print("Accept button pressed")
        #print( "\"" + self.Value.get()+ "\"")
        if self.AcceptCommand != None:
            self.AcceptCommand(self.Value.get())
        self.destroy()

    def Cancel(self):
        #print("Cancel Button pressed")
        if self.CancelCommand != None:
            self.CancelCommand()
        self.destroy()


class PreferenceWindow(Toplevel):
    Verdana_Normal_12 = ("verdana", 12, "normal")
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.transient(master)
        self.title("Preferences")
        self.minsize(500,300)
        self.maxsize(600, 500)
        self.geometry("345x120+%d+%d" % (
                master.winfo_rootx() + (master.winfo_width()/2 - 125) ,
                master.winfo_rooty() + (master.winfo_height()/2 - 80)
            )
        )
        self.parent = master
        self.Info = {
            "Download Loc" : StringVar(),
            "Driver Loc" : StringVar(),
            "status" : StringVar()
        }
        self.selection = {
            "Search" : {
                "Index" : -1,
                "Entry" : ""
            }
        }
        self.Info["Download Loc"].set( self.parent.appConfig["Default Download Location"])
        self.Info["Driver Loc"].set(self.parent.appConfig["Webdriver Location"])
        self.Widgets = {}
        self.Drivers = []
        self._build()

    def _build(self):
        self.Widgets["Window Frame"] = Frame(master=self)
        self.Widgets["Window Frame"].pack(fill=BOTH, expand=1)
        self.Widgets["Window Frame"].grid_columnconfigure(0,weight=1)
        self.Widgets["Window Frame"].grid_rowconfigure(0,weight=1)
        self.Widgets["Selection Notebook"] = Notebook(master=self.Widgets["Window Frame"])
        self.Widgets["Button Bar"] = Frame(master=self.Widgets["Window Frame"])
        self.Widgets["Button Bar"]["relief"] = "sunken"
        self.Widgets["Button Bar"].grid_columnconfigure(0, weight=1)
        self.Widgets["Status"] = Label(master=self.Widgets["Button Bar"],textvariable=self.Info["status"])
        self.Widgets["Close"] = Button(master=self.Widgets["Button Bar"], text="Close", command=self._on_close, width=5)

        self.Widgets["Status"].grid(row=0, column=0, sticky=E+W,padx=2)
        self.Widgets["Close"].grid(row=0, column=1, sticky=E)
        
        self.Widgets["General Frame"] = Frame(master=self.Widgets["Selection Notebook"])

        self.Widgets["Theme Frame"] = Frame(master=self.Widgets["General Frame"])
        self.Widgets["Theme Frame"]["relief"] = "ridge"
        self.Widgets["Theme Label"] = Label(master=self.Widgets["Theme Frame"], text="Theme", font=PreferenceWindow.Verdana_Normal_12)
        self.Widgets["Theme Combo"] = Combobox(master=self.Widgets["Theme Frame"])
        self.Widgets["Theme Combo"].bind( "<<ComboboxSelected>>", self._on_theme_select )
        
        self.Widgets["Theme Frame"].pack(side=TOP, fill=X, expand=0)
        self.Widgets["Theme Frame"].grid_columnconfigure(1, weight=1)
        self.Widgets["Theme Label"].grid(row=0, column=0,padx=5, pady=2 ,sticky=W)
        self.Widgets["Theme Combo"].grid(row=0, column=1,padx=5, sticky=E)

        self.Widgets["Theme Combo"].insert(0, self.parent.theme)
        themes = []
        for t in self.parent.style.theme_names():
            themes.append(t)
        self.Widgets["Theme Combo"]["values"] = themes       
        self.Widgets["Theme Combo"]["state"] = "readonly"

        self.Widgets["DL Frame"] = Frame(master=self.Widgets["General Frame"])
        self.Widgets["DL Frame"]["relief"] = "ridge"
        self.Widgets["DL Frame"].grid_columnconfigure(1,weight=1)
        self.Widgets["DL Label"] = Label( master=self.Widgets["DL Frame"], text="Download Location", font=PreferenceWindow.Verdana_Normal_12 )
        self.Widgets["DL Entry"] = Entry(master=self.Widgets["DL Frame"], font=PreferenceWindow.Verdana_Normal_12)
        self.Widgets["DL Button"] = Button(master=self.Widgets["DL Frame"], text="Browse", width=8, command=self._on_dl_browse)

        self.Widgets["DL Frame"].pack(side=TOP,fill=X, expand=0)
        self.Widgets["DL Label"].grid(row=0, column=0,padx=5)
        self.Widgets["DL Entry"].grid(row=0, column=1, sticky=E+W)
        self.Widgets["DL Entry"].insert(END, self.Info["Download Loc"].get())
        self.Widgets["DL Button"].grid(row=0, column=2, sticky=E)

        self.Widgets["SL Frame"] = Frame(master=self.Widgets["General Frame"])
        self.Widgets["SL Frame"]["relief"] = "ridge"
        self.Widgets["SL Frame"].grid_columnconfigure(1,weight=1)
        self.Widgets["SL Label"] = Label( master=self.Widgets["SL Frame"], text="Search Location(s)", font=PreferenceWindow.Verdana_Normal_12 )
        self.Widgets["SL Entry"] = Entry(master=self.Widgets["SL Frame"], font=PreferenceWindow.Verdana_Normal_12)
        self.Widgets["SL Add Button"] = Button(master=self.Widgets["SL Frame"], text="+", width=3, command=self._on_search_add)
        self.Widgets["SL Remove Button"] = Button(master=self.Widgets["SL Frame"], text="-", width=3, command=self._on_search_remove)
        self.Widgets["SL Browse Button"] = Button(master=self.Widgets["SL Frame"], text="Browse", width=8, command=self._on_sl_browse)
        self.Widgets["SL List"] = ScrollableListbox(master=self.Widgets["SL Frame"],command=self._on_search_select)

        self.Widgets["SL Frame"].pack(side=TOP,fill=X, expand=0)
        self.Widgets["SL Label"].grid(row=0, column=0, padx=5)
        self.Widgets["SL Entry"].grid(row=0, column=1, sticky=E+W)
        self.Widgets["SL Add Button"].grid(row=0, column=2, sticky=E)
        self.Widgets["SL Remove Button"].grid(row=0,column=3)
        self.Widgets["SL Browse Button"].grid(row=0, column=4)
        self.Widgets["SL List"].grid(row=1, column=0, sticky=N+E+S+W,columnspan=5, padx=10, pady=5)

        for l in self.parent.appConfig["Search Location(s)"]:
            self.Widgets["SL List"].insert(l)

        #self.Widgets["Plugin Frame"] = Frame(master=self.Widgets["Selection Notebook"])
        self.Widgets["Plugin Frame"] = ScrollableFrame( master=self.Widgets["Selection Notebook"], anchor="nw" )

        self.Widgets["Driver Frame"] = Frame(master=self.Widgets["Selection Notebook"])
        self.Widgets["Driver Location Frame"] = Frame(master=self.Widgets["Driver Frame"])
        self.Widgets["Driver Location Frame"].grid_columnconfigure(1, weight=1)
        self.Widgets["Driver Label"] = Label(master=self.Widgets["Driver Location Frame"], text="Driver Location", font=PreferenceWindow.Verdana_Normal_12)
        self.Widgets["Driver Entry"] = Entry(master=self.Widgets["Driver Location Frame"], font=PreferenceWindow.Verdana_Normal_12)
        self.Widgets["Driver Entry"].insert(END, self.Info["Driver Loc"].get())
        self.Widgets["Driver Button"] = Button(master=self.Widgets["Driver Location Frame"], text="Browse", width=8)

        self.Widgets["Driver Location Frame"].pack(side=TOP, fill=X, expand=0)
        self.Widgets["Driver Label"].grid( row=0, column=0, sticky=W )
        self.Widgets["Driver Entry"].grid( row=0, column=1, sticky=E+W )
        self.Widgets["Driver Button"].grid( row=0, column=2, sticky=E, padx=5 )

        self.update_driver_list()

        self.Widgets["General Frame"].pack(fill=BOTH, expand=1)
        self.Widgets["Plugin Frame"].pack(fill=BOTH, expand=1)

        self.Widgets["Plugin Frame"].grid_columnconfigure(index=0,weight=1)
        plugin_list = self.parent.PluginManager.get_plugin_list()
        for i in range(0, len(plugin_list)):
            discription = self.parent.PluginManager.get_plugin_by_name( plugin_list[i] ).TitlePlugin.description
            plugin = PreferenceWindow.PluginFrame(master=self.Widgets["Plugin Frame"].get_attach_point(), text=plugin_list[i], 
                discription=discription, command=self._on_reload)
            plugin["relief"] = "sunken"
            plugin.grid(row=i, column=0, sticky=E+W, padx=2)

        self.Widgets["Driver Frame"].pack(fill=BOTH, expand=1)

        self.Widgets["Selection Notebook"].add( self.Widgets["General Frame"], text="General", compound=TOP)
        self.Widgets["Selection Notebook"].add( self.Widgets["Plugin Frame"], text="Plugin")
        self.Widgets["Selection Notebook"].add( self.Widgets["Driver Frame"], text="Driver")

        self.Widgets["Selection Notebook"].grid(row=0,column=0,sticky=N+E+S+W)
        self.Widgets["Button Bar"].grid(row=1,column=0,sticky=E+W,padx=2,pady=2)

    def update_driver_list(self):
        driver_location = self.parent.appConfig["Webdriver Location"]
        browsers = os.listdir(driver_location)
        drivers = {}
        for b in browsers:
            print(b)
            if b.lower() == "chrome":
                print("Chrome Drivers found")
                drivers["Chrome"] = self.find_drivers(b, driver_location, "chromedriver")
            elif b.lower() == "firefox":
                print("Firefox Drivers looking")
                drivers["Firefox"] = self.find_drivers(b, driver_location, "geckodriver")                

        for d in drivers.keys():
            selected = ""
            if d == self.parent.appConfig["Browser"]:
                selected = self.parent.appConfig["Browser Version"]
            driver = PreferenceWindow.DriverFrame(master=self.Widgets["Driver Frame"], browser_name=d, version_list=drivers[d], selected_version=selected, command=self._on_driver_select )
            driver["relief"] = "ridge"
            driver.pack(side=TOP, fill=X, expand=0)
            if d == self.parent.appConfig["Browser"]:
                driver.set_active(False)
            self.Drivers.append(driver)

    def find_drivers(self, browser, path, drivername):
        version_list = []
        browser_path = os.path.join(path, browser)
        versions = os.listdir(browser_path)
        for v in versions:
            version_path = os.path.join(browser_path, v)
            suffix = ""
            p = platform.system()
            if p == "Windows":
                suffix = ".exe"
            elif p == "Linux":
                suffix = "_Linux"
            else:
                continue 
            if os.path.isfile( version_path + "/" + drivername + suffix ) == True:
                version_list.append(v)
        return version_list

    def _on_close(self, event=None):
        self.parent.appConfig["Search Location(s)"] = self.Widgets["SL List"].get_list()
        self.destroy()

    def _on_driver_select(self, data=None):
        for d in self.Drivers:
            if d.browser_name == data:
                if d.selected_version != "":
                    d.set_active(False)
                    self.parent.appConfig["Browser"] = data
                    self.parent.appConfig["Browser Version"] = d.selected_version
                else:
                    return
            else:
                d.set_active(True) 

    def _on_dl_browse(self, event=None):
        directory = filedialog.askdirectory(title="Choose download directory")
        if type( directory ) == str:
            self.Widgets["DL Entry"].delete(0, END)
            self.Widgets["DL Entry"].insert(0, directory)
            self.parent.appConfig["Default Download Location"] = directory

    def _on_reload(self, name):
        if self.parent.PluginManager.reload_plugin(name) != 0:
            self.Info["status"].set("Failed to reload plugin \"" + name + "\"")
        else:
            self.Info["status"].set("Reloaded plugin \"" + name + "\" successfully")

    def _on_sl_browse(self, event=None):
        directory = filedialog.askdirectory(title="Choose directory to search")
        if type(directory) == str:
            self.Widgets["SL Entry"].delete(0, END)
            self.Widgets["SL Entry"].insert(0, directory)

    def _on_search_select(self, data=None):
        print(data)
        self.selection["Search"]["Index"] = data[0]
        self.selection["Search"]["Entry"] = data[1]
        self.Widgets["SL Entry"].delete(0,END)
        self.Widgets["SL Entry"].insert(0,data[1])

    def _on_search_add(self, data=None):
        location = self.Widgets["SL Entry"].get()
        if location != "":
            self.Widgets["SL List"].insert(location)
            self.Widgets["SL Entry"].delete(0, END)

    def _on_search_remove(self, index=None):
        if self.selection["Search"]["Index"] != -1:
            self.Widgets["SL List"].delete(self.selection["Search"]["Index"])
            self.selection["Search"]["Index"] = -1
            self.selection["Search"]["Entry"] = ""

    def _on_theme_select(self, event=None):
        print(self.Widgets["Theme Combo"].get())
        self.parent.style.theme_use( self.Widgets["Theme Combo"].get() )
        self.parent.appConfig["tktheme"] = self.Widgets["Theme Combo"].get()

    class PluginFrame(LabelFrame):
        def __init__(self, master=None, text="", discription="",command=None, **kw):
            LabelFrame.__init__(self, master=master, **kw)
            self.Widgets = {}
            self.text = text
            self["text"] = text
            self.discription = discription
            self.command = command

        def _build(self):
            self.Widgets["Plugin Discription"] = Label(master=self, text=self.discription)
            self.Widgets["Reload Button"] = Button(master=self, text="reload", command=self._on_command, width=6)
            self.grid_columnconfigure(0, weight=1 )
            self.Widgets["Plugin Discription"].grid(row=0, column=0, sticky=E+W, padx=3)
            self.Widgets["Reload Button"].grid(row=0, column=1, sticky=E)

        def _on_command(self):
            if self.command != None:
                self.command(self.text)

        def grid(self,**kwargs):
            self._build()
            LabelFrame.grid(self,**kwargs) 
    
        def pack(self,**kwargs):
            self._build()
            LabelFrame.pack(self,**kwargs)
    
    class DriverFrame(Frame):
        def __init__(self, master=None,browser_name="" ,version_list=[], selected_version="", command=None, **kw):
            Frame.__init__(self, master=master, **kw)
            self.Widgets = {}
            self.browser_name = browser_name
            self.version_list = version_list
            self.selected_version = selected_version
            self.command = command

        def _build(self):
            self.Widgets["Driver Label"] = Label(master=self, text=self.browser_name)
            self.Widgets["Driver Version Select"] = Combobox(master=self)
            self.Widgets["Select Button"] = Button(master=self, text="Select", command=self._on_command, width=6)
            self.grid_columnconfigure(0, weight=1 )
            self.Widgets["Driver Label"].grid(row=0, column=0, sticky=W, padx=2)
            self.Widgets["Driver Version Select"].grid(row=0, column=1,sticky=E)
            self.Widgets["Driver Version Select"].insert(0, self.selected_version)
            self.Widgets["Driver Version Select"].bind("<<ComboboxSelected>>",self._on_version_select)
            self.set_list(self.version_list)
            self.Widgets["Select Button"].grid(row=0, column=2, sticky=E, padx=2, pady=2)

        def set_list(self, version_list):
            if type(version_list) == list:
                self.Widgets["Driver Version Select"]["state"] = "normal"
                self.Widgets["Driver Version Select"]["values"] = version_list
                self.Widgets["Driver Version Select"]["state"] = "readonly"

        def is_active(self):
            if self.Widgets["Select Button"]["state"] == "normal":
                return True
            else:
                return False

        def set_active(self, state=False):
            if state == True:
                self.Widgets["Select Button"]["state"] = "normal"
            else:
                self.Widgets["Select Button"]["state"] = DISABLED

        def _on_command(self):
            if self.command != None:
                self.command(self.browser_name)

        def _on_version_select(self, event=None):
            version = self.Widgets["Driver Version Select"].get()
            self.Widgets["Driver Version Select"]["state"] = "normal"
            self.Widgets["Driver Version Select"].delete(0, END)
            self.Widgets["Driver Version Select"].insert(0, version )
            self.selected_version = version
            self.Widgets["Driver Version Select"]["state"] = "readonly"

        def grid(self,**kwargs):
            self._build()
            Frame.grid(self,**kwargs) 
    
        def pack(self,**kwargs):
            self._build()
            Frame.pack(self,**kwargs)


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
        self.info["version"].set("Version 0.4b")
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
        self.ButtonFrame = Frame(master=self.frame)
        self.fillFrrame = Frame( master=self.ButtonFrame )
        self.closeButton = Button(master=self.ButtonFrame,command=self.close,text="Close")
        self.licenseButton = Button(master=self.ButtonFrame, command=self.showLicense, text="License")

        self.Icon.grid(         row=0,column=0,columnspan=3)
        self.NameLabel.grid(    row=1,column=0,columnspan=3)
        self.versionLabel.grid( row=2,column=0,columnspan=3)
        self.NoticeLabel.grid(  row=3,column=0,columnspan=3)
        self.copyright.grid(    row=4,column=0,columnspan=3)

        self.ButtonFrame["relief"] = "ridge"
        self.ButtonFrame.grid(  row=6, column=0, columnspan=3, sticky=E+W)
        self.ButtonFrame.grid_columnconfigure(0, weight=1)
        self.fillFrrame.grid( row=0, column=0, sticky=E+W )
        self.closeButton.grid(  row=0,column=2, pady=2)
        self.licenseButton.grid(row=0,column=1, pady=2)
    
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
    pref = PreferenceWindow(master=root)
    #about = about_dialog(master=root)
    root.mainloop()