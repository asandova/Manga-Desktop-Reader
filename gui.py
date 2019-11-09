#!/usr/bin/python3
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk,GLib as glib, GObject
from Manga_Park import MangaPark_Source
from Manga_Source import Manga_Source
from GUI_Popups import *

#from multiprocessing.pool import ThreadPool

import threading
import json, os, platform, re

new_manga_url = None
config_string = {}


class MangaListBoxRow(gtk.ListBoxRow):
    def __init__(self,Label_text,*args,**kwargs):
        gtk.ListBoxRow.__init__(self, *args,**kwargs)
        label = gtk.Label(Label_text, xalign=0)
        label.set_line_wrap_mode(0)
        self.add(label)
        self.text = Label_text
        label.show()
        self.show()

    def get_text(self):
        return self.text

class ChapterListBoxRow(gtk.ListBoxRow):
    def __init__(self,Label_text,chapter_number,*args,**kwargs):
        gtk.ListBoxRow.__init__(self, *args,**kwargs)
        label = gtk.Label(Label_text, xalign=0.5)
        label.set_line_wrap_mode(0)
        self.chapter_number = chapter_number
        self.add(label)
        self.text = Label_text
        label.show()
        self.show()
    def get_chapter_number(self):
        return self.chapter_number
        

class ViewerWindow(gtk.Window):
    
    def __init__(self, glade_file,chapter_object,keeped=False,save_location='./', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_page_number = 0
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)
        self.chapter = chapter_object
        self.save_location = save_location
        self.keeped = keeped
        self.page_image = {}
        self.Widgets={
            "Viewer Window" : self.builder.get_object("Viewer_Window"),
            "Window Title" : self.builder.get_object("Window_Title"),
            "Quit" : self.builder.get_object("Quit_Button"),
            "Back" : self.builder.get_object("Back_Button"),
            "Next" : self.builder.get_object("Forward_Button"),
            "Page Image" : self.builder.get_object("Page_Image"),
            "Page Number Label" : self.builder.get_object("Page_Number_Label")
        }
        title = re.split("(: )*", chapter_object.chapter_name)
        print(chapter_object.chapter_name)
        self.Widgets["Window Title"].title = title[0]
        if len(title) > 1:
            self.Widgets["Window Title"].subtitle = title[1]
        self._discover_pages()
        self.update_page(1)

        self.Widgets["Viewer Window"].show_all()

    def _discover_pages(self):
        print (self.save_location +'/'+ self.chapter.get_directory())
        if os.path.exists(  self.save_location +'/'+ self.chapter.get_directory()):
            pages = os.listdir(self.save_location +'/'+ self.chapter.get_directory() )
            print(pages)
            for p in pages:
                elements = re.split("[._]*",p)
                print(elements)
                self.page_image[elements[1]] = p
        else:
            popup = Error_Popup(self, "Chapter Not Found", "Failed to find chapter pages in location:\n" + self.save_location +'/'+ self.chapter.get_directory())
            popup.run()
            popup.destroy()
            self.error_quit()

    def update_page(self, page_number):
        self.Widgets["Page Image"].clear()
        if self.page_image.get(page_number) != None:
            path = self.save_location +'/'+ self.chapter.get_directory() +"/"+ self.page_image[page_number] 
            print(path)
            if os.path.isfile(path) == False or page_number == -1: 
                self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)
            else:
                self.Widgets["Page Image"].set_from_file( path )
        else:
            self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)

    def _on_back_page(self, widget):
        pass
    def _on_next_page(self, widget):
        pass
    def error_quit(self):
        self.Widgets["Viewer Window"].destroy()
        self.destroy()

    def _on_quit(self, widget):
        if self.keeped == False:
            if os.path.exists(self.save_location) == False:
                self.chapter.delete_chapter(self.save_location)

        self.Widgets["Viewer Window"].destroy()

