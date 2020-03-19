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
    from tkinter import Tk, Button, Frame, Entry, Label, Listbox, Menubutton, Menu, Message, Scrollbar, PanedWindow, LabelFrame, StringVar,Canvas, Text, messagebox, Grid
    from tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from tkinter import font
    from tkinter.ttk import Style, Button, Frame, Entry, Label, Menubutton, Scrollbar, PanedWindow, LabelFrame

except:
    from Tkinter import Tk, Button, Frame, Entry, Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text, messagebox, Grid
    from Tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from Tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from Tkinter import font
    from Tkinter.ttk import Style, Button, Frame, Entry, Label, Menubutton, Scrollbar, PanedWindow, LabelFrame

import os, sys ,json, platform, pygubu, threading, shutil, re, traceback
from PIL import Image, ImageTk
from queue import Queue
try:
    from ..src.MangaPark import MangaPark_Source
    from ..src.TitleSource import TitleSource
    from ..scr.controller import control
    from .ScrollableListBox import ScrollableListbox
    from .Viewer import Viewer
    from .popups import add_Window, about_dialog
    from .ChapterRow import ChapterRow
except:
    from src.MangaPark import MangaPark_Source
    from src.TitleSource import TitleSource
    from src.controller import control
    from tk.ScrollableListBox import ScrollableListbox
    from tk.Viewer import Viewer
    from tk.popups import add_Window, about_dialog
    from tk.ChapterRow import ChapterRow

