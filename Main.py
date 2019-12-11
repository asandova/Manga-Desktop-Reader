#!/usr/bin/python3
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk,GLib as glib, GObject
GObject.threads_init()
glib.threads_init()
#from gi.repository.GdkPixbuf import Pixbuf
from Manga_Park import MangaPark_Source
from Manga_Source import Manga_Source
from ChapterListRow import ChapterListBoxRow
from manga_chapter import Chapter
from GUI_Popups import Error_Popup, Warning_Popup, Info_Popup, add_Popup, About_Popup

import threading
import json, os, platform, re, shutil,traceback, sys


class MangaListBoxRow(gtk.ListBoxRow):
    __gsignals__ = { "remove_row" : (GObject.SIGNAL_RUN_FIRST,None,(GObject.TYPE_PYOBJECT,)) }

    def __init__(self,Label_text,*args,**kwargs):
        gtk.ListBoxRow.__init__(self, *args,**kwargs)
        self.RowWidgets = {}
        self.RowWidgets["Box"] = gtk.Box()
        self.RowWidgets["Title Label"] = gtk.Label(Label_text, xalign=0)
        self.RowWidgets["Title Label"].set_line_wrap_mode(0)
        self.RowWidgets["Delete Button"] = gtk.Button.new_from_icon_name("gtk-close",1)
        self.text = Label_text
        self.RowWidgets["Box"].pack_start(self.RowWidgets["Delete Button"],0,0,2)
        self.RowWidgets["Box"].pack_start(self.RowWidgets["Title Label"],0,0,2)
        self.RowWidgets["Delete Button"].connect('clicked',self._on_delete)
        self.add(self.RowWidgets["Box"])
        self.show_all()

    def _on_delete(self, Widget):
        print("Delete row pressed")
        self.emit("remove_row",self)
    """
    def __lt__(self, row):
        titles = []
        titles.append(self.text)
        titles.append(row.text)
        titles.sort()
        if self.text == titles[0]:
            return True
        else:
            return False

    def __gl__(self,row):
        titles = []
        titles.append(self.text)
        titles.append(row.text)
        titles.sort()
        if self.text == titles[1]:
            return True
        else:
            return False

    def __eq__(self, row):
        self_title = self.text
        row_title = row.text
        if self_title == row_title:
            return True
        else:
            return False
    
    def __ne__(self, row):
        print(row)
        if row != None:
            self_title = self.text
            row_title = row.text
            if self_title != row_title:
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash( self.text )
    """
    def get_text(self):
        return self.text