class GUI(gtk.Window):

    def __init__(self, glade_file, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        
        self.entered_url = ""
        self.selected_Manga = None
        self.selected_stream = None
        self.selected_chapter = None
        self.search_locations = []
        self.Manga_Dict = {} # holds all manga instances
        self.Chapter_List = []
        self.Widgets = {
            "Main Window"       : self.builder.get_object("Main_Window"),
            "Chapter Viewer"    : None,
            "Info Viewer"       : self.builder.get_object("Manga_info_viewer"),
            "Status Spinner"    : self.builder.get_object("Status_Spinner"),
            "Status Label"      : self.builder.get_object("Status_Label"),
            "Title Label"       : self.builder.get_object("Manga_Title_Label" ),
            "Authors Label"     : self.builder.get_object("Manga_Author_Label"),
            "Artists Label"     : self.builder.get_object("Manga_Artist_label"),
            "Genre Label"       : self.builder.get_object("Manga_Genre_Label"),
            "Summary Label"     : self.builder.get_object("Summary_Data_Label"),
            "Stream Select"     : self.builder.get_object("Stream_Combo_Box"),
            "Cover"             : self.builder.get_object("Manga_Cover_Image"),
            "Chapter List Box"  : self.builder.get_object("Chapter_List"),
            "Manga List"        : self.builder.get_object("Manga_List"),
            "Search Box"        : self.builder.get_object("Manga_Tile_Search"),
            "View Chapter Button"           : self.builder.get_object("View_Chapter"),
            "Download Chapter Button"       : self.builder.get_object("download_chapter_button"),
            "Download all chapters Button"  : self.builder.get_object("download_all_button"),
            "Chapter Buttons" : [],
            "Manga Title Buttons" : {}

        }
        self.builder.connect_signals(self)
        self.Widgets["Main Window"].connect("delete-event", self.Quit)
        self.Widgets["Main Window"].show()
        self.Widgets["Status Spinner"].stop()
        self.Widgets["Status Label"].set_label("")
        self._get_manga_list_from_file()
        self._load_manga_entry()

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
            for m in dic["Manga List"].keys():
                path = dic["Manga List"][m]
                _m = m.replace(' ', '_')
                cache_path = _m +'/'+ _m+'.json'
                if self._check_manga_cache_exists( path ,cache_path ) == True:
                    manga_object = GUI._read_manga_cache( path +'/'+ cache_path )
                    if manga_object != None:
                        self.Manga_Dict[ m ] = manga_object

            #search for manga not in tracking file
            for search in dic["Search Location(s)"]:
                files = os.listdir(search)
                dirs = []
                if len(files) != 0:
                    for f in files:
                        if os.path.isdir(search + "/"+ f) == True:
                            dirs.append(f)
                    for d in dirs:
                        path = search + "/"+ d + '/' + d + ".json"
                        #print("Path : " + path)
                        if os.path.isfile( path ) == True:
                            manga_object = GUI._read_manga_cache( path)  
                            if manga_object != None:
                                if self.Manga_Dict.get(manga_object.get_title()) == None:
                                    #print(manga_object)
                                    self.Manga_Dict[manga_object.get_title()] = manga_object

    def get_widgets(self):
        return self.Widgets

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

    def _update_Manga_info_veiwer(self):
        if self.selected_Manga != None:
            self.Widgets["Cover"].clear()
            if os.path.isfile(self.selected_Manga.get_cover_location()) == False: 
                self.Widgets["Cover"].set_from_icon_name("gtk-missing-image", 30)
            else:
                self.Widgets["Cover"].set_from_file(self.selected_Manga.get_cover_location())
            self.Widgets["Title Label"].set_label(self.selected_Manga.get_title())
            self.Widgets["Authors Label"].set_label( "Author(s): " + self.selected_Manga.get_Authors_str())
            self.Widgets["Artists Label"].set_label("Artist(s): " + self.selected_Manga.get_Artists_str())
            self.Widgets["Genre Label"].set_label("Genre(s): " + self.selected_Manga.get_Genres_str())
            self.Widgets["Summary Label"].set_label(self.selected_Manga.get_summary())

            if( self.Widgets["Info Viewer"].props.visible == False ):
                self.Widgets["Info Viewer"].show()

    def update_status(self, turn_on, message=""):
        if turn_on == True:
            self.Widgets["Status Label"].set_label(message)
            self.Widgets["Status Spinner"].start()
        else:
            self.Widgets["Status Spinner"].stop()
            self.Widgets["Status Label"].set_label(message)

    def  _load_manga_entry(self):
        self.update_status(True, "Loading Manga List.....")
        for m in self.Manga_Dict.keys():  
            #print("loading Entry: " + str( m ) )     
            self._add_manga_entry(m)
        self.Widgets["Manga List"].show()
        self.update_status(False,"Loaded Manga List")

    def _add_manga_entry(self,name):
        row = MangaListBoxRow(name)
        row.show()
        self.Widgets["Manga Title Buttons"][row] = name
        self.Widgets["Manga List"].add(row)  #add(button)
        if self.Widgets["Manga List"].props.visible == False:
            self.Widgets["Manga List"].show()

    def _on_manga_list_button(self,widget,data=None):
        #print(widget)
        if data != None:
            data = widget.get_selected_row()
            self.selected_Manga =  self.Manga_Dict[ self.Widgets["Manga Title Buttons"][data] ]
            self.selected_stream = None
            self._update_Manga_info_veiwer()
            self._update_stream_dropdown()

    def _on_menu_add(self , data):
        Entry_popup = add_Popup(self,"Manga_Reader_add_manga_dialog.glade")
        response = Entry_popup.run()

        if response == gtk.ResponseType.OK:
            domain = Manga_Source.find_site_domain(self.entered_url)
            if domain == 'mangapark.net' or domain == 'www.mangapark.net':
                manga = MangaPark_Source()
                self.update_status(True, "Connecting...")
                code = manga.request_manga(self.entered_url)
                if code != 0:
                    error = Error_Popup(self, "Failed to Connect", "Error: " + str(code) )
                    error.run()
                    error.destroy()
                    self.update_status(False)
                else:
                    if self.Manga_Dict.get(manga.get_title() ) == None:
                        self.update_status(True, "Extracting ...")
                        manga.extract_manga()
                        self.update_status(True, "Extraction Complete")
                        self._add_manga_entry(manga.get_title())
                        self.Manga_Dict[manga.get_title()] = manga
                        print(manga.save_location)
                        manga.to_json_file(manga.save_location)
                        self.update_status(False)
                    else:
                        error = Error_Popup(self,"Manga Already Exists",manga.get_title() )
                        error.run()
                        error.destroy()
            
            elif domain == None:
                error = Error_Popup(self,"Invalid","Invalid site domain")
                error.run()
                error.destroy()
            else:
                error = Error_Popup(self,"Unsupported Manga Site", domain + " is currently not supported")
                error.run()
                error.destroy()

        elif response == gtk.ResponseType.CANCEL:
            self.entered_url = ""
        
        Entry_popup.destroy()
        
    def Quit(self, widget, data):
        self.export_manga_list_to_file()
        gtk.main_quit()

    def _on_stream_change(self,widget):
        #print(widget.get_active_text())
        self.selected_stream = self.selected_Manga.get_stream_with_name(widget.get_active_text())
        self._update_Chapter_list()

    def _update_stream_dropdown(self):
        if self.selected_Manga != None:
            self.Widgets["Stream Select"].remove_all()
            for s in self.selected_Manga.get_streams():
                self.Widgets["Stream Select"].append_text(s.get_name())
    
    def _update_Chapter_list(self):
            if self.selected_stream != None:
                if len(self.Chapter_List) > 0:
                    #5print("removing chapters")
                    for c in self.Chapter_List:
                        self.Widgets["Chapter List Box"].remove(c)
                    self.Chapter_List = []

                chapters = self.selected_stream.get_chapters()
                for c in chapters:
                    row = ChapterListBoxRow(str(c),c.get_chapter_number()-1)
                    self.Chapter_List.append(row)
                    self.Widgets["Chapter List Box"].add(row)

    def _on_update_stream_button(self,widget):
        if self.selected_Manga != None:
            if self.selected_stream != None:
                pass
            else:
                error = Error_Popup(self,"No Stream Selected", "Please select a manga stream")
                error.run()
                error.destroy()
        else:
            error = Error_Popup(self,"No Manga Selected")
            error.run()
            error.destroy()
        pass

    def _on_chapter_select(self,widget,data=None):
        print(data)
        if data != None:
            self.selected_chapter = self.selected_stream.get_chapter(data.get_chapter_number())
            self.update_status(False, self.selected_Manga.get_title() + "\nSelected " + str(self.selected_chapter) )

    def __check_all_selections(self):
        if self.selected_Manga != None:
            if self.selected_stream != None:
                if self.selected_chapter != None:
                    return 0
                else:
                    return 1
            else:
                return 2
        else:
            return 3

    def _on_viewer_button(self, widget):
        errors = self.__check_all_selections()

        if errors == 0:
            keep = self.selected_Manga.is_keeped(self.selected_stream.id,self.selected_chapter)
            chapters_path =  self.selected_Manga.save_location + "/" + self.selected_Manga.get_directory() +'/'+ self.selected_stream.get_directory()
            print(chapters_path)
            is_downloaded = self.selected_chapter.is_downloaded(chapters_path)
            if is_downloaded == True:
                print("is downloaded")
            else:
                self.update_status(True,self.selected_Manga.get_title() + "\n"+str( self.selected_chapter)+"\t Downloading...")
                print("is not downloaded")
 
                download_thread = threading.Thread( self.selected_Manga.Download_Manga_Chapter, args=[ self.selected_stream.id, self.selected_chapter.get_chapter_number(), "" , keep ] )
                download_thread.start()

                #pool = ThreadPool(processes=1)
                #results = pool.apply_async( self.selected_Manga.Download_Manga_Chapter,(self.selected_stream.id, self.selected_chapter.get_chapter_number(), "" , keep) )
                #self.update_status(True,self.selected_Manga.get_title() + "\n"+str( self.selected_chapter)+"\t Downloading...")
                    
        self.update_status(False)

    def _on_download_chapter_button(self, widget):
        if self.selected_Manga != None:
            if self.selected_stream != None:
                if self.selected_chapter != None:

                    pass
                else:
                    error = Error_Popup(self,"No Chapter selected", "Please select a chapter")
                    error.run()
                    error.destroy()
            else:
                error = Error_Popup(self,"No Stream Selected", "Please select a manga stream")
                error.run()
                error.destroy()
        else:
            error = Error_Popup(self,"No Manga Selected", "Please Select a Manga Series")
            error.run()
            error.destroy()

    def _on_download_all_button(self, widget):
        if self.selected_Manga != None:
            if self.selected_stream != None:
                pass
            else:
                error = Error_Popup(self,"No Stream Selected", "Please select a manga stream")
                error.run()
                error.destroy()
        else:
            error = Error_Popup(self,"No Manga Selected", "Please Select a Manga Series")
            error.run()
            error.destroy()


if __name__ == '__main__':
    if os.path.exists("config.json") == True:
        with open("config.json",'r') as f:
            config_string = f.read()
            config = json.loads(config_string)
    else:
        config["Hide Cache Files"] = True
        config["Hide Download Directory"] = False
        config["Cashe Save Location"] = "./"
        config["Default Download Location"] = "./Manga"
        config["Webdriver Location"] = "./WebDrivers"
        config["default WebDriver"] = "geckodriver"
        config["Search Location(s)"] = []
    
    Manga_Source.set_default_save_location(config["Default Download Location"])
    main = GUI("Manga_Reader_Main_Window.glade")
    gtk.main()
