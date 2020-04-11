#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :MainWindow.py                                                 #
#description     :Defines the MainWidow for gtk.                                #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :defines a custom gkt window                                   #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk,GLib as glib, GObject
GObject.threads_init()
glib.threads_init()

import os, shutil, threading, re, sys, traceback

from src.controller import control
from src.pluginManager import Manager
#from src.MangaPark import MangaPark_Source
from src.TitleSource import TitleSource
from gtk3.ChapterListRow import ChapterListBoxRow
from gtk3.TitleListBoxRow import TitleListBoxRow
from gtk3.Viewer import Viewer
from gtk3.GUI_Popups import Error_Popup, Warning_Popup, Info_Popup, add_Popup, About_Popup, ask_Popup, Preference_Window

class MainWindow( control, gtk.Window):

    def __init__(self, UI_Main, UI_Viewer, UI_Add_Dialog, *args, **kwargs):
        control.__init__(self)
        gtk.Window.__init__(self, *args, **kwargs)
        
        self.__spinner_status = False
        self.builder = gtk.Builder()
        self.builder.add_from_file(UI_Main+".glade")
        self.About = None
        self.entered_url = None
        self.UI_Viewer = UI_Viewer
        self.UI_Add = UI_Add_Dialog
        self.signal_ids = {}

        self.Widgets["Main Window"]       = self.builder.get_object("Main_Window")
        self.Widgets["Chapter Viewer"]    = None
        self.Widgets["Info Viewer"]       = self.builder.get_object("Manga_info_viewer")
        self.Widgets["Status Spinner"]    = self.builder.get_object("Status_Spinner")
        self.Widgets["Status Label"]      = self.builder.get_object("Status_Label")
        self.Widgets["Title Label"]       = self.builder.get_object("Manga_Title_Label" )
        self.Widgets["Authors Label"]     = self.builder.get_object("Manga_Author_Label")
        self.Widgets["Artists Label"]     = self.builder.get_object("Manga_Artist_label")
        self.Widgets["Genre Label"]       = self.builder.get_object("Manga_Genre_Label")
        self.Widgets["Summary Label"]     = self.builder.get_object("Summary_Data_Label")
        self.Widgets["Stream Select"]     = self.builder.get_object("Stream_Combo_Box")
        self.Widgets["Beginning Button"]  = self.builder.get_object("BeginingButton")
        self.Widgets["Prev Button"]       = self.builder.get_object("PrevButton")
        self.Widgets["Location Select"]   = self.builder.get_object("Location")
        self.Widgets["Next Button"]       = self.builder.get_object("NextButton")
        self.Widgets["End Button"]        = self.builder.get_object("EndButton")
        self.Widgets["Cover"]             = self.builder.get_object("Manga_Cover_Image")
        self.Widgets["Chapter List Box"]  = self.builder.get_object("Chapter_List")
        self.Widgets["Title List"]        = self.builder.get_object("Manga_List")
        self.Widgets["Search Box"]        = self.builder.get_object("Manga_Title_Search")
        self.Widgets["Update Streams"]    = self.builder.get_object("Update_Streams_Button")
        self.Widgets["About"]             = self.builder.get_object("About_Menu_Button")
        self.Widgets["Pref"]              = self.builder.get_object("Preferences_Menu_Button")
        self.Widgets["Link"]              = self.builder.get_object("Manga_Link")
        self.Widgets["Chapter Sort"]      = self.builder.get_object("Sort_Toggle")
        self.Widgets["Sort Image"]        = self.builder.get_object("sort_button_image")
        self.Widgets["Download all chapters Button"]  = self.builder.get_object("download_all_button")
        self.Widgets["Add Title"]                     = self.builder.get_object("Add_Manga_Menu_Button")
        self.Widgets["Title Buttons"] = {}

        self.Widgets["Download all chapters Button"].set_sensitive(True)
        self.Widgets["Download all chapters Button"].set_tooltip_text("Download all chapters in current stream list")
        self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-descending", 1)
        self.Widgets["Chapter Sort"].set_tooltip_text("set to descending order")

        self.signal_ids["Main Window"]         = self.Widgets["Main Window"].connect("delete-event", self._on_quit)
        self.signal_ids["Add Title"]           = self.Widgets["Add Title"].connect("activate",self._on_menu_add)
        self.signal_ids["Pref"]           = self.Widgets["Pref"].connect("activate",self._on_pref)
        self.signal_ids["Update Streams"]      = self.Widgets["Update Streams"].connect("clicked",self._on_update)
        self.signal_ids["Beginning Button"]    = self.Widgets["Beginning Button"].connect("clicked", self._on_beginning)
        self.signal_ids["Prev Button"]         = self.Widgets["Prev Button"].connect("clicked", self._on_prev)
        self.signal_ids["Location Select"]     = self.Widgets["Location Select"].connect("changed", self._on_location_change)
        self.signal_ids["Next Button"]         = self.Widgets["Next Button"].connect("clicked", self._on_next)
        self.signal_ids["End Button"]          = self.Widgets["End Button"].connect("clicked", self._on_end)
        self.signal_ids["Download all chapters Button"] = self.Widgets["Download all chapters Button"].connect("clicked", self._on_download_all)
        self.signal_ids["Search Box"]          = self.Widgets["Search Box"].connect("search-changed",self._on_search_change)
        self.signal_ids["Stream Select"]       = self.Widgets["Stream Select"].connect("changed",self._on_stream_change)
        self.signal_ids["Title List row select"] = self.Widgets["Title List"].connect("row_selected",self._on_list_select)
        self.signal_ids["Title List row change"] = self.Widgets["Title List"].connect("selected-rows-changed",self._on_list_select)
        self.signal_ids["About"]        = self.Widgets["About"].connect("activate", self.about)
        self.signal_ids["Chapter Sort"] = self.Widgets["Chapter Sort"].connect("clicked", self._on_sort)


        self.Widgets["Main Window"].show()
        self._get_title_list_from_file()
        self._load_title_entry()

    def add_title_entry(self, name):
        row = TitleListBoxRow(name)
        row.show()
        self.Widgets["Title Buttons"][row] = name
        index = self._find_insertion_point(name)
        row.connect("remove_row", self._on_remove)
        self.Widgets["Title List"].insert(row, index)
        
        if self.Widgets["Title List"].props.visible == False:
            self.Widgets["Title List"].show()

    def title_exist(self, name):
        for t in self.Title_Dict.keys():
            if t == name:
                return True
        return False

    def update_status(self, turn_on, message=None):

        if turn_on == True and self.__spinner_status == False:
            self.__spinner_status = True
            self.Widgets["Status Spinner"].start()

        elif turn_on == False and self.__spinner_status == True:
            self.__spinner_status = False
            self.Widgets["Status Spinner"].stop()

        if message != None:
            self.Widgets["Status Label"].set_label(message)

    def _find_insertion_point(self, title):
        rows = list(self.Widgets["Title Buttons"].values())
        rows.append(title)
        rows.sort()
        for i in range(0,len(rows)):
            if rows[i] == title:
                return i

    def _is_chapter_visable(self, title, stream, chapter ):
        chapter_hash = hash( (title, stream, chapter) )
        for i in range(0, len(self.Chapter_List) ):
            if chapter_hash == hash(self.Chapter_List[i]):
                return self.Chapter_List[i]
        return None

    def _load_title_entry(self):
        self.update_status(True, "Loading Title List.....")
        for m in self.Title_Dict.keys():      
            self.add_title_entry(m)
        self.Widgets["Title List"].show()
        self.update_status(False,"Loaded Title List")

    def _on_remove_chapter(self, chapter_row):
        print(chapter_row.is_downloaded())
        if chapter_row.is_downloaded() == True:
            print(chapter_row.chapter_path+'/'+chapter_row.chapter.directory+ '.zip')
            if os.path.isfile(chapter_row.chapter_path+'/'+chapter_row.chapter.directory+ '.zip') == True:
                os.remove(chapter_row.chapter_path+'/'+chapter_row.chapter.directory+ '.zip')
                chapter_row.update_state("download", "Download", "Download " + str(chapter_row.chapter), True)
                chapter_row.update_state("remove", "Remove","Chapter " + str(chapter_row.chapter)+ " is not downloaded")
                chapter_row.update_state("view", "View", "Download " + str(chapter_row.chapter) + " before viewing")
                chapter_row.set_is_downloaded(False)

    def _on_sort(self, widget):
        self._sort = not self._sort

        if self._sort == True:
            self.Widgets["Chapter Sort"].set_tooltip_text("set to descending order")
            self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-descending",1)
        else:
            self.Widgets["Sort Image"].set_from_icon_name("gtk-sort-ascending",1)
            self.Widgets["Chapter Sort"].set_tooltip_text("set to ascending order")

        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _update_location_bounds(self):
        self.Widgets["Location Select"].disconnect( self.signal_ids["Location Select"] )
        self.signal_ids["Location Select"] = None

        self.Widgets["Location Select"].remove_all()
        super()._update_location_bounds()

        
        for i in range(1, self.page_location["end"]+1) :
            self.Widgets["Location Select"].append_text( str(i) +"/"+str( self.page_location["end"]) )

        self.signal_ids["Location Select"] = self.Widgets["Location Select"].connect("changed", self._on_location_change)

    def _update_location_controls(self, disable=False):
        self.Widgets["Location Select"].disconnect( self.signal_ids["Location Select"] )
        self.signal_ids["Location Select"] = None

        if disable == True:
            entry = self.Widgets["Location Select"].get_child()
            entry.set_text("")
            self.Widgets["Location Select"].set_sensitive(False)
            self.Widgets["Next Button"].set_sensitive(False)
            self.Widgets["End Button"].set_sensitive(False)
            self.Widgets["Prev Button"].set_sensitive(False)
            self.Widgets["Beginning Button"].set_sensitive(False)

        else:
            entry = self.Widgets["Location Select"].get_child()
            entry.set_text( str( self.page_location["current"]+1) +"/"+ str(self.page_location["end"]))

            if self.page_location["end"] == 1:
                self.Widgets["Next Button"].set_sensitive(False)
                self.Widgets["End Button"].set_sensitive(False)
                self.Widgets["Prev Button"].set_sensitive(False)
                self.Widgets["Beginning Button"].set_sensitive(False)

            elif self.page_location["current"] == self.page_location["end"]-1:
                self.Widgets["Next Button"].set_sensitive(False)
                self.Widgets["End Button"].set_sensitive(False)
                self.Widgets["Prev Button"].set_sensitive(True)
                self.Widgets["Beginning Button"].set_sensitive(True)

            elif self.page_location["current"] == 0 :
                self.Widgets["Next Button"].set_sensitive(True)
                self.Widgets["End Button"].set_sensitive(True)
                self.Widgets["Prev Button"].set_sensitive(False)
                self.Widgets["Beginning Button"].set_sensitive(False)

            else:
                self.Widgets["Next Button"].set_sensitive(True)
                self.Widgets["End Button"].set_sensitive(True)
                self.Widgets["Prev Button"].set_sensitive(True)
                self.Widgets["Beginning Button"].set_sensitive(True)

        self.signal_ids["Location Select"] = self.Widgets["Location Select"].connect("changed", self._on_location_change)

    def _update_title_details(self):
        if self.selection["Title"] != None:
            self.Widgets["Cover"].clear()
            if os.path.isfile(self.selection["Title"].get_cover_location()) == False: 
                self.Widgets["Cover"].set_from_icon_name("gtk-missing-image", 30)
            else:
                self.Widgets["Cover"].set_from_file(self.selection["Title"].get_cover_location())
            self.Widgets["Title Label"].set_label(self.selection["Title"].get_title())
            self.Widgets["Authors Label"].set_label( "Author(s): " + self.selection["Title"].get_Authors_str())
            self.Widgets["Artists Label"].set_label("Artist(s): " + self.selection["Title"].get_Artists_str())
            self.Widgets["Genre Label"].set_label("Genre(s): " + self.selection["Title"].get_Genres_str())
            self.Widgets["Summary Label"].set_label(self.selection["Title"].get_summary())
            self.Widgets["Link"].set_uri(self.selection["Title"].site_url)
            self.Widgets["Link"].set_label("Visit Site")

            if( self.Widgets["Info Viewer"].props.visible == False ):
                self.Widgets["Info Viewer"].show()
        else:
            self.Widgets["Info Viewer"].hide()

    def _check_all_selections(self):
        if self.selection["Title"] != None:
            if self.selection["Stream"] != None:
                if self.selection["Chapter"] != None:
                    return 0
                else:
                    return 1 # no chapter selected
            else: 
                return 2 # no stream selected
        else:
            return 3 # no Title selected

    # Signal callback methods ---------------------------------------------------------------#

    def about(self, widget):
        self.About = About_Popup(self)

    def _on_beginning(self, widget):
        super()._on_beginning()

    def _on_download(self, title, stream, chapter, location):
        id = hash( (title, stream, chapter) )
        if self.in_chapter_queue( id ) == False:
            self.ChapterQueue.appendleft( (title, stream, chapter, location, id) )
            if self.threads["Chapter"] == None:
                self.threads["Chapter"] = threading.Thread( target=self._download_chapter_runner )
                self.threads["Chapter"].start()
            else:
                self.update_status( True, "Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) ) )

    def _on_end(self, widget):
        super()._on_end()

    def _on_download_all(self, widget):
        for c in self.selection["Stream"].get_chapters():
            path = self.selection["Title"].save_location + "/" + self.selection["Title"].get_directory() +'/'+ self.selection["Stream"].get_directory()
            if c.is_downloaded(path) == False:
                self._on_download( self.selection["Title"],self.selection["Stream"], c, path )
        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_menu_add(self, widget):
        Entry_popup = add_Popup(self, self.UI_Add )
        response = Entry_popup.run()

        if response == gtk.ResponseType.OK:
            pattern = re.compile(r"\s")
            self.entered_url = re.subn(pattern,"", self.entered_url)[0]
            urls = self.entered_url.split(',')
            for u in urls: 
                if u == "" or u == None:
                    error = Error_Popup(self,"Invalid","Invalid site domain")
                    error.run()
                    error.destroy()
                else:
                    domain = TitleSource.find_site_domain( u )
                    if self.PluginManager.is_source_supported(domain):
                        title = self.PluginManager.create_instance(domain)
                        self.TitleQueue.appendleft( (title, u) )
                        if self.threads["Title"] == None:
                            self.threads["Title"] = threading.Thread(target=self._add_title_from_url_runner)
                            self.threads["Title"].start()
                    
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

    def _on_next(self, widget):
        super()._on_next()

    def _on_list_select(self, widget, data=None):
        if data != None:
            data = widget.get_selected_row()
            if self.selection["Title"] != self.Title_Dict[ self.Widgets["Title Buttons"][data] ]:
                self.selection["Title"] = self.Title_Dict[ self.Widgets["Title Buttons"][data] ]
                self.selection["Stream"] = None
                self._update_location_controls(disable=True)
                self._update_title_details()
                self._update_stream_dropdown()
                self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_location_change(self, widget):
        print("Location change")
        print(f"Selected text: {widget.get_active_text()}")
        str_elements = widget.get_active_text().split("/")

        if str_elements[0].isnumeric() == True:
            page_num = int(str_elements[0]) -1
            if page_num > self.page_location["end"]:
                page_num = self.page_location["end"]-1
            elif page_num < 0:
                page_num = 0
            self.page_location["current"] = page_num

            self._update_location_controls()
            self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])
        pass

    def _on_pref(self, widget):
        self.Pref_window = Preference_Window(self,"Preference_Window")

    def _on_prev(self, widget):
        super()._on_prev()

    def _on_quit(self, widget, data):
        if self.threads["Chapter"] != None or self.threads["Stream"] != None or self.threads["Title"] != None:
            popup = ask_Popup(self, "Active Downloads", "Do you wish to stop downloads?")
            responce = popup.run()
            popup.destroy()
            if responce == gtk.ResponseType.CANCEL:
                print("Cancel pressed")
                return True
            else:
                self.update_status(True, "Canceling Downloads")
                self._KillThreads = True
                if self.threads["Chapter"] != None:
                    self.threads["Chapter"].join()
                if self.threads["Stream"] != None:
                    self.threads["Stream"].join()
                if self.threads["Title"] != None:
                    self.threads["Title"].join()
                self._export_title_list_to_file()
                self._export_config()
                self.update_status(False)
                gtk.main_quit()
            
        else:
            self.update_status(True, "exporting Title List")
            self._export_title_list_to_file()
            self._export_config()
            self.update_status(False)
            gtk.main_quit()

    def _on_remove(self, widget, data):
        key = self.Widgets["Title Buttons"][data]
        del self.Widgets["Title Buttons"][data]
        self.Widgets["Title List"].remove(data)
        manga_to_delete = self.Title_Dict[key]

        location = manga_to_delete.save_location +'/' + manga_to_delete.directory
        if os.path.isdir(location) == True:
            shutil.rmtree(location)
            del self.Title_Dict[key]
        if manga_to_delete == self.selection["Title"]:
            self.selection["Title"] = None
            self._update_title_details()

    def _on_search_change(self, widget):
        text = widget.get_text()
        if text == "":
            for m in self.Widgets["Title Buttons"]:
                m.show()
        else:
            text = text.lower()
            pattern = re.compile( '(' + text + ')' )
            for m in self.Widgets["Title Buttons"]:
                if re.search(pattern,m.get_text().lower()) != None:
                    m.show()
                else:
                    m.hide()

    def _on_stream_change(self, widget):
        self.selection["Stream"] = self.selection["Title"].get_stream_with_name(widget.get_active_text())
        if self.selection["Stream"] == None:
            entry = self.Widgets["Stream Select"].get_child()
            entry.set_text("")
            self.Widgets["Location Select"].set_sensitive(False)
            self._update_location_controls(disable=True)
        else:
            self.Widgets["Location Select"].set_sensitive(True)
            self._update_location_bounds()
            self._update_location_controls()
        self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"])

    def _on_view(self, number, location):
        self.selection["Chapter"] = self.selection["Stream"].get_chapter(number)
        v = Viewer.get_instance( self.selection["Title"], self.selection["Stream"], self.selection["Chapter"] )
        if v != None:
            popup = Info_Popup(self,"Viewer open","A viewer for this chapter is already open")
            popup.run()
            popup.destroy()
        else:
            Viewer(self,self.UI_Viewer,self.selection["Title"], self.selection["Stream"], self.selection["Chapter"],location)
    
    def _on_update(self, widget):
        status = self._check_all_selections()

        if status <= 2:
            self.update_status(True,"Updating : " +  self.selection["Title"].get_title())
            updater = threading.Thread( target=self._update_stream_runner, args=(self.selection["Title"],) )
            updater.daemon = True
            updater.start()
        else:
            popup = Warning_Popup(self,"No Stream Selected")
            popup.run()
            popup.destroy()

    def _update_chapter_list(self, length=-1, offset=0):
        if self.selection["Stream"] != None:
            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    self.Widgets["Chapter List Box"].remove(r)
                self.Chapter_List = []

            chapters = self.selection["Stream"].get_chapters()
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
                row = ChapterListBoxRow(self,
                    self.selection["Title"],
                    self.selection["Stream"],
                    chapters[i],
                    downloadCommand=self._on_download,
                    removeCommand= self._on_remove_chapter,
                    viewCommand=self._on_view
                )
                self.Chapter_List.append(row)
                self.Widgets["Chapter List Box"].insert(row, i)
        else:
            if len(self.Chapter_List) > 0:
                for r in self.Chapter_List:
                    self.Widgets["Chapter List Box"].remove(r)
                    self.Chapter_List = [] 
 
    def _update_stream_dropdown(self):
        if self.selection["Title"] != None:
            self.Widgets["Stream Select"].remove_all()
            for s in self.selection["Title"].get_streams():
                self.Widgets["Stream Select"].append_text(s.get_name())

    # Static Methods ------------------------------------------------------------------------#

    # Thread worker methods -----------------------------------------------------------------#

    def _add_title_from_url_runner( self ):
        while len( self.TitleQueue ) > 0:
            if self._KillThreads == True:
                return 

            self._current_task["Title"] = self.TitleQueue.pop()
            title = self._current_task["Title"][0]
            url = self._current_task["Title"][1]
            glib.idle_add(self.update_status, True , "Fetching title from " + url)
            code = title.request_manga(url)

            if code != 0:
                error = Error_Popup(self, "Failed to Connect", "HTML Error " + str(code))
                error.run()
                error.destroy()
                
            else:
                try:
                    glib.idle_add(self.update_status, True , "Extracting : " + url)
                    title.extract_manga()
                    glib.idle_add(self.update_status,False, "Extraction Complete")
                    if self.title_exist(title.get_title() ) == False:
                        self.add_title_entry(title.get_title())
                        self.Title_Dict[title.get_title()] = title

                        title.to_json_file(title.save_location)
                        glib.idle_add(self.update_status, False, "Sucsessfully added: " + title.get_title())
                    else:
                        glib.idle_add(self.update_status, False, title.get_title() + " already exists")
                except:
                    glib.idle_add(self.update_status, False, "Failed to extract title from url: " + url)
        self.threads["Title"] = None
        self._current_task["Title"] = None

    def _download_chapter_runner(self):
        while len(self.ChapterQueue) > 0:
            if self._KillThreads[0] == True:
                return
            self._current_task["Chapter"] = self.ChapterQueue.pop()
            title = self._current_task["Chapter"][0]
            stream = self._current_task["Chapter"][1]
            chapter = self._current_task["Chapter"][2]
            row = self._is_chapter_visable( title, stream, chapter )
            if row != None:
                GObject.idle_add( row.update_state,"download", "Downloading...", "Chapter is downloading", False, True )
            GObject.idle_add( self.update_status, True,"Downloading " + title.get_title() + " Chapter  " + str(chapter.get_chapter_number()) + "\nChapters Queued " + str( len(self.ChapterQueue) ) ) 
            code = title.download_title_chapter( stream.get_id(),chapter.get_chapter_number(), self._current_task["Chapter"][3], self._KillThreads )
            row = self._is_chapter_visable( title, stream, chapter )
            if code != 0:
                GObject.idle_add(self.update_status,False, "Failed to download:\n" + str(chapter) )
                if row != None:
                    GObject.idle_add(row.update_state,"download","Download",None,True, False)
            else:
                self.update_status(False, "Download of " + title.get_title() + "\n" + str(chapter) + " --- Completed")
                if row != None:
                    GObject.idle_add(row.update_state,"download", "Downloaded","Chapter "+ str(chapter.get_chapter_number()) + " is already downloaded",False, False)
                    GObject.idle_add(row.update_state,"view", "view", "View chapter "+ str(chapter.get_chapter_number()),True, False)
                    GObject.idle_add(row.update_state,"remove", "Remove","remove chapter "+ str(chapter.get_chapter_number()) + " from local storage?",True, False)
        self._current_task["Chapter"] = None
        self.threads["Chapter"] = None

    def _update_stream_runner( self, title ):
        GObject.idle_add( self.update_status, True, "Updating : " +  self.selection["Title"].get_title())
        try:
            status = title.update_streams()
            if status == 0:
                print("Status " + str(status))
                GObject.idle_add( self._update_chapter_list)
                GObject.idle_add( self.update_status, False, "Updated : " + self.selection["Title"].get_title())
                title.to_json_file(title.save_location)
            else:
                popup = Error_Popup(self,"Update Error", "Site returned error " + str(status))
                popup.run()
                popup.destroy()
            
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))
        self.threads["Stream"] = None
