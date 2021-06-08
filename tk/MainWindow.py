#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :MainWindow.py                                                 #
#description     :Defines the MainWidow for tkinter.                            #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :defines a custom tkinter window                               #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

try:
    #Importing Python 3 Tkinter
    from tkinter import Tk, Widget, Button, Frame, Entry, Label, Listbox, Menubutton, Menu, Message, Scrollbar, PanedWindow, LabelFrame, StringVar,Canvas, Text, messagebox, Grid, filedialog
    from tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from tkinter import font, Event
    from tkinter.ttk import Style, Button, Frame, Entry, Label, Menubutton, Scrollbar, PanedWindow, LabelFrame, Label
    from ttkthemes import ThemedStyle
except:
    #Importing Python 2 Tkinter
    from Tkinter import Tk, Button, Frame, Entry, Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text, messagebox, Grid, filedialog
    from Tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from Tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from Tkinter import font
    from Tkinter.ttk import Style, Button, Frame, Entry, Label, Menubutton, Scrollbar, PanedWindow, LabelFrame

import os, sys ,json, platform, pygubu, threading, shutil, re, traceback, logging
import math
from PIL import Image, ImageTk
from queue import Queue
from src.pluginManager import Manager
from src.TitleSource import TitleSource
from src.controller import control
from tk.ScrollableListBox import ScrollableListbox
from tk.ScrollableFrame import ScrollableFrame
from tk.Viewer import Viewer
from tk.QueueWindow import QueueWindow
from tk.popups import add_Window, about_dialog, PreferenceWindow, Queue_Window
from tk.ChapterRow import ChapterRow

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/TKMainWindow.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class MainWindow(Tk, control):

    Instance = None

    Verdana_Normal_13 = ("verdana", 13, "normal")
    Verdana_Normal_12 = ("verdana", 12, "normal")
    Verdana_Normal_11 = ("verdana", 11, "normal")
    Verdana_Normal_10 = ("verdana", 10, "normal")
    Verdana_Bold_15 = ("verdana", 15, "bold")
    Verdana_Bold_13 = ("verdana", 13, "bold")
    Verdana_Bold_11 = ("verdana", 11, "bold")

    def __init__(self, UI_Template=None, title="Untitled", theme="clam", *args, **kwargs):
        if MainWindow.Instance != None:
            raise Exception("Only one instance of MainWindow is allowed")
        else:
            control.__init__(self)
            Tk.__init__(self ,*args, **kwargs)
            #self.style = Style()
            self.style = ThemedStyle(self)
            self.theme = theme
            #self.style.theme_use(theme)
            self.style.set_theme(theme)
            self.Info = {
                "Title"     : StringVar(),
                "Authors"   : StringVar(),
                "Artists"   : StringVar(),
                "Genres"    : StringVar(),
                "Summary"   : StringVar(),
                "Status"    : StringVar(),
                "Source Name" : StringVar(),
                "Update Time" : StringVar()
            }

            self.title(title)
            self.minsize(900,500)
            self["height"] = 500
            self["width"] = 1200         

            if UI_Template != None or os.path.isfile(UI_Template+".ui") != False:
                self.__create_from_template(UI_Template)
            else:
                logger.error("No valid template file found. Exiting.")
                quit(-1)
                #self.__create_from_default()

            self.protocol("WM_DELETE_WINDOW",self._on_quit)

            self._get_title_list_from_file()
            self._load_title_entry()
            MainWindow.Instance = self
            Viewer.load_config(self.appConfig)
  
    def __create_from_template(self, template):
        self.builder = pygubu.Builder()
        self.builder.add_from_file(template+".ui")

        self.Widgets["Main Window"] = self.builder.get_object("MainWindow", master=self)
        self.Widgets["Menu"] = self.builder.get_object("Menu",master=self)
        self.Widgets["Add Command"] = self.builder.get_object("AddTitleCommand")
        self.Widgets["Pref Command"] = self.builder.get_object("Preferences")
        self.Widgets["Quit Command"]= self.builder.get_object("QuitCommand")
        self.Widgets["Export Full"] = self.builder.get_object("ExportFull")
        self.Widgets["Export Lite"] = self.builder.get_object("ExportLite")
        self.Widgets["Title Frame"] = self.builder.get_object("Titleframe")
        self.Widgets["Title List"] = None
        self.Widgets["Add Popup"] = None
        self.Widgets["View Downloads"] = None
        self.Widgets["InfoLabelFrame"] = self.builder.get_object("InfoFrameLabel")
        self.Widgets["Scroll Frame"] = self.builder.get_object("ScrollFrame")
        self.Widgets["InfoFrame"] = self.builder.get_object("InfoFrame")
        self.Widgets["Cover"] = self.builder.get_object("Cover")
        self.Widgets["Title Label"] = self.builder.get_object("TitleLabel")
        self.Widgets["Author Label"] = self.builder.get_object("AuthorLabel")
        self.Widgets["Artist Label"] = self.builder.get_object("ArtistLabel")
        self.Widgets["Genre Label"] = self.builder.get_object("GenreLabel")
        self.Widgets["Update Time Label"] = self.builder.get_object("UpdateTimeLabel")
        self.Widgets["Summary Text"] = self.builder.get_object("SummaryText")
        self.Widgets["Summary Frame"] = self.builder.get_object("SummaryFrame")
        self.Widgets["Stream Select"] = self.builder.get_object("StreamSelect")
        self.Widgets["Cancel DL Button"] = self.builder.get_object("CancelDL_Button")
        self.Widgets["View DL Button"] = self.builder.get_object("ViewDL_Button")
        self.Widgets["Search Button"] = self.builder.get_object("SearchButton")
        self.Widgets["Beginning Button"] = self.builder.get_object("BeginningButton")
        self.Widgets["Prev Button"] = self.builder.get_object("PrevButton")
        self.Widgets["Location Select"] = self.builder.get_object("Location")
        self.Widgets["Next Button"] = self.builder.get_object("NextButton")
        self.Widgets["End Button"] = self.builder.get_object("EndButton")
        self.Widgets["Remove Button"] = self.builder.get_object("RemoveButton")
        self.Widgets["Update Button"] = self.builder.get_object("UpdateButton")
        self.Widgets["Sort Button"] = self.builder.get_object("SortButton")
        self.Widgets["Status Label"] = self.builder.get_object("StatusLabel")
        self.Widgets["Search Entry"] = self.builder.get_object("SearchEntry")

        self.Widgets["Search Entry"]["font"] = self.Verdana_Normal_13
        self.Widgets["InfoFrame"].grid_forget()
        self.Widgets["InfoLabelFrame"]["labelwidget"] = Label(textvariable=self.Info["Source Name"], font=self.Verdana_Bold_15)

        self.Widgets["Title Label"]["textvariable"] = self.Info["Title"]
        self.Widgets["Title Label"]["font"] = self.Verdana_Bold_13
        self.Widgets["Title Label"]["relief"] = "raised"

        self.Widgets["Author Label"]["textvariable"] = self.Info["Authors"]
        self.Widgets["Author Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Author Label"]["relief"] = "ridge"
        
        self.Widgets["Artist Label"]["textvariable"] = self.Info["Artists"]
        self.Widgets["Artist Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Artist Label"]["relief"] = "ridge"

        self.Widgets["Genre Label"]["textvariable"] = self.Info["Genres"]
        self.Widgets["Genre Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Genre Label"]["relief"] = "ridge"

        self.Widgets["Update Time Label"]["textvariable"] = self.Info["Update Time"]
        self.Widgets["Update Time Label"]["font"] = self.Verdana_Normal_10
        self.Widgets["Update Time Label"].config(width=19)

        self.Widgets["Summary Frame"]["labelwidget"] = Label(text="Summary", font=self.Verdana_Bold_11)
        self.Widgets["Summary Text"]["font"] = self.Verdana_Normal_11

        self.Widgets["Stream Select"].bind("<<ComboboxSelected>>",self._on_stream_change)
        self.Widgets["Stream Select"].insert(0, "Select Stream")
        self.Widgets["Stream Select"].config(width=13)
        self.Widgets["Stream Select"]["state"] = "readonly"
        self.Widgets["Stream Select"]["font"] = self.Verdana_Normal_12

        self.Widgets["Location Select"].bind( "<FocusOut>", 
            lambda e: 
                self.Widgets["Location Select"].unbind("<Return>")
        )
        self.Widgets["Location Select"].bind( "<FocusIn>", 
            lambda e:
                self.Widgets["Location Select"].bind("<Return>", self._on_location_change)
        )
        self.Widgets["Location Select"].bind("<<ComboboxSelected>>", self._on_location_change)
        self.Widgets["Location Select"]["font"] = self.Verdana_Normal_12
        self.Widgets["Location Select"]["state"] = DISABLED

        self.Widgets["Status Label"]["textvariable"] = self.Info["Status"]

        self.Widgets["Cancel DL Button"].config( command=self._on_cancel_downloads)
        #self.Widgets["View DL Button"]["state"] = DISABLED
        self.Widgets["View DL Button"].config(command=self._on_view_downloads)
        self.Widgets["Search Button"].config(command=self._on_search_change)
        self.Widgets["Beginning Button"].config(command=self._on_beginning)
        self.Widgets["Prev Button"].config(command=self._on_prev)
        self.Widgets["Next Button"].config(command=self._on_next)
        self.Widgets["End Button"].config(command=self._on_end)
        self.Widgets["Update Button"].config(command=self._on_update)
        self.Widgets["Remove Button"].config(command=self._on_remove)
        self.Widgets["Sort Button"].config(command=self._on_sort)

        self.Widgets["Search Entry"].bind( "<FocusOut>", 
            lambda e: 
                self.Widgets["Search Entry"].unbind("<Return>")
        )
        self.Widgets["Search Entry"].bind( "<FocusIn>", 
            lambda e:
                self.Widgets["Search Entry"].bind("<Return>", self._on_search_change)
            )

        self.Widgets["Main Window"].pack(fill=BOTH,expand=1)
        self.Widgets["Title List"] = ScrollableListbox(master=self.Widgets["Title Frame"], command=self._on_list_select)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 0, weight=0)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 1, weight=1)
        
        self.Widgets["Title List"].grid(row=1,column=0,sticky=N+E+S+W)
        self.config( menu = self.Widgets["Menu"])
        self.builder.connect_callbacks(self)

    #def __create_from_default(self):
    #    pass

    def add_title_entry(self,name):
        self.Widgets["Title List"].insert(name)

    def update_status(self, message=""):
        if type(message) == str:
            self.Info["Status"].set(message)

    def _download_chapter(self, title, stream, chapter, location):
        hash_id = hash( ( title, stream, chapter ) )
        self.ChapterQueue.appendleft( (title, stream, chapter, location, hash_id) )
        if self.threads["Chapter"] == None:
            self.threads["Chapter"] = threading.Thread( target=self._download_chapter_runner )
            logger.info("Starting chapter download thread")
            self._KillThreads[0] = False
            self.threads["Chapter"].start()
        else:
            if self._current_task["Chapter"] != None:
                title = self._current_task["Chapter"][0]
                chapter = self._current_task["Chapter"][2]
                mess = "Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) )
                self.update_status( message=mess )
                
    def is_chapter_visable( self, title, stream, chapter ):
        chapter_hash = hash( ( title, stream, chapter ) )
        for i in range( 0, len(self.Chapter_List) ):
            if chapter_hash == self.Chapter_List[i][1]:
                return self.Chapter_List[i][0]
        return None

    def _load_title_entry(self):
        self.update_status( "Loading Title List.....")
        for m in self.Title_Dict.keys():     
            self.add_title_entry(m)
        self.update_status("Loaded Title List")

    def _update_location_bounds(self):
        super()._update_location_bounds()

        selection_values = []
        for i in range(1, self.page_location["end"]+1) :
            selection_values.append( str(i) + "/" + str(self.page_location["end"]) )
        self.Widgets["Location Select"]["values"] = selection_values

    def _update_location_controls(self, disable=False):
        if disable == True:
            self.Widgets["Location Select"].delete(0, END)
            self.Widgets["Location Select"].insert(0, "" )
            self.Widgets["Location Select"]["state"] = DISABLED
            self.Widgets["Next Button"]["state"] = DISABLED
            self.Widgets["End Button"]["state"] = DISABLED
            self.Widgets["Prev Button"]["state"] = DISABLED
            self.Widgets["Beginning Button"]["state"] = DISABLED

        else:
            self.Widgets["Location Select"].delete(0, END)
            self.Widgets["Location Select"].insert(0, str( self.page_location["current"]+1) +"/"+ str(self.page_location["end"]))

            if self.page_location["end"] == 1:
                self.Widgets["Next Button"]["state"] = DISABLED
                self.Widgets["End Button"]["state"] = DISABLED
                self.Widgets["Prev Button"]["state"] = DISABLED
                self.Widgets["Beginning Button"]["state"] = DISABLED

            elif self.page_location["current"] == self.page_location["end"]-1:
                self.Widgets["Next Button"]["state"] = DISABLED
                self.Widgets["End Button"]["state"] = DISABLED
                self.Widgets["Prev Button"]["state"] = NORMAL
                self.Widgets["Beginning Button"]["state"] = NORMAL

            elif self.page_location["current"] == 0 :
                self.Widgets["Next Button"]["state"] = NORMAL
                self.Widgets["End Button"]["state"] = NORMAL
                self.Widgets["Prev Button"]["state"] = DISABLED
                self.Widgets["Beginning Button"]["state"] = DISABLED

            else:
                self.Widgets["Next Button"]["state"] = NORMAL
                self.Widgets["End Button"]["state"] = NORMAL
                self.Widgets["Prev Button"]["state"] = NORMAL
                self.Widgets["Beginning Button"]["state"] = NORMAL

    def _update_title_details(self):
        load = Image.open(self.selection["Title"].get_cover_location())
        load.thumbnail( (300,350), Image.ANTIALIAS )
        render = ImageTk.PhotoImage(load)
        self.Widgets["Cover"]["width"] = render.width()
        self.Widgets["Cover"]["height"] = render.height()
        self.Widgets["Cover"].create_image(render.width()/2,render.height()/2,anchor="c", image=render)
        self.Widgets["Cover"].image = render
        self.Info["Source Name"].set( self.selection["Title"].get_site_name() )
        self.Info["Title"].set(self.selection["Title"].get_title(group=6))
        authors_string = " Author(s): " + self.selection["Title"].get_Authors_str(group=4)
        artists_string = " Artist(s)  : " + self.selection["Title"].get_Artists_str(group=4)
        genres_string =  " Genre(s) : " + self.selection["Title"].get_Genres_str(group=4)
        self.Info["Authors"].set(authors_string)
        self.Info["Artists"].set(artists_string)
        self.Info["Genres"].set(genres_string)
        if self._current_task["Update Title"] == self.selection["Title"]:
            self.Widgets["Update Button"]["state"] = DISABLED
        else:
            self.Widgets["Update Button"]["state"] = NORMAL
        self.Info["Update Time"].set( "Last update: "+self.selection["Title"].download_time )
        self.Widgets["Summary Text"]["state"] = NORMAL
        self.Widgets["Summary Text"].delete(1.0,END)
        self.Widgets["Summary Text"].insert(END, self.selection["Title"].get_summary())
        self.Widgets["Summary Text"]["state"] = DISABLED
        if self.selection["Stream"] != None:
            self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])
               

    # Signal callback methods ---------------------------------------------------------------#

    def about(self):
        about_dialog(master=self)

    def _import_library(self):
        libraryfile = filedialog.askopenfile(title="Choose Library Archive", filetypes=( ("zip files", "*.zip"),( "all files","*.*" )))
        
        if type(libraryfile) == str:
            self.update_status("Importing Library:\n"+libraryfile)
            result = super()._import_library(libraryfile)
            if result == 1:
                errorpopup = messagebox.showerror("Import Error", libraryfile + "\nFailed to import library")
                self.update_status("Library Import Failed")
            else:
                self.update_status("Library Imported")

    def _on_cancel_downloads(self):
        self._KillThreads[0] = True

    def _on_menu_add(self):
        self.Widgets["Add Popup"] = add_Window(master=self,OKCommand=self._on_add_responce)
    
    def _on_quit(self):
        self._export_title_list_to_file()
        self._export_config()
        result = None
        if self.threads["Title"] != None or self.threads["Stream"] != None or self.threads["Chapter"]:
            result = messagebox.askyesno("Active Download(s)", "Do you want to wait for downloads to finish?")
            if result == False:
                self.Info["Status"].set("shuting down threads")
                self._KillThreads = True
                if self.threads["Title"] != None:
                    self.threads["Title"].join()
                if self.threads["Stream"] != None:
                    self.threads["Stream"].join()
                if self.threads["Chapter"] != None:
                    self.threads["Chapter"].join()
            else:
                return

        self.destroy()

    def _on_add_responce(self , data):
        pattern = re.compile(r"\s")
        data = re.subn(pattern,"", data)[0]
        urls = data.split(",")
        print(urls)
        for u in urls:
            domain = TitleSource.find_site_domain(u)
            if self.PluginManager.is_source_supported(domain):
                title = self.PluginManager.create_instance(domain)
                self.TitleQueue.appendleft( (title, u) )
                if self.threads["Title"] == None:
                    self.threads["Title"] = threading.Thread(target=self._add_title_from_url_runner)
                    logger.info("Starting Title Thread")
                    self.threads["Title"].start()     
                
            elif domain == None:
                messagebox.showerror("Invalid","Invalid site domain")
            else:
                messagebox.showerror("Unsupported Title Site",domain + " is currently not supported")

    def _on_list_select(self, data, widget=None):
        if self.selection["Title"] == None or self.selection["Title"] != self.Title_Dict[data[1]]:
            self.selection["Title"] = self.Title_Dict[data[1]]
            self.selection["Stream"] = None
            if self.Widgets["InfoFrame"].winfo_ismapped() == False:
                self.Widgets["InfoFrame"].grid(row=0,column=0, sticky=N+E+S+W, pady=2, padx=2)

            self._update_location_controls(disable=True)

            self._update_title_details()
            self._update_stream_dropdown()
            self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_location_change(self, event=None):
        page_str = self.Widgets["Location Select"].get()
        page_elements = page_str.split("/")
        if event.keycode == 36:
            if page_elements[0].isnumeric() == True:
                page_num = int( page_elements[0] ) - 1
                if page_num > self.page_location["end"]:
                    page_num = self.page_location["end"]-1
                elif page_num <= 0:
                    page_num = 0
                self.page_location["current"] = page_num
        else:
            self.page_location["current"] = int(page_elements[0])-1
        
        self._update_location_controls()
        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_pref(self, event=None):
        self.Widgets["Preference Window"] = PreferenceWindow(master=self)

    def _on_remove(self):
        result = messagebox.askyesno("Are you sure?", "Do you want to remove\n\"" + self.selection["Title"].get_title() + "\"?")

        if result == True:
            self.Widgets["InfoFrame"].grid_forget()
            self.Info["Source Name"].set("")
            title_to_delete = self.Title_Dict[self.selection["Title"].get_title()]

            location = os.path.join( title_to_delete.save_location, title_to_delete.directory)
            if os.path.isdir(location) == True:
                if location != self.appConfig["Default Download Location"] or location != title_to_delete.save_location:
                    shutil.rmtree(location)
                    del self.Title_Dict[ self.selection["Title"].get_title() ]
                    self.Widgets["Title List"].delete( self.selection["Title"].get_title() )
                    self.selection["Title"] = None
                    self.selection["stream"] = None
                    self.selection["chapter"] = None
                else:
                    logging.warning("Tried to delete library location")

    def _on_remove_chapter(self, chapter_row):
        chapter_row.update_state("download", "Download", active=True)
        chapter_row.update_state("view", active=False)
        chapter_row.update_state("remove", active=False)
        if os.path.isfile(chapter_row.chapter_path+'/'+chapter_row.chapter.directory+ '.zip') == True:
            os.remove(chapter_row.chapter_path+"/"+chapter_row.chapter.directory+".zip")

    def _on_search_change(self, event=None):
        text = self.Widgets["Search Entry"].get()
        self.Widgets["Title List"].remove_all()
        if text == "":
            for t in self.Title_Dict.keys():
                self.add_title_entry(t)

        else:
            pattern = re.compile( "(" + text.lower() + ")" )
            for t in self.Title_Dict.keys():
                if re.search(pattern, t.lower()) != None:
                    self.add_title_entry(t)

    def _on_sort(self):
        self._sort = not self._sort
        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_stream_change(self, event):
        self.selection["Stream"] = self.selection["Title"].get_stream_with_name(
            self.Widgets["Stream Select"].get()
        )
        self.Widgets["Location Select"]["state"] = NORMAL
        self._update_location_bounds()
        self._update_location_controls()
        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_view(self, number):
        self.selection["Chapter"] = self.selection["Stream"].get_chapter(number)
        v = Viewer.get_instance( self.selection["Title"], self.selection["Stream"], self.selection["Chapter"] )
        if v != None:
            messagebox.showinfo("Viewer open", "A viewer for this chapter is already open")
        else:
            Viewer(self.selection["Title"], self.selection["Stream"], self.selection["Chapter"],master=self)
    
    def _on_view_downloads(self):
        self.Widgets["Queue Window"] = Queue_Window(master=self)

    def _on_update(self):

        if self.selection["Title"] != None:
            if self.threads["Stream"] == None:
                self.UpdateTitleQueue.appendleft( self.selection["Title"] )
                self.threads["Stream"] = threading.Thread( target=self._update_stream_runner )
                logger.info("Starting Title Update Thread")
                self.threads["Stream"].start()
            else:
                self.UpdateTitleQueue.appendleft(self.selection["Title"])
        else:
            #should never get here
            messagebox.showwarning("Warning","No Title Stream Selected")

    def _update_chapter_list(self, length=-1, offset=0):
        if self.selection["Stream"] != None:
            
            #removing old chapter entries
            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    r[0].destroy()
                self.Chapter_List = []

            #getting new chapter list
            chapters = self.selection["Stream"].get_chapters()
            
            #applying sort
            if self._sort == True :
                chapters.sort(reverse=True)
            else: 
                chapters.sort(reverse=False)

            start = None
            end = None

            if length == -1 or length > len(chapters):
                start = 0
                end = len(chapters)
            else:
                self.page_location["end"] = int( len(chapters) / length)
                if len(chapters) % length != 0:
                    self.page_location["end"] += 1
                
                if offset >= self.page_location["end"]:
                    offset = self.page_location["end"]
                    self.page_location["current"] = offset
                
                start = length * offset
                end = length * offset + length
                if end > len(chapters):
                    end = len(chapters)

            for i in range(start, end):
                row = ChapterRow(   master=self.Widgets["InfoFrame"],
                                    masterWindow=self,
                                    title=self.selection["Title"],     
                                    stream=self.selection["Stream"],
                                    chapter=chapters[i],
                                    viewcommand=self._on_view,
                                    downloadcommand=self._download_chapter,
                                    removecommand=self._on_remove_chapter
                )
                row.grid(row=8+i, column=0, columnspan=12, sticky=E+W)
                row["relief"] = "groove"

                self.Chapter_List.append( (row , hash(row) )  )
        else:
            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    r[0].destroy()
                    self.Chapter_List = [] 
 
    def _update_stream_dropdown(self):
        if self.selection["Stream"] == None:
            self.Widgets["Stream Select"]["state"] = NORMAL
            self.Widgets["Stream Select"].delete(0, END)
            self.Widgets["Stream Select"].insert(0,"Select Stream")
            self.Widgets["Stream Select"]["state"] = "readonly"
        streamlist = self.selection["Title"].get_streams()
        streamlist_names = []
        longest = -1
        for i in range(0,len(streamlist)):
            if len(  streamlist[i].get_name() ) > longest:
                longest = len( streamlist[i].get_name() )
            streamlist_names.append(streamlist[i].get_name())
        self.Widgets["Stream Select"]["width"] = longest+2
        self.Widgets["Stream Select"]["values"] = streamlist_names

    # Thread worker methods -----------------------------------------------------------------#

    def _add_title_from_url_runner( self ):

        while len(self.TitleQueue) > 0 :
            if self._KillThreads[0] == True:
                logger.info("Title Thread kill signal received.")
                self.TitleQueue.clear()
                return
            self._current_task["Title"] = self.TitleQueue.pop()
            title = self._current_task["Title"][0]
            url = self._current_task["Title"][1]
            self.update_status( "Downloading : " + url )
            code = title.request_manga(url)

            if code != 0:
                logger.info("Failed to Connect. HTML Error " + str(code))
                messagebox.showerror( "Failed to Connect", "HTML Error " + str(code))
                
            else:
                try: 
                    if self.Title_Dict.get(title.get_title()) == None:
                        self.update_status("Extracting : " + url)
                        title.extract_title()
                        self.update_status( "Extraction of " + title.get_title() + " Complete" )
                        self.add_title_entry(title.get_title())
                        self.Title_Dict[title.get_title()] = title
                        title.to_json_file(title.save_location)
                        self.update_status( "Sucsessfully added: " + title.get_title() ) 
                    else:
                        logger.warning("Insertion of an already existing Title.")
                        messagebox.showerror("Title Already Exists", title.get_title())
                except:
                    logger.exception("Failed to extraction: " + url)
                    messagebox.showerror("Failed to extract","Failed to extract title data from url: " + url)
            if self._KillThreads[0] == True:
                logger.info("Title Thread kill signal received.")
                return

        self.threads["Title"] = None

    def _download_chapter_runner(self):
        while len(self.ChapterQueue) > 0:
            if self._KillThreads[0] == True:
                logger.info("Chapter Thread kill signal received.")
                self.ChapterQueue.clear()
                return
            self._current_task["Chapter"] = self.ChapterQueue.pop()
            #print(self._current_task["Chapter"])
            title = self._current_task["Chapter"][0]
            #print(title)
            stream = self._current_task["Chapter"][1]
            chapter = self._current_task["Chapter"][2]
            row = self.is_chapter_visable( title, stream, chapter )
            if row != None:
                row.Info["Download"].set( "Downloading.." )
            self.update_status( "Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) ) )
            code = title.download_title_chapter( stream.get_id(), chapter.get_chapter_number(), self._current_task["Chapter"][3], self._KillThreads )
            row = self.is_chapter_visable( title, stream,chapter )
            if code == 4:
                return

            elif code != 0:
                self.update_status("Failed to download:\n" + str(chapter) )
                if row != None:
                    row.Info["Download"].set( "Download" )
                    row.update_state("download", "Download" , True)
                continue
            else:
                self.update_status( "Download of " + title.get_title() + "\n" + str(chapter) + " --- Completed" )
                if row != None:
                    row.Info["Download"].set( "Downloaded" )
                    row.update_state("download")
                    row.update_state("view", "View",True)
                    row.update_state("remove", "Remove",True)
            if self._KillThreads[0] == True:
                logger.info("Chapter Thread kill signal received.")
                return

        self.threads["Chapter"]= None

    def _update_stream_runner( self ):
       
        while len(self.UpdateTitleQueue) > 0:
            if self._KillThreads[0] == True:
                logger.info("Stream Thread kill signal received.")
                return
            self._current_task["Update Title"] = self.UpdateTitleQueue.pop()
            title_object = self._current_task["Update Title"]
            self.update_status( "Updating " + title_object.get_title()+ "\n" + str(len( self.UpdateTitleQueue) ) + " Updates pending")
            if title_object == self.selection["Title"]:
                self.Widgets["Update Button"]["state"] = DISABLED
            try:
                status = title_object.update_streams()
                if status == 0:
                    title_object.to_json_file(title_object.save_location)
                    if title_object == self.selection["Title"]:
                        self.Info["Update Time"].set( "Last Update: " + title_object.download_time )
                    self.update_status( title_object.get_title() + "\nUpdated" )
                    if title_object == self.selection["Title"]:
                        self.Widgets["Update Button"]["state"] = NORMAL
                else:
                    logger.info("Update Error, HTML error code: " + str(status))
                    messagebox.showerror("Update Error", "Site returned error " + str(status) )
            except Exception:
                logger.exception("Failed to update " + title_object.get_title())
                self.update_status( "Failed to update " + title_object.get_title())

            if self._KillThreads[0] == True:
                logger.info("Stream Thread kill signal received.")
                return

        self.threads["Stream"] = None