class Main_Window(gtk.Window):

    def __init__(self, glade_file, *args, **kwargs):
        super(Main_Window, self).__init__(*args, **kwargs)
        self.__spinner_status = False
        self.entered_url = None
        self.Selected_Manga = None
        self.Selected_Stream = None
        self.Selected_Chapter = None
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.Chapter_List = []
        self.sort_state = 0 #0 mean sort in descending and 1 for ascending order
        self.Manga_Dict = {}
        self.About = None
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
            "Search Box"        : self.builder.get_object("Manga_Title_Search"),
            "Update Streams"    : self.builder.get_object("Update_Streams_Button"),
            "About"             : self.builder.get_object("About_Menu_Button"),
            "Link"              : self.builder.get_object("Manga_Link"),
            "Chapter Sort"      : self.builder.get_object("Sort_Toggle"),
            "Sort Image"        : self.builder.get_object("sort_button_image"),
            #"View Chapter Button"           : self.builder.get_object("View_Chapter"),
            #"Download Chapter Button"       : self.builder.get_object("download_chapter_button"),
            "Download all chapters Button"  : self.builder.get_object("download_all_button"),
            "Add Manga"                     : self.builder.get_object("Add_Manga_Menu_Button"),
            #"Chapter Buttons" : [],
            "Manga Title Buttons" : {}

        }
        #self.builder.connect_signals(self)
        #self.Widgets["Main Window"].connect("delete-event", self.Quit)
        self.Widgets["Stream Select"].connect("changed",self._on_stream_change)
        self.Widgets["Manga List"].connect("row_selected",self._on_manga_list_button)
        self.Widgets["Manga List"].connect("selected-rows-changed",self._on_manga_list_button)
        self.Widgets["About"].connect("activate",self._on_menu_about)
        self.Widgets["Chapter Sort"].connect("clicked", self._on_sort_clicked)
        #self.Widgets[ "Download all chapters Button"].set_sensitive( False ) 
        #self.Widgets[ "Download all chapters Button"].set_tooltip_text("not Implemented")
        #self.Widgets["Chapter List Box"].connect("row-selected",self._on_chapter_select)
        #self.Widgets["Chapter List Box"].connect("selected-rows-changed",self._on_chapter_select)
        self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-descending",1)
        self.Widgets["Chapter Sort"].set_tooltip_text("set to descending order")

        self.Widgets["Main Window"].show()
    def get_widgets(self):
        return self.Widgets


    def _update_Manga_info_veiwer(self):
        if self.Selected_Manga != None:
            self.Widgets["Cover"].clear()
            if os.path.isfile(self.Selected_Manga.get_cover_location()) == False: 
                self.Widgets["Cover"].set_from_icon_name("gtk-missing-image", 30)
            else:
                self.Widgets["Cover"].set_from_file(self.Selected_Manga.get_cover_location())
            self.Widgets["Title Label"].set_label(self.Selected_Manga.get_title())
            self.Widgets["Authors Label"].set_label( "Author(s): " + self.Selected_Manga.get_Authors_str())
            self.Widgets["Artists Label"].set_label("Artist(s): " + self.Selected_Manga.get_Artists_str())
            self.Widgets["Genre Label"].set_label("Genre(s): " + self.Selected_Manga.get_Genres_str())
            self.Widgets["Summary Label"].set_label(self.Selected_Manga.get_summary())
            #print(self.Selected_Manga.site_url)
            self.Widgets["Link"].set_uri(self.Selected_Manga.site_url)
            self.Widgets["Link"].set_label("Visit Manga Site")

            if( self.Widgets["Info Viewer"].props.visible == False ):
                self.Widgets["Info Viewer"].show()
        else:
            self.Widgets["Info Viewer"].hide()

    def update_status(self, turn_on, message=None):

        if turn_on == True and self.__spinner_status == False:
            self.__spinner_status = True
            self.Widgets["Status Spinner"].start()

        elif turn_on == False and self.__spinner_status == True:
            self.__spinner_status = False
            self.Widgets["Status Spinner"].stop()

        if message != None:
            self.Widgets["Status Label"].set_label(message)

    def _on_manga_list_button(self,widget,data=None):
        #print(widget)
        #print(data)
        if data != None:
            data = widget.get_selected_row()
            self.Selected_Manga = self.Manga_Dict[ self.Widgets["Manga Title Buttons"][data] ]
            self.Selected_stream = None
            self._update_Manga_info_veiwer()
            self._update_stream_dropdown()

    def _on_stream_change(self,widget):
        #print(widget.get_active_text())
        self.Selected_Stream = self.Selected_Manga.get_stream_with_name(widget.get_active_text())
        #print(self.Selected_Stream)
        if self.Selected_Stream == None:
            entry = self.Widgets["Stream Select"].get_child()
            entry.set_text("")
        self._update_Chapter_list()

    def _update_stream_dropdown(self):
        if self.Selected_Manga != None:
            self.Widgets["Stream Select"].remove_all()
            for s in self.Selected_Manga.get_streams():
                self.Widgets["Stream Select"].append_text(s.get_name())
    
    def _update_Chapter_list(self):
        #print("in _update_chapter_list")
        if self.Selected_Stream != None:
            if len(self.Chapter_List) > 0:
                #5print("removing chapters")
                for r in self.Chapter_List:
                    self.Widgets["Chapter List Box"].remove(r)
                self.Chapter_List = []

            chapters = self.Selected_Stream.get_chapters()
            if self.sort_state == 1 :
                chapters.sort(reverse=True)
            else: 
                chapters.sort(reverse=False)
                
            for i in range(0, len(chapters)):
                row = ChapterListBoxRow(self,self.Selected_Manga,self.Selected_Stream,chapters[i])
                self.Chapter_List.append(row)
                self.Widgets["Chapter List Box"].insert(row, i)
        else:
            if len(self.Chapter_List) > 0:
            #5print("removing chapters")
                for r in self.Chapter_List:
                    self.Widgets["Chapter List Box"].remove(r)
                    self.Chapter_List = []

    def _on_sort_clicked(self, widget):
        #print("sort button clicked")
        if self.Selected_Stream != None:
            #print(self.Chapter_List)
            if self.sort_state == 1:
                self.sort_state = 0
                self.Widgets["Chapter Sort"].set_tooltip_text("set to descending order")
                self.Chapter_List.sort()
                self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-descending",1)
            else:
                self.sort_state = 1
                self.Chapter_List.sort(reverse=True)
                self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-ascending",1)
                self.Widgets["Chapter Sort"].set_tooltip_text("set to ascending order")

            #print(self.Widgets["Chapter Buttons"])
            for r in self.Chapter_List:
                self.Widgets["Chapter List Box"].remove(r)

            for i in range(0, len(self.Chapter_List) ):
                self.Widgets["Chapter List Box"].insert(self.Chapter_List[i], i )
                self.Chapter_List[i].show()

    def _on_menu_about(self,widget):
        self.About = About_Popup(self)


    def _on_chapter_keep(self, widget, state, manga, stream_id, chapter):
        print("toggled keep to " + str(state))
        pass
    def _on_chapter_download(self, widget, manga, stream_id, chapter):
        print("Download " + str(chapter))
        pass
    def _on_chapter_delete(self, widget, manga, stream_id, chapter):
        print("Delete " + str(chapter))
        pass

    def _on_chapter_select(self,widget,data=None):
        print(data)
        if data != None:
            self.Selected_Chapter = self.Selected_Stream.get_chapter(data.get_chapter_number())
            self.update_status(False, self.Selected_Manga.get_title() + "\nSelected " + str(self.Selected_Chapter) )

    def _check_all_selections(self):
        if self.Selected_Manga != None:
            if self.Selected_Stream != None:
                if self.Selected_Chapter != None:
                    return 0
                else:
                    return 1 # no chapter selected
            else: 
                return 2 # no stream selected
        else:
            return 3 # no manga Title selected