class MainWindow(Tk, control):

    Instance = None

    Verdana_Normal_12 = ("verdana", 12, "normal")
    Verdana_Normal_11 = ("verdana", 11, "normal")
    Verdana_Bold_15 = ("verdana", 15, "bold")
    Verdana_Bold_13 = ("verdana", 13, "bold")
    Verdana_Bold_11 = ("verdana", 11, "bold")

    def __init__(self, UI_Template=None, title="Untitled", theme="clam", *args, **kwargs):
        if MainWindow.Instance != None:
            raise Exception("Only one instance of MainWindow is allowed")
        else:
            control.__init__(self)
            Tk.__init__(self ,*args, **kwargs)
            self.style = Style()
            self.style.theme_use(theme)
            self.Info = {
                "Title"     : StringVar(),
                "Authors"   : StringVar(),
                "Artists"   : StringVar(),
                "Genres"    : StringVar(),
                "Summary"   : StringVar(),
                "Status"    : StringVar(),
                "Source Name" : StringVar(),
            }

            self.title(title)
            self.minsize(900,500)
            self["height"] = 500
            self["width"] = 1200         

            if UI_Template != None or os.path.isfile(UI_Template+".ui") != False:
                self.__create_from_template(UI_Template)
            else:
                self.__create_from_default()

            self.protocol("WM_DELETE_WINDOW",self._on_quit)

            self._get_title_list_from_file()
            self._load_title_entry()
            MainWindow.Instance = self
  
    def __create_from_template(self, template):
        self.builder = pygubu.Builder()
        self.builder.add_from_file(template+".ui")

        self.Widgets["Main Window"] = self.builder.get_object("MainWindow", master=self)
        self.Widgets["Menu"] = self.builder.get_object("Menu",master=self)
        self.Widgets["Add Command"] = self.builder.get_object("AddMangaCommand")
        self.Widgets["Quit Command"]= self.builder.get_object("QuitCommand")
        self.Widgets["Title Frame"] = self.builder.get_object("Titleframe")
        self.Widgets["Title List"] = None
        self.Widgets["Add Popup"] = None
        self.Widgets["InfoLabelFrame"] = self.builder.get_object("InfoFrameLabel")
        self.Widgets["Scroll Frame"] = self.builder.get_object("ScrollFrame")
        self.Widgets["InfoFrame"] = self.builder.get_object("InfoFrame")
        self.Widgets["Cover"] = self.builder.get_object("Cover")
        self.Widgets["Title Label"] = self.builder.get_object("TitleLabel")
        self.Widgets["Author Label"] = self.builder.get_object("AuthorLabel")
        self.Widgets["Artist Label"] = self.builder.get_object("ArtistLabel")
        self.Widgets["Genre Label"] = self.builder.get_object("GenreLabel")
        self.Widgets["Summary Text"] = self.builder.get_object("SummaryText")
        self.Widgets["Summary Frame"] = self.builder.get_object("SummaryFrame")
        self.Widgets["Stream Select"] = self.builder.get_object("StreamSelect")
        self.Widgets["Remove Button"] = self.builder.get_object("RemoveButton")
        self.Widgets["Update Button"] = self.builder.get_object("UpdateButton")
        self.Widgets["Sort Button"] = self.builder.get_object("SortButton")
        self.Widgets["Status Label"] = self.builder.get_object("StatusLabel")
        self.Widgets["Search Entry"] = self.builder.get_object("SearchEntry")
        
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

        self.Widgets["Summary Frame"]["labelwidget"] = Label(text="Summary", font=self.Verdana_Bold_11)
        self.Widgets["Summary Text"]["font"] = self.Verdana_Normal_11

        self.Widgets["Stream Select"].bind("<<ComboboxSelected>>",self._on_stream_change)
        self.Widgets["Stream Select"].insert(0, "Select Stream")
        self.Widgets["Stream Select"]["state"] = "readonly"
        self.Widgets["Stream Select"]["font"] = self.Verdana_Normal_12

        self.Widgets["Status Label"]["textvariable"] = self.Info["Status"]
        self.Widgets["Update Button"].config(command=self._on_update)
        self.Widgets["Remove Button"].config(command=self._on_remove)
        self.Widgets["Sort Button"].config(command=self._on_sort)

        self.Widgets["Search Entry"].bind("<Return>", self._on_search_change)
        
        self.Widgets["Main Window"].pack(fill=BOTH,expand=1)
        self.Widgets["Title List"] = ScrollableListbox(master=self.Widgets["Title Frame"], command=self._on_list_select)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 0, weight=0)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 1, weight=1)
        
        self.Widgets["Title List"].grid(row=1,column=0,sticky=N+E+S+W)
        self.config( menu = self.Widgets["Menu"])
        self.builder.connect_callbacks(self)

    def __create_from_default(self):
        pass

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
            self.threads["Chapter"].start()
        else:
            if self._current_task["Chapter"] != None:
                title = self._current_task["Chapter"][0]
                chapter = self._current_task["Chapter"][2]
                mess = "Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) )
                self.update_status( message=mess )
 
    def _export_title_list_to_file(self, export_file="tracking_list.json"):
        if self.appConfig['Hide Cache Files']== True:
            if platform.system()  == "Linux":
                export_file = "." + export_file

        dic = { "Number of titles": len(self.Title_Dict), "Search Location(s)" : [], "Title List" : {} }
        for l in self.search_locations:
            dic["Search Location(s)"].append(l)

        for m in self.Title_Dict.keys():
            location = self.Title_Dict[m].save_location
            if dic["Title List"].get(location) == None:
                dic["Title List"][location] = []
            dic["Title List"][location].append(m)

        with open(self.appConfig["Cashe Save Location"] +'/'+ export_file, 'w') as f:
            f.write(json.dumps(dic, separators=(",", " : "), indent=4))
            f.close()

    def _get_title_list_from_file(self, json_file="tracking_list.json"):
        if self.appConfig["Hide Cache Files"] == True:
            if platform.system() == "Linux":
                json_file = "." + json_file

        if os.path.exists(self.appConfig["Cashe Save Location"] +'/'+json_file) == True:
            cache_string = ""
            with open(self.appConfig["Cashe Save Location"] +'/'+ json_file, 'r') as f:
                cache_string = f.read()
                f.close()
            dic = json.loads(cache_string)
            if(len(dic) != 0):
                #get title from tracking file
                for l in dic["Title List"].keys():
                    self.search_locations.add(l)
                    for m in dic["Title List"][l]:
                        _m = m.replace(" ", "_")
                        cache_path = _m + "/" + _m + ".json"
                        if self.check_title_cache_exists(l,cache_path) == True:
                            title_object = self.read_title_cache(l + '/' + cache_path)
                            if title_object != None:
                                self.Title_Dict[m] = title_object
        #search for titles not in tracking file
        print("Searching for untracked Titles")
        for search in self.appConfig["Search Location(s)"]:
            #print(search)
            dirs = os.listdir(search)
            for d in dirs:
                #print("Checking " + str(d))
                path = search + '/'+ d + "/" + d + '.json'
                _d = d.replace('_', ' ')
                if os.path.isfile(path) == True and self.Title_Dict.get(_d) == None:
                    title_object = self.read_title_cache( path)
                    if title_object != None:
                        if self.Title_Dict.get(title_object.get_title()) == None:
                            self.search_locations.add(search)
                            print("Discovered: " + title_object.get_title() + " in " + search)
                            self.Title_Dict[title_object.get_title()] = title_object

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

    def _on_remove_chapter(self, chapter_row):
        chapter_row.update_state("download", True)
        chapter_row.Info["Download"].set("Download")
        chapter_row.update_state("view", False)
        chapter_row.update_state("remove", False)
        if os.path.isfile(chapter_row.chapter_path+'/'+chapter_row.chapter.directory+ '.zip') == True:
            os.remove(chapter_row.chapter_path+"/"+chapter_row.chapter.directory+".zip")

    def _update_title_details(self):
        load = Image.open(self.selection["Title"].get_cover_location())
        render = ImageTk.PhotoImage(load)
        self.Widgets["Cover"]["width"] = render.width()
        self.Widgets["Cover"]["height"] = render.height()
        self.Widgets["Cover"].create_image(render.width()/2,render.height()/2,anchor="c", image=render)
        self.Widgets["Cover"].image = render
        self.Info["Title"].set(self.selection["Title"].get_title(group=6))
        authors_string = " Author(s): " + self.selection["Title"].get_Authors_str(group=4)
        artists_string = " Artist(s)  : " + self.selection["Title"].get_Artists_str(group=4)
        genres_string =  " Genre(s) : " + self.selection["Title"].get_Genres_str(group=4)
        self.Info["Authors"].set(authors_string)
        self.Info["Artists"].set(artists_string)
        self.Info["Genres"].set(genres_string)

        self.Widgets["Summary Text"]["state"] = NORMAL
        self.Widgets["Summary Text"].delete(1.0,END)
        self.Widgets["Summary Text"].insert(END, self.selection["Title"].get_summary())
        self.Widgets["Summary Text"]["state"] = DISABLED
        if self.selection["Stream"] != None:
            self._update_chapter_list()
 
    # Signal callback methods ---------------------------------------------------------------#

    def about(self):
        about_dialog(master=self)

    def _on_menu_add(self):
        self.Widgets["Add Popup"] = add_Window(master=self,OKCommand=self._on_add_responce)

    def _on_quit(self):
        self._export_title_list_to_file()
        if self.threads["Title"] != None:
            result = messagebox.askyesno("Active Download", "Do you want to wait title to download?")
            if result == False:
                return
            else:
                self._KillThreads = True

        if self.threads["Stream"] != None:
            self.Info["Status"].set("Waiting for Stream Update to finish")
            self.threads["Stream"].join()

        if self.threads["Chapter"] != None:
            result = messagebox.askyesno("Active Downloads", "Do you want to stop download?")
            if result == False:
                return
            else:
                self._KillThreads[0] = True
                self.Info["Status"].set("Waiting for Chapter downloads to finish")
           
        self.destroy()

    def _on_add_responce(self , data):
        pattern = re.compile(r"\s")
        data = re.subn(pattern,"", data)[0]
        urls = data.split(",")
        for u in urls:
            domain = TitleSource.find_site_domain(u)
            if domain == 'mangapark.net' or domain == 'www.mangapark.net':
                title = MangaPark_Source()
                self.TitleQueue.appendleft( (title, u) )
                if self.threads["Title"] == None:
                    self.threads["Title"] = threading.Thread(target=self._add_title_from_url_runner)
                    self.threads["Title"].start()        
                
            elif domain == None:
                messagebox.showerror("Invalid","Invalid site domain")
            else:
                messagebox.showerror("Unsupported Title Site",domain + " is currently not supported")

    def _on_list_select(self, data ,widget=None):
        self.selection["Title"] = self.Title_Dict[data[1]]
        self.selection["Stream"] = None
        if self.Widgets["InfoFrame"].winfo_ismapped() == False:
            self.Widgets["InfoFrame"].grid(row=0,column=0, sticky=N+E+S+W, pady=2, padx=2)
        
        self._update_title_details()
        self._update_stream_dropdown()
        self._update_chapter_list()

    def _on_remove(self):
        self.Widgets["InfoFrame"].grid_forget()
        title_to_delete = self.Title_Dict[self.selection["Title"].get_title()]

        location = title_to_delete.save_location +'/' + title_to_delete.directory
        
        if os.path.isdir(location) == True:
            shutil.rmtree(location)
            del self.Title_Dict[self.selection["Title"].get_title()]
            self.Widgets["Title List"].delete( self.selection["Title"].get_title() )

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
        self._update_chapter_list()

    def _on_stream_change(self, event):
        self.selection["Stream"] = self.selection["Title"].get_stream_with_name(
            self.Widgets["Stream Select"].get()
        )
        self._update_chapter_list()

    def _on_view(self, number):
        self.selection["Chapter"] = self.selection["Stream"].get_chapter(number)
        v = Viewer.get_instance( self.selection["Title"], self.selection["Stream"], self.selection["Chapter"] )
        if v != None:
            messagebox.showinfo("Viewer open", "A viewer for this chapter is already open")
        else:
            Viewer(self.selection["Title"], self.selection["Stream"], self.selection["Chapter"])
    
    def _on_update(self):

        if self.selection["Title"] != None:
            if self.threads["Stream"] == None:
                self.update_status(self.selection["Title"].get_title() + "\tUpdating Streams...")
                self.threads["Stream"] = threading.Thread( target=self._update_stream_runner, args=(self.selection["Title"],) )
                self.threads["Stream"].start()

            elif self.threads["Stream"].is_alive() == False:
                self.update_status(self.selection["Title"].get_title() + "\tUpdating Streams...")
                self.threads["Stream"] = threading.Thread( target=self._update_stream_runner, args=(self.selection["Title"],) )
                self.threads["Stream"].start()
            else:
                messagebox.showwarning("Title Update", "An update is in progress. Wait for update to complete before requesting another.")
        else:
            #should never get here
            messagebox.showwarning("Warning","No Title Stream Selected")

    def _update_chapter_list(self, start=0, end=-1):
        if self.selection["Stream"] != None:

            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    r[0].destroy()
                self.Chapter_List = []

            chapters = self.selection["Stream"].get_chapters()
            if self._sort == True :
                chapters.sort(reverse=True)
            else: 
                chapters.sort(reverse=False)
            if end == -1 or end > len(chapters):
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
                row.grid(row=8+i, column=0, columnspan=5, sticky=E+W)
                row["relief"] = "groove"

                self.Chapter_List.append( (row , hash(row) )  )
        else:
            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    r[0].destroy()
                    self.Chapter_List = [] 
 
    def _update_stream_dropdown(self):
        if self.selection["Stream"] != None:
            self.Widgets["Stream Select"].delete(0, END)
            self.Widgets["Stream Select"].insert(0,"Select Stream")
        streamlist = self.selection["Title"].get_streams()
        streamlist_names = []
        for i in range(0,len(streamlist)):
            streamlist_names.append(streamlist[i].get_name())
        self.Widgets["Stream Select"]["values"] = streamlist_names

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def check_title_cache_exists( search_location, title_name ):
        if os.path.isfile(search_location+'/'+ title_name):
            return True
        else:
            return False

    @staticmethod
    def read_title_cache(json_file):
        title_string = ""
        with open(json_file, 'r') as f:
            title_string = f.read()
            f.close()
        Title_Dict = json.loads(title_string)
        if Title_Dict["Site Domain"] == "https://mangapark.net":
            title = MangaPark_Source()
            title.from_dict(Title_Dict)
            return title
        else:
            return None

    # Thread worker methods -----------------------------------------------------------------#

    def _add_title_from_url_runner( self ):

        while len(self.TitleQueue) > 0 :
            if self._KillThreads == True:
                return
            self._current_task["Title"] = self.TitleQueue.pop()
            title = self._current_task["Title"][0]
            url = self._current_task["Title"][1]
            self.update_status( "Downloading : " + url )
            code = title.request_manga(url)

            if code != 0:
                messagebox.showerror( "Failed to Connect", "HTML Error " + str(code))
                
            else:
                try: 
                    if self.Title_Dict.get(title.get_title()) == None:
                        self.update_status("Extracting : " + url)
                        title.extract_manga()
                        self.update_status( "Extraction of " + title.get_title() + " Complete" )
                        self.add_title_entry(title.get_title())
                        self.Title_Dict[title.get_title()] = title
                        title.to_json_file(title.save_location)
                        self.update_status( "Sucsessfully added: " + title.get_title() ) 
                    else:
                        messagebox.showerror("Title Already Exists",title.get_title())
                except:
                    messagebox.showerror("Failed to extract","Failed to extract title data from url: " + url)

        self.threads["Title"] = None

    def _download_chapter_runner(self):
        while len(self.ChapterQueue) > 0:
            if self._KillThreads[0] == True:
                return
            self._current_task["Chapter"] = self.ChapterQueue.pop()
            title = self._current_task["Chapter"][0]
            stream = self._current_task["Chapter"][1]
            chapter = self._current_task["Chapter"][2]
            row = self.is_chapter_visable( title, stream, chapter )
            if row != None:
                    row.Info["Download"].set( "Downloading.." )
            self.update_status( "Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) ) )
            code = title.Download_Manga_Chapter( stream.get_id(), chapter.get_chapter_number(), self._current_task["Chapter"][3], self._KillThreads )
            row = self.is_chapter_visable( title, stream,chapter )
            if code == 4:
                return

            elif code != 0:
                self.update_status("Failed to download:\n" + str(chapter) )
                if row != None:
                    row.Info["Download"].set( "Download" )
                    row.update_state("download", True)
                continue
            else:
                self.update_status( "Download of " + title.get_title() + "\n" + str(chapter) + " --- Completed" )
                if row != None:
                    row.Info["Download"].set( "Downloaded" )
                    row.update_state("download")
                    row.update_state("view", "View",True)
                    row.update_state("remove", "Remove",True)

        self.threads["Chapter"]= None

    def _update_stream_runner( self, title_object ):
        self.update_status( "Updating Streams for " + self.selection["Title"].get_title())
        try:
            status = title_object.update_streams()
            if status == 0:
                title_object.to_json_file(title_object.save_location)
                self.update_status( self.selection["Title"].get_title() + "\nUpdated" )
            else:
                messagebox.showerror("Update Error", "Site returned error " + str(status) )
            self.threads["Stream"] = None
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))
