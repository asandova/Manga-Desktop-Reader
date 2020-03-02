#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Main_tkinter.py                                               #
#description     :The Main driver script for tkinter interface for this project.#
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Main python script for Manga Desktop Reader using TKinter     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

try:
    from tkinter import Tk, Button, Frame,Entry,Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text, messagebox
    from tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from tkinter import font
    from tkinter.ttk import *

except:
    from Tkinter import Tk, Button, Frame,Entry,Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text, messagebox
    from Tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from Tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from Tkinter import font
    from Tkinter.ttk import *

from tk.ScrollableFrame import *
from tk.ScrollableListBox import *

import pygubu, json, os, platform, traceback, sys, shutil
from src.MangaPark import MangaPark_Source
from src.TitleSource import TitleSource
from src.Chapter import Chapter
from tk.ChapterRow import ChapterRow
from tk.popups import add_Window, about_dialog
from tk.Viewer import Viewer
from PIL import Image, ImageTk
from queue import Queue
import threading

class Main_Window(Tk):
    
    Verdana_Normal_12 = ("verdana", 12, "normal")
    Verdana_Normal_11 = ("verdana", 11, "normal")
    Verdana_Bold_15 = ("verdana", 15, "bold")
    Verdana_Bold_13 = ("verdana", 13, "bold")
    Verdana_Bold_11 = ("verdana", 11, "bold")

    def __init__(self, UI_Template, *args, **kwargs):
        Tk.__init__(self,*args, **kwargs)

        self.style = Style()
        try:
            self.style.theme_use("winnative")
        except:
            self.style.theme_use("clam")
        self.selection = {
            "Title"     : None,
            "Stream"    : None,
            "Chapter"   : None
        }
        self.Manga_Dict = {}
        self.Streams = []
        self.Chapter_List = []
        self.search_locations = []
        self.__KillThreads = False
        self.threads = {
            "Title" : None,
            "Stream" : None,
            "Chapter" : None
        }
        self.ChapterQueue = Queue()
        self.TitleQueue = Queue()
        self.title("Mange Reader")
        self.minsize(900,500)
        self["height"] = 500
        self["width"] = 1200

        self.builder = pygubu.Builder()
        self.builder.add_from_file(UI_Template+".ui")
        self.Info = {
            "Title"     : StringVar(),
            "Authors"   : StringVar(),
            "Artists"   : StringVar(),
            "Genres"    : StringVar(),
            "Summary"   : StringVar(),
            "Status"    : StringVar(),
            "Source Name" : StringVar()
        }
        self.__sort = False #False mean sort in descending and True for ascending order
        self.Info["Source Name"].set("Manga Park")

        self.Widgets = {
            "Main Window"       :   self.builder.get_object("MainWindow", master=self),
            "Menu"              :   self.builder.get_object("Menu",master=self),
            "Add Command"       :   self.builder.get_object("AddMangaCommand"),
            "Quit Command"      :   self.builder.get_object("QuitCommand"),    
            "Title Frame"       :   self.builder.get_object("Titleframe"),
            "Title List"        :   None,
            "Add Popup"         :   None,
            "InfoLabelFrame"    :   self.builder.get_object("InfoFrameLabel"),
            "InfoFrame"         :   self.builder.get_object("InfoFrame"),
            "Cover"             :   self.builder.get_object("Cover"),
            "Title Label"       :   self.builder.get_object("TitleLabel"),
            "Author Label"      :   self.builder.get_object("AuthorLabel"),
            "Artist Label"      :   self.builder.get_object("ArtistLabel"),
            "Genre Label"       :   self.builder.get_object("GenreLabel"),
            "Summary Text"      :   self.builder.get_object("SummaryText"),
            "Summary Frame"     :   self.builder.get_object("SummaryFrame"),
            "Stream Select"     :   self.builder.get_object("StreamSelect"),
            "Remove Button"     :   self.builder.get_object("RemoveButton"),
            "Update Button"     :   self.builder.get_object("UpdateButton"),
            "SortButton"        :   self.builder.get_object("SortButton"),
            "Status Label"      :   self.builder.get_object("StatusLabel"),
            "Search Entry"      :   self.builder.get_object("SearchEntry")
        }
        self.Widgets["InfoFrame"].grid_forget()
        self.Widgets["InfoLabelFrame"]["labelwidget"] = Label(textvariable=self.Info["Source Name"], font=self.Verdana_Bold_15)
        
        self.Widgets["Title Label"]["textvariable"] = self.Info["Title"]
        self.Widgets["Title Label"]["font"] = self.Verdana_Bold_13
        self.Widgets["Title Label"]["relief"]= "raised"

        self.Widgets["Author Label"]["textvariable"] = self.Info["Authors"]
        self.Widgets["Author Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Author Label"]["relief"]= "ridge"
        
        self.Widgets["Artist Label"]["textvariable"] = self.Info["Artists"]
        self.Widgets["Artist Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Artist Label"]["relief"]= "ridge"

        self.Widgets["Genre Label"]["textvariable"] = self.Info["Genres"]
        self.Widgets["Genre Label"]["font"] = self.Verdana_Normal_12
        self.Widgets["Genre Label"]["relief"]= "ridge"

        self.Widgets["Summary Frame"]["labelwidget"] = Label(text="Summary", font=self.Verdana_Bold_11)
        self.Widgets["Summary Text"]["font"] = self.Verdana_Normal_11

        self.Widgets["Stream Select"].bind("<<ComboboxSelected>>",self._on_stream_change)
        self.Widgets["Stream Select"].insert(0, "Select Stream")
        self.Widgets["Stream Select"]["state"] = "readonly"
        self.Widgets["Stream Select"]["font"] = self.Verdana_Normal_12

        self.Widgets["Status Label"]["textvariable"] = self.Info["Status"]
        self.Widgets["Update Button"].config(command=self._on_Update)
        
        self.Widgets["Main Window"].pack(fill=BOTH,expand=1)
        self.Widgets["Title List"] = ScrollableListbox(master=self.Widgets["Title Frame"], command=self._on_list_select)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 0, weight=0)
        Grid.grid_rowconfigure(self.Widgets["Title Frame"], 1, weight=1)
        
        self.Widgets["Title List"].grid(row=1,column=0,sticky=N+E+S+W)
        self.config(menu=self.Widgets["Menu"])
        self.Widgets["InfoLabelFrame"]
        self.builder.connect_callbacks(self)        

        self.protocol("WM_DELETE_WINDOW",self.on_quit)

        self._get_manga_list_from_file()
        self._load_manga_entry()

    def _on_list_select(self, val):
        print(val)
        self.selection["Title"] = self.Manga_Dict[val[1]]
        self.selection["Stream"] = None
        if self.Widgets["InfoFrame"].winfo_ismapped() == False:
            self.Widgets["InfoFrame"].grid(row=0,column=0, sticky=N+E+S+W, pady=2, padx=2)
        
        self.update_title_details()
        self._update_stream_dropdown()
        self._update_Chapter_list()
        print("list item selected")

    def on_menu_add(self):
        print("on menu add")
        self.Widgets["Add Popup"] = add_Window(master=self,OKCommand=self.__on_add_responce)
    
    def _add_manga_from_url_runner( self ):
        while self.TitleQueue.empty() == False :
            if self.__KillThreads == True:
                return
            task = self.TitleQueue.get()
            manga_object = task[0]
            self.Info["Status"].set( task[1] +"\n\tDownloading...")
            code = manga_object.request_manga(task[1])

            if code != 0:
                messagebox.showerror( "Failed to Connect", "HTML Error " + str(code))
                
            else:
                if self.Manga_Dict.get(manga_object.get_title()) == None:
                    self.Info["Status"].set( manga_object.get_title() + "\n\tExtracting...")
                    manga_object.extract_manga()

                    self.Info["Status"].set( manga_object.get_title() + "\n\tExtraction Complete")
                    self._add_manga_entry(manga_object.get_title())
                    self.Manga_Dict[manga_object.get_title()] = manga_object
                    manga_object.to_json_file(manga_object.save_location)
                    self.Info["Status"].set( "Sucsessfully added: " + manga_object.get_title())   
                else:
                    messagebox.showerror("Manga Already Exists",manga_object.get_title())

            self.TitleQueue.task_done()
        self.threads["Title"] = None

    def __on_add_responce(self , data):
        domain = TitleSource.find_site_domain(data)
        if domain == 'mangapark.net' or domain == 'www.mangapark.net':
            print("valid responce")
            manga = MangaPark_Source()
            print(manga.save_location)
            self.TitleQueue.put( (manga, data) )
            if self.threads["Title"] == None:
                print("Starting Download Thread")
                self.threads["Title"] = threading.Thread(target=self._add_manga_from_url_runner)
                self.threads["Title"].start()        
            
        elif domain == None:
            print("invalid reponce")
            messagebox.showerror("Invalid","Invalid site domain")
        else:
            print("Invalid responce")
            messagebox.showerror("Unsupported Manga Site",domain + " is currently not supported")

    def on_quit(self):
        print("exporting manga list")
        self.export_manga_list_to_file()
        if self.threads["Title"] != None:
            result = messagebox.askyesno("Active Download", "Do you want to wait title to download?")
            if result == False:
                return
            else:
                self.__KillThreads = True

        if self.threads["Stream"] != None:
            self.Info["Status"].set("Waiting for Stream Update to finish")
            self.threads["Stream"].join()

        if self.threads["Chapter"] != None:
            result = messagebox.askyesno("Active Downloads", "Do you want to wait for chapter(s) to download?")
            if result == False:
                return
            else:
                self.__KillThreads = True
            self.Info["Status"].set("Waiting for Chapter downloads to finish")
            self.threads["Stream"].join()
           
        self.destroy()

    def _on_sort(self):
        self.__sort = not self.__sort
        self._update_Chapter_list()

    def _on_Update(self):
        #status = self.Main_Window._check_all_selections()
        print("Update Stream button pressed")
        print("Updating: " + self.selection["Title"].get_title())

        if self.selection["Title"] != None:
            if self.threads["Stream"] == None:
                #print("Starting Update")
                self.update_status(self.selection["Title"].get_title() + "\tUpdating Streams...")
                self.threads["Stream"] = threading.Thread( target=self._update_stream_runner, args=(self.selection["Title"],) )
                self.threads["Stream"].start()

            elif self.threads["Stream"].is_alive() == False:
                #print("Starting Update")
                self.update_status(self.selection["Title"].get_title() + "\tUpdating Streams...")
                self.threads["Stream"] = threading.Thread( target=self._update_stream_runner, args=(self.selection["Title"],) )
                self.threads["Stream"].start()
            else:
                messagebox.showwarning("Title Update", "An update is in progress. Wait for update to complete before requesting another.")
        else:
            #should never get here
            messagebox.showwarning("Warning","No Manga Stream Selected")

    def _on_Remove(self):
        self.Widgets["InfoFrame"].grid_forget()
        manga_to_delete = self.Manga_Dict[self.selection["Title"].get_title()]

        location = manga_to_delete.save_location +'/' + manga_to_delete.directory
        
        if os.path.isdir(location) == True:
            shutil.rmtree(location)
            del self.Manga_Dict[self.selection["Title"].get_title()]
            self.Widgets["Title List"].delete( self.selection["Title"].get_title() )
        print("Remove button pressed")

    def __on_view(self, number):
        print("view chapter " + str(number))
        self.selection["Chapter"] = self.selection["Stream"].get_chapter(number)
        v = Viewer.get_instance( self.selection["Title"], self.selection["Stream"], self.selection["Chapter"] )
        if v != None:
            messagebox.showinfo("Viewer open", "A viewer for this chapter is already open")
        else:
            Viewer(self.selection["Title"], self.selection["Stream"], self.selection["Chapter"])

    def __on_remove_chapter(self, number):
        pass

    def _on_stream_change(self, event):
        print("Stream change")
        self.selection["Stream"] = self.selection["Title"].get_stream_with_name(
            self.Widgets["Stream Select"].get()
        )
        print(self.Widgets["Stream Select"].get())
        self._update_Chapter_list()

    def _update_stream_dropdown(self):
        if self.selection["Stream"] != None:
            self.Widgets["Stream Select"].delete(0, END)
            self.Widgets["Stream Select"].insert(0,"Select Stream")
        streamlist = self.selection["Title"].get_streams()
        streamlist_names = []
        for i in range(0,len(streamlist)):
            #print(streamlist[i].get_name())
            streamlist_names.append(streamlist[i].get_name())
        self.Widgets["Stream Select"]["values"] = streamlist_names


    def _update_Chapter_list(self):
        #print("in _update_chapter_list")

        if self.selection["Stream"] != None:
            if len(self.Chapter_List) > 0:
                #print("removing chapters")
                for r in self.Chapter_List:
                    r[0].destroy()
                self.Chapter_List = []

            chapters = self.selection["Stream"].get_chapters()
            if self.__sort == True :
                chapters.sort(reverse=True)
            else: 
                chapters.sort(reverse=False)

            for i in range(0, len(chapters)):
                row = ChapterRow(   master=self.Widgets["InfoFrame"],
                                    title=self.selection["Title"],     
                                    stream=self.selection["Stream"],
                                    chapter=chapters[i],
                                    viewcommand=self.__on_view,
                                    downloadcommand=self.__download_chapter
                )
                row.grid(row=8+i, column=0, columnspan=5, sticky=E+W)
                row["relief"] = "groove"

                self.Chapter_List.append( (row , hash(row) )  )
        else:
            if len(self.Chapter_List) > 0:
            #5print("removing chapters")
                for r in self.Chapter_List:
                    print(r[0])
                    r[0].destroy()
                    self.Chapter_List = []

    def __download_chapter(self, title, stream, chapter, location):
        print("Chapter download buttom pressed")
        self.ChapterQueue.put( (title, stream, chapter, location) )
        if self.threads["Chapter"] == None:
            self.threads["Chapter"] = threading.Thread( target=self.__download_chapter_runner )
            self.threads["Chapter"].start()
            

    def  __download_chapter_runner(self):
        while self.ChapterQueue.empty() == False:
            if self.__KillThreads == True:
                return
            task = self.ChapterQueue.get()
            manga = task[0]
            row = self.__is_chapter_visable( task[0], task[1],task[2] )
            if row != None:
                    row.Info["Download"].set( "Downloading.." )

            self.Info["Status"].set("Downloading....\n" +  manga.get_title() + " Chapter  " + str(task[2].get_chapter_number()) )
            #print( f"Title: {manga.get_title()}\nStream: {task[1].get_name()}\nChapter: {task[2].get_chapter_number()}\nSave Location: {task[3]}" )
            code = manga.Download_Manga_Chapter( task[1].get_id(),task[2].get_chapter_number(), task[3] )
            row = self.__is_chapter_visable( task[0], task[1],task[2] )
            if code != 0:
                self.Info["Status"].set("Failed to download:\n" + str(task[2]))
                if row != None:
                    row.Info["Download"].set( "Download" )
                    row.update_state("download", True)
                self.ChapterQueue.task_done()
                continue
            else:
                self.Info["Status"].set("Download of " + manga.get_title() + "\n" + str(task[2]) + " --- Completed")
                if row != None:
                    row.Info["Download"].set( "Downloaded" )
                    row.update_state("download")
                    row.update_state("view", True)
                    row.update_state("remove", True)
                self.ChapterQueue.task_done()

        self.threads["Chapter"]= None

    def __is_chapter_visable( self, title, stream, chapter ):
        chapter_hash = hash( ( title, stream, chapter ) )
        for i in range( 0, len(self.Chapter_List) ):
            if chapter_hash == self.Chapter_List[i][1]:
                return self.Chapter_List[i][0]
        return None

    def update_title_details(self):
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
            #print(self.Selected_Manga.site_url)
        if self.selection["Stream"] != None:
            self._update_Chapter_list()

    def _get_manga_list_from_file(self):
        filename = 'tracking_list.json'
        if config['Hide Cache Files']== True:
            if platform.system() == "Windows":
                filename = "$" + filename
            else:
                filename = "." + filename

        if os.path.exists(config["Cashe Save Location"] +'/'+filename) != True:
            print("Cache file not found")
            self.Manga_Dict = {}
            self.search_locations = ["."]
        else:
            cache_string = ""
            with open(config["Cashe Save Location"] +'/'+ filename, 'r') as f:
                cache_string = f.read()
                f.close()
            if cache_string == "":
                self.Manga_Dict = {}
                self.search_locations = ["."]
                return

            dic = json.loads(cache_string)
            if(len(dic) == 0):
                self.Manga_Dict = {}
                self.search_locations = ["."]
                return
            #get manga from tracking file
            #print("Loading manga from tracking list")
            for m in dic["Manga List"].keys():
                path = dic["Manga List"][m]
                _m = m.replace(' ', '_')
                cache_path = _m +'/'+ _m+'.json'
                if self._check_manga_cache_exists( path ,cache_path ) == True:
                    manga_object = self._read_manga_cache( path +'/'+ cache_path )
                    if manga_object != None:
                        self.Manga_Dict[ m ] = manga_object

            #search for manga not in tracking file
            #print("Searching for untracked Manga")
            for search in config["Search Location(s)"]:
                dirs = os.listdir(search)
                print(dirs)
                for d in dirs:
                    print("Checking " + str(d))
                    path = search + '/'+ d + "/" + d + '.json'
                    if os.path.isfile(path) == True:
                        manga_object = self._read_manga_cache( path)
                        self.search_locations.append(search)
                        if manga_object != None:
                            if self.Manga_Dict.get(manga_object.get_title()) == None:
                                #print(manga_object)
                                self.Manga_Dict[manga_object.get_title()] = manga_object

    def export_manga_list_to_file(self):
        filename = 'tracking_list.json'
        if config['Hide Cache Files']== True:
            if platform.system()  == "Windows":
                filename = "$" + filename
            else:
                filename = "." + filename

        dic = { "Number of Manga": len(self.Manga_Dict), "Search Location(s)" : [], "Manga List" : {} }
        for l in self.search_locations:
            dic["Search Location(s)"].append(l)

        for m in self.Manga_Dict.keys():
            dic["Manga List"][m] = self.Manga_Dict[m].save_location

        with open(config["Cashe Save Location"] +'/'+ filename, 'w') as f:
            f.write(json.dumps(dic))
            f.close()

    @staticmethod
    def _check_manga_cache_exists( search_location,manga_name ):
        #print( search_location + '/' + manga_name)
        if os.path.isfile(search_location+'/'+manga_name):
            #print("exists")
            return True
        else:
            return False

    @staticmethod
    def _read_manga_cache(filename):
        manga_string = ""
        with open(filename, 'r') as f:
            manga_string = f.read()
            f.close()
        manga_dict = json.loads(manga_string)
        if manga_dict["Site Domain"] == "https://mangapark.net":
            manga = MangaPark_Source()
            manga.from_dict(manga_dict)
            return manga
        else:
            return None

    def  _load_manga_entry(self):
        self.update_status( "Loading Manga List.....")
        for m in self.Manga_Dict.keys():  
            #print("loading Entry: " + str( m ) )     
            self._add_manga_entry(m)
        #self.Widgets["Manga List"].show()
        self.update_status("Loaded Manga List")

    def _add_manga_entry(self,name):
        self.Widgets["Title List"].insert(name)

    def update_status(self, message=None):

        if message != None:
            self.Info["Status"].set(message)
            #self.Widgets["Status Label"].set(message)

    def _update_stream_runner( self, manga_object ):
        #GObject.idle_add( self.Main_Window.update_status, True, self.Main_Window.Selected_Manga.get_title() + "\nUpdating Streams...")
        self.Info["Status"].set(self.selection["Title"].get_title() + "\nUpdating Streams...")
        try:

            status = manga_object.update_streams()
            if status == 0:
                print("Status " + str(status))
                manga_object.to_json_file(manga_object.save_location)
                self.Info["Status"].set(self.selection["Title"].get_title() + "\nUpdated")
            else:
                messagebox.showerror("Update Error", "Site returned error " + str(status) )
            self.threads["Stream"] = None
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))

    def about(self):
        about_dialog(master=self)


if __name__ == "__main__":
    config = {}
    if os.path.exists("config.json") == True:
        with open("config.json",'r') as f:
            config_string = f.read()
            config = json.loads(config_string)
    else:
        config["Hide Cache Files"] = True
        config["Hide Download Directory"] = False
        config["Cashe Save Location"] = "."
        config["Default Download Location"] = "./Manga"
        config["Webdriver Location"] = "./WebDrivers"
        config["Browser Version"] = "2.45"
        config["Browser"] = "Chrome"
        config["Search Location(s)"] = []

    if os.path.isdir(config["Default Download Location"]) == False:
        os.makedirs( config["Default Download Location"] )

    Chapter.Driver_path = config["Webdriver Location"] +'/'+config["Browser"] +'/'+ config["Browser Version"] +'/'+ "chromedriver"
    Chapter.Driver_type = config["Browser"]
    print(Chapter.Driver_path)
    if platform.system() == "Windows":
        Chapter.Driver_path += ".exe"
    elif platform.system() == "Linux":
        Chapter.Driver_path += "_Linux"
    TitleSource.set_default_save_location(config["Default Download Location"])
    main = Main_Window( UI_Template=config["UI"]["Main"] )

    main.mainloop()