class Main():
    def __init__(self, Main_Window_Glade, Viewer_Window_Glade, Add_Dialog_Glade):
        self.Active_threads = []
        self.search_locations = []
        self.Main_Window = Main_Window(Main_Window_Glade)
        self.Widgets = self.Main_Window.get_widgets()
        self.Viewer_Window_Glade = Viewer_Window_Glade
        self.Add_Dialog_Glade = Add_Dialog_Glade
        self.Widgets["Main Window"].connect("delete-event", self.Quit)
        self.Widgets["Add Manga"].connect("activate",self._on_menu_add)
        self.Widgets["Update Streams"].connect("clicked",self._update_stream)
        self.Widgets["Download all chapters Button"].set_sensitive(False)
        self.Widgets["Download all chapters Button"].set_tooltip_text("Currently not implemented")
        #self.Widgets[ "Download all chapters Button"].connect("clicked", self._on_download_all)
        self.Widgets["Search Box"].connect("search-changed",self._on_search_change)

        self.Main_Window.update_status(True, "Loading Manga List")
        self._get_manga_list_from_file()
        self._load_manga_entry()
        self.Main_Window.update_status(False, "Loaded Manga List")


    def _on_download_all(self,widget):
        self.Main_Window.Widgets[ "Download all chapters Button"].set_sensitive(False)
        to_download =[]
        path = self.Main_Window.Selected_Manga.save_location +"/" + self.Main_Window.Selected_Manga.get_directory() + "/" + self.Main_Window.Selected_Stream.get_directory()
        for c in self.Main_Window.Selected_Stream.get_chapters():
            if c.is_downloaded(path) == False:
                to_download.append(c)
        download_all = threading.Thread(target=self._download_all_runner,args=(self.Main_Window.Selected_Manga,self.Main_Window.Selected_Stream,path,to_download,))
        download_all.start()

    def _download_all_runner(self,manga,stream,path,chapter_list):
        GObject.idle_add(self.Main_Window.update_status, True, "Beginning Download of " + manga.get_title() + "\nStream " + stream.get_name())
        for c in chapter_list:
            GObject.idle_add(self.Main_Window.update_status, True, "Downloading " + manga.get_title() + " : Stream " + stream.get_name() + "\n" + str(c))
            c.download_chapter(path)
        GObject.idle_add(self.Main_Window.update_status, False, "Downloaded " + manga.get_title() + " : Stream " + stream.get_name())
        

    def Quit(self, widget, data):
        self.Main_Window.update_status(True, "exporting Manga List")
        self.export_manga_list_to_file()
        self.Main_Window.update_status(False)
        gtk.main_quit()

    def _get_manga_list_from_file(self):
        filename = 'tracking_list.json'
        if config['Hide Cache Files']== True:
            if platform.system() == "Windows":
                filename = "$" + filename
            else:
                filename = "." + filename

        if os.path.exists(config["Cashe Save Location"] +'/'+filename) != True:
            print("Cache file not found")
            self.Main_Window.Manga_Dict = {}
            self.Main_Window.search_locations = ["."]
        else:
            cache_string = ""
            with open(config["Cashe Save Location"] +'/'+ filename, 'r') as f:
                cache_string = f.read()
                f.close()
            if cache_string == "":
                self.Main_Window.Manga_Dict = {}
                self.Main_Window.search_locations = ["."]
                return

            dic = json.loads(cache_string)
            if(len(dic) == 0):
                self.Main_Window.Manga_Dict = {}
                self.search_locations = ["."]
                return
            #get manga from tracking file
            #print("Loading manga from tracking list")
            for m in dic["Manga List"].keys():
                path = dic["Manga List"][m]
                _m = m.replace(' ', '_')
                cache_path = _m +'/'+ _m+'.json'
                if self._check_manga_cache_exists( path ,cache_path ) == True:
                    manga_object = Main._read_manga_cache( path +'/'+ cache_path )
                    if manga_object != None:
                        self.Main_Window.Manga_Dict[ m ] = manga_object

            #search for manga not in tracking file
            #print("Searching for untracked Manga")
            for search in config["Search Location(s)"]:
                dirs = os.listdir(search)
                print(dirs)
                for d in dirs:
                    print("Checking " + str(d))
                    path = search + '/'+ d + "/" + d + '.json'
                    if os.path.isfile(path) == True:
                        manga_object = Main._read_manga_cache( path)
                        if manga_object != None:
                            if self.Main_Window.Manga_Dict.get(manga_object.get_title()) == None:
                                #print(manga_object)
                                self.Main_Window.Manga_Dict[manga_object.get_title()] = manga_object
                              
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
        self.Main_Window.update_status(True, "Loading Manga List.....")
        for m in self.Main_Window.Manga_Dict.keys():  
            #print("loading Entry: " + str( m ) )     
            self._add_manga_entry(m)
        self.Widgets["Manga List"].show()
        self.Main_Window.update_status(False,"Loaded Manga List")

    def _on_search_change(self, widget):
        #print(f"Search Changed: {widget.get_text()} ")
        text = widget.get_text()
        if text == "":
            for m in self.Widgets["Manga Title Buttons"]:
                m.show()
        else:
            text = text.lower()
            pattern = re.compile( '(' + text + ')' )
            #print(pattern)
            #print(text)
            for m in self.Widgets["Manga Title Buttons"]:
                #print(m.get_text())
                #print()
                if re.search(pattern,m.get_text().lower()) != None:
                    m.show()
                else:
                    m.hide()

    def _add_manga_entry(self,name):
        row = MangaListBoxRow(name)
        #print(row)
        row.show()
        self.Widgets["Manga Title Buttons"][row] = name
        index = self.__find_insertion_point(name)
        row.connect("remove_row", self._on_remove_manga)
        self.Widgets["Manga List"].insert(row, index)  #add(button)
        
        if self.Widgets["Manga List"].props.visible == False:
            self.Widgets["Manga List"].show()
    
    def __find_insertion_point(self, title):
        rows = list(self.Widgets["Manga Title Buttons"].values())
        #print(rows)
        rows.append(title)
        rows.sort()
        for i in range(0,len(rows)):
            #print(rows[i])
            if rows[i] == title:
                #print(i)
                return i

    def _on_remove_manga(self, Widget, data ):
        #print(Widget)
        key = self.Widgets["Manga Title Buttons"][data]
        del self.Widgets["Manga Title Buttons"][data]
        self.Widgets["Manga List"].remove(data)
        manga_to_delete = self.Main_Window.Manga_Dict[key]
        #print(manga_to_delete.directory)
        #print(self.Main_Window.Manga_Dict[data.text].save_location)
        location = manga_to_delete.save_location +'/' + manga_to_delete.directory
        if os.path.isdir(location) == True:
            shutil.rmtree(location)
            del self.Main_Window.Manga_Dict[key]
            #print(location)
        if manga_to_delete == self.Main_Window.Selected_Manga:
            self.Main_Window.Selected_Manga = None
            self.Main_Window._update_Manga_info_veiwer()

    def _add_manga_from_url_runner( self,manga_object ,url ):
        glib.idle_add(self.Main_Window.update_status, True , url + "\t Downloading...")
        code = manga_object.request_manga(url)

        if code != 0:
            error = Error_Popup(self.Main_Window, "Failed to Connect", "HTML Error " + str(code))
            error.run()
            error.destroy()
            
        else:
            if self.Main_Window.Manga_Dict.get(manga_object.get_title()) == None:
                glib.idle_add(self.Main_Window.update_status, True , manga_object.get_title() + "\t Extracting...")
                manga_object.extract_manga()
                self.Main_Window.update_status(False, "Extraction Complete")
                self._add_manga_entry(manga_object.get_title())
                self.Main_Window.Manga_Dict[manga_object.get_title()] = manga_object
                #print(manga_object.save_location)
                manga_object.to_json_file(manga_object.save_location)
                self.Main_Window.update_status(False, "Sucsessfully added: " + manga_object.get_title())
            else:
                error = Error_Popup(self.Main_Window,"Manga Already Exists",manga_object.get_title() )
                error.run()
                error.destroy()

    def _on_menu_add(self , data):
        Entry_popup = add_Popup(self.Main_Window, self.Add_Dialog_Glade )
        response = Entry_popup.run()

        if response == gtk.ResponseType.OK:
            domain = Manga_Source.find_site_domain(self.Main_Window.entered_url)
            if domain == 'mangapark.net' or domain == 'www.mangapark.net':
                manga = MangaPark_Source()
                #print(manga.save_location)
                runner = threading.Thread(target=self._add_manga_from_url_runner, args=(manga,self.Main_Window.entered_url))
                runner.daemon = True
                runner.start()
            
            elif domain == None:
                error = Error_Popup(self.Main_Window,"Invalid","Invalid site domain")
                error.run()
                error.destroy()
            else:
                error = Error_Popup(self.Main_Window,"Unsupported Manga Site", domain + " is currently not supported")
                error.run()
                error.destroy()

        elif response == gtk.ResponseType.CANCEL:
            self.entered_url = ""
        
        Entry_popup.destroy()

    def export_manga_list_to_file(self):
        filename = 'tracking_list.json'
        if config['Hide Cache Files']== True:
            if platform.system()  == "Windows":
                filename = "$" + filename
            else:
                filename = "." + filename

        dic = { "Number of Manga": len(self.Main_Window.Manga_Dict), "Search Location(s)" : [], "Manga List" : {} }
        for l in self.search_locations:
            dic["Search Location(s)"].append(l)

        for m in self.Main_Window.Manga_Dict.keys():
            dic["Manga List"][m] = self.Main_Window.Manga_Dict[m].save_location

        with open(config["Cashe Save Location"] +'/'+ filename, 'w') as f:
            f.write(json.dumps(dic))
            f.close()

    def _on_download_all_button(self, widget):
        pass

    def _download_all_runner(self):
        pass

    def _update_stream_runner( self, manga_object ):
        GObject.idle_add( self.Main_Window.update_status, True, self.Main_Window.Selected_Manga.get_title() + "\nUpdating Streams...")
        try:

            status = manga_object.update_streams()
            if status == 0:
                print("Status " + str(status))
                GObject.idle_add( self.Main_Window._update_Chapter_list)
                GObject.idle_add( self.Main_Window.update_status, False, self.Main_Window.Selected_Manga.get_title() + "\nUpdated Streams")
                manga_object.to_json_file(manga_object.save_location)
            else:
                popup = Error_Popup(self.Main_Window,"Update Error", "Manga Site returned error " + str(status))
                popup.run()
                popup.destroy()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))

    def _update_stream(self,Widget):
        status = self.Main_Window._check_all_selections()

        if status <= 2:
            self.Main_Window.update_status(True,self.Main_Window.Selected_Manga.get_title() + "\tUpdating Streams...")
            updater = threading.Thread( target=self._update_stream_runner, args=(self.Main_Window.Selected_Manga,) )
            updater.daemon = True
            updater.start()
        else:
            popup = Warning_Popup(self.Main_Window,"No Manga Stream Selected")
            popup.run()
            popup.destroy()


if __name__ == '__main__':
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
    elif platform.system() == "MacOS":
        Chapter.Driver_path += "_mac"
    Manga_Source.set_default_save_location(config["Default Download Location"])
    main = Main("Manga_Reader_Main_Window.glade", "Manga_Reader_Viewer_window.glade", "Manga_Reader_add_manga_dialog.glade")
    gtk.main()
