#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ChapterListRow.py                                             #
#description     :creates a custom gtk ListRowBox and Window  widget            #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Defines a custom gtk ListRowBox and Window object             #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, GObject
from gi.repository import GdkPixbuf
from .GUI_Popups import Error_Popup, Warning_Popup, Info_Popup
from zipfile import ZipFile
import re, os, shutil, threading, sys


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, GObject
from gi.repository import GdkPixbuf

class ChapterListBoxRow(gtk.ListBoxRow):

    def __init__(self, parent, title, stream, chapter, downloadCommand=None,removeCommand=None,viewCommand=None,*args, **kwargs):
        gtk.ListBox.__init__(self, *args, **kwargs)
        self.downloadCommand = downloadCommand
        self.removeCommand = removeCommand
        self.viewCommand = viewCommand
        self.parent = parent
        self.chapter_path = title.save_location + "/" + title.get_directory() +'/'+ stream.get_directory()
        self.title = title
        self.stream = stream
        self.chapter = chapter
        self.RowWidgets = {}
        self.downloaded = False
        self.chapter_number = chapter.get_chapter_number()
        self.RowWidgets["Row Box"] = gtk.Box(spacing=2)
        self.RowWidgets["Row Box"].fill = True
        self.RowWidgets["Row Box"].hexpand = True
        self.RowWidgets["Row Box"].halign = gtk.Align.FILL

        self.RowWidgets["Label"] = gtk.Label(str(self.chapter)) 
        self.RowWidgets["Label"].hexpand = True
        self.RowWidgets["Label"].set_justify(gtk.Justification.LEFT)
        self.RowWidgets["Label"].set_xalign(0.0)
        self.RowWidgets["Label"].set_line_wrap_mode(0)

        self.RowWidgets["Button Box"] = gtk.ButtonBox(spacing=2)
        self.RowWidgets["Button Box"].fill = True

        self.RowWidgets["Spinner"] = gtk.Spinner()
        self.RowWidgets["Download Button"] = gtk.Button()
        self.RowWidgets["Remove Button"] = gtk.Button()
        self.RowWidgets["View Button"] = gtk.Button("View")
        

        if self.chapter.is_downloaded(self.chapter_path) == True:
            self.update_state("remove", "Remove","Remove chapter " + str(self.chapter_number) + " from local storage?", active=True )
            self.update_state("download", "Downloaded", str(self.chapter)+ " is already downloaded")
            self.update_state("view", "View", "View " + str(self.chapter), True) 
            self.set_is_downloaded(True)
        else:
            self.update_state("remove", "Remove","Chapter " + str(self.chapter_number) + " is not downloaded" )
            self.update_state("download", "Download", "Download " + str(self.chapter), active=True)
            self.update_state("view", "View", "Download " + str(self.chapter) + " before viewing")

        if parent._current_task["Chapter"] != None:
            if parent._current_task["Chapter"][4] == hash(self):
                self.update_state("remove", "Remove","Chapter " + str(self.chapter_number) + " is not downloaded" )
                self.update_state("download", "Downloading...", str(self.chapter)+ " is downloading")
                self.update_state("view", "View", "Download " + str(self.chapter) + " before viewing", False, True)
            elif parent.in_chapter_queue( hash(self) ) == True:
                    self.update_state("remove", "Remove","Chapter " + str(self.chapter_number) + " is not downloaded" )
                    self.update_state("download", "pending...", str(self.chapter)+ " is waiting to be download")
                    self.update_state("view", "View", "Download " + str(self.chapter) + " before viewing", False, False)

        self.add(self.RowWidgets["Row Box"])
        self.RowWidgets["Row Box"].pack_start( self.RowWidgets["Label"],1,0,2)
        self.RowWidgets["Row Box"].pack_end( self.RowWidgets["Button Box"] ,0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Spinner"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["View Button"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Download Button"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Remove Button"],0,0,2)
        self.RowWidgets["View Button"].connect("clicked", self._on_view)
        self.RowWidgets["Download Button"].connect("clicked",self._on_download )
        self.RowWidgets["Remove Button"].connect("clicked",self._on_remove )

        self.RowWidgets["Row Box"].show()
        self.RowWidgets["Button Box"].show()
        self.RowWidgets["Label"].show()
        self.RowWidgets["Spinner"].show()
        self.RowWidgets["View Button"].show()
        self.RowWidgets["Download Button"].show()
        self.RowWidgets["Remove Button"].show()
        self.show()

    def __hash__(self):
        return hash( (self.title, self.stream, self.chapter) )

    def is_downloaded(self):
        return self.downloaded

    def set_is_downloaded(self, is_downloaded=False):
        self.downloaded = is_downloaded

    def update_state(self,button, text=None, tooltip=None, active=False, downloading=False):

        if downloading == True:
            self.RowWidgets["Spinner"].start()
        else:
            self.RowWidgets["Spinner"].stop()

        #print(button)
        #print(f"text: {text}")
        if button == "remove":
            #print("changing remove button")
            if text != None:
                self.RowWidgets["Remove Button"].set_label(text)
                self.RowWidgets["Remove Button"].set_tooltip_text(tooltip)
            self.RowWidgets["Remove Button"].set_sensitive(active)

        elif button == "download":
            #print("changing download button")
            if text != None:
                self.RowWidgets["Download Button"].set_label(text)
                self.RowWidgets["Download Button"].set_tooltip_text(tooltip)
            self.RowWidgets["Download Button"].set_sensitive(active)
        elif button == "view":
            #print("changing view button")
            if text != None:
                self.RowWidgets["View Button"].set_label(text)
                self.RowWidgets["View Button"].set_tooltip_text(tooltip)
            self.RowWidgets["View Button"].set_sensitive(active)

    # Signal Handlers -----------------------------------------------------------------------#

    def _on_view(self, widget):
        """ Callback function for view button """
        if self.viewCommand != None:
            self.viewCommand(self.chapter_number, self.chapter_path)

    def _on_download(self, widget):
        """ Callback function for download button """
        if self.downloadCommand != None:
            self.update_state(button="download",text="pending...")
            self.downloadCommand(self.title, self.stream, self.chapter, self.chapter_path)
        
    def _on_remove(self, widget):
        """ Callback function for remove button """
        print("Remove button pressed")
        if self.removeCommand != None:
            self.removeCommand(self)


"""
class ChapterListBoxRow(gtk.ListBoxRow):
    ""A GTK ListboxRow child
       Creates a GTK ListBoxRow with the children being gtksplinner, label and three buttons for each instance
    ""
    active = {}

    def __init__(self,parent_window,manga_object,stream_object,chapter_object,*args,**kwargs):
        gtk.ListBoxRow.__init__(self, *args,**kwargs)
        self.viewer_window = None
        self.parent_window = parent_window
        self.chapters_path =  manga_object.save_location + "/" + manga_object.get_directory() +'/'+ stream_object.get_directory()
        self.manga = manga_object
        self.stream_id = stream_object.id
        self.chapter = chapter_object
        self.RowWidgets = {}
        self.downloaded = False
        self.chapter_number = chapter_object.get_chapter_number()

        self.RowWidgets["Row Box"] = gtk.Box(spacing=2)
        self.RowWidgets["Row Box"].fill = True
        self.RowWidgets["Row Box"].hexpand = True
        self.RowWidgets["Row Box"].halign = gtk.Align.FILL

        self.RowWidgets["Label"] = gtk.Label(str(self.chapter)) 
        self.RowWidgets["Label"].hexpand = True
        self.RowWidgets["Label"].set_justify(gtk.Justification.LEFT)
        self.RowWidgets["Label"].set_xalign(0.0)
        self.RowWidgets["Label"].set_line_wrap_mode(0)

        self.RowWidgets["Button Box"] = gtk.ButtonBox(spacing=2)
        self.RowWidgets["Button Box"].fill = True

        self.RowWidgets["Spinner"] = gtk.Spinner()
        if ChapterListBoxRow.is_thread_active(self.manga,self.stream_id,self.chapter_number) == True:
            self.RowWidgets["Spinner"].start()
        else:
            self.RowWidgets["Spinner"].stop()

        self.RowWidgets["Download Button"] = gtk.Button()
        self.RowWidgets["Remove Button"] = gtk.Button()
        self.RowWidgets["View Button"] = gtk.Button("View")
        if self.chapter.is_downloaded(self.chapters_path) == True:
            self.RowWidgets["Remove Button"].set_label("Remove")
            self.RowWidgets["Remove Button"].set_tooltip_text("Remove chapter " + str(self.chapter_number) + " from local storage?")
            self.RowWidgets["Remove Button"].set_sensitive(True)
            self.RowWidgets["Download Button"].set_label("Downloaded")
            self.RowWidgets["Download Button"].set_tooltip_text(str(self.chapter)+ " is already downloaded")
            self.RowWidgets["Download Button"].set_sensitive(False)
            self.RowWidgets["View Button"].set_tooltip_text("View " + str(self.chapter))
            self.RowWidgets["View Button"].set_sensitive(True)
            self.set_is_downloaded(True)
        else:
            self.RowWidgets["Remove Button"].set_label("Remove")
            self.RowWidgets["Remove Button"].set_tooltip_text("Chapter " + str(self.chapter_number) + " is not downloaded")
            self.RowWidgets["Remove Button"].set_sensitive(False)
            self.RowWidgets["Download Button"].set_label("Download")
            self.RowWidgets["Download Button"].set_tooltip_text("Download " + str(self.chapter))
            self.RowWidgets["Download Button"].set_sensitive(True)
            self.RowWidgets["View Button"].set_tooltip_text("Download " + str(self.chapter) + " before viewing")
            self.RowWidgets["View Button"].set_sensitive(False)

        if ChapterListBoxRow.is_thread_active(self.manga,self.stream_id,self.chapter_number) == True:
            self.RowWidgets["Download Button"].set_label("Downloading...")
            self.RowWidgets["Download Button"].set_tooltip_text("Chapter is Downloading")
            self.RowWidgets["Download Button"].set_sensitive(False)
        
        if ChapterListBoxRow.is_viewing(self.manga,self.stream_id,self.chapter_number) == True:
            self.RowWidgets["View Button"].set_label("Viewing")
            self.RowWidgets["View Button"].set_tooltip_text("Currently Viewing")
            self.RowWidgets["View Button"].set_sensitive(False)
        
        self.add(self.RowWidgets["Row Box"])
        self.RowWidgets["Row Box"].pack_start( self.RowWidgets["Label"],1,0,2)
        self.RowWidgets["Row Box"].pack_end( self.RowWidgets["Button Box"] ,0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Spinner"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["View Button"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Download Button"],0,0,2)
        self.RowWidgets["Button Box"].pack_end(self.RowWidgets["Remove Button"],0,0,2)
        self.RowWidgets["View Button"].connect("clicked", self._on_view_button)
        self.RowWidgets["Download Button"].connect("clicked",self._on_Download_button )
        self.RowWidgets["Remove Button"].connect("clicked",self._on_Delete_Button )

        self.id = hash(self)

        self.add_to_active()
        self.RowWidgets["Row Box"].show()
        self.RowWidgets["Button Box"].show()
        self.RowWidgets["Label"].show()
        self.RowWidgets["Spinner"].show()
        self.RowWidgets["View Button"].show()
        self.RowWidgets["Download Button"].show()
        self.RowWidgets["Remove Button"].show()
        self.show()

    def __del__(self):
        ""ChapterListRowBox destructor""
        ChapterListBoxRow.active[ self.id ]["Instance"] = None

    @staticmethod
    def is_thread_active(manga_key,stream_id,chapter_number):
        ""Checks if a thread assosiated with instance is active""

        id = hash( (manga_key, stream_id,chapter_number) )
        if ChapterListBoxRow.active.get(id) != None:
            if ChapterListBoxRow.active[id]["Thread"] == None:
                return -1
            else:
                return ChapterListBoxRow.active[id]["Thread"].is_alive()
        else:
            return None

    @staticmethod
    def is_viewing(manga_key,stream_id,chapter_number):
        ""Checks if the chapter is already being viewed""
        id = hash( (manga_key, stream_id,chapter_number) )
        if ChapterListBoxRow.active.get(id) != None:
            if ChapterListBoxRow.active[id]["Viewer"] == None:
                return False
            else:
                return True
        else:
            return False

    #@staticmethod
    #def get_instance( manga,stream_id, chapter ):
    #    Gets this chapters ChapterListBoxRow instance from ChapterListBoxRow.active dictionary
    #       if instance is not found return none otherwise return ChapterListBoxRow instance
    #    
    #    id = hash( (manga, stream_id, chapter.get_chapter_number() ) )
    #    if ChapterListBoxRow.active.get(id) != None:
    #        return ChapterListBoxRow.active[id]["Instance"]
    #    else:
    #        return None

    @staticmethod
    def _update_spinner(manga, stream_id , chapter , turn_on=False):
        "" Updates a particuler ChapterListBoxRow instance spinner.
            Assumes the ChapterListBoxInstance is still valid.
        ""
        row = ChapterListBoxRow.get_instance(manga, stream_id,chapter)
        if row != None:
            if turn_on == True:
                row.RowWidgets["Spinner"].start()
            else:
                row.RowWidgets["Spinner"].stop()

    @staticmethod
    def _update_view_button(manga, stream_id, chapter, button_text, tooltip_text,sensitive):
        "" Updates a particuler ChapterListBoxRow instance view button.
            Assumes the ChapterListBoxInstance is still valid.
        ""
        row = ChapterListBoxRow.get_instance(manga, stream_id, chapter  )
        if row != None:     
            row.RowWidgets["View Button"].set_label(button_text)
            row.RowWidgets["View Button"].set_tooltip_text(tooltip_text)
            row.RowWidgets["View Button"].set_sensitive(sensitive)

    @staticmethod
    def _update_remove_button( manga, stream_id, chapter ,button_text, tooltip_text,sensitive):
        "" Updates a particuler ChapterListBoxRow instance remove button.
            Assumes the ChapterListBoxInstance is still valid.
        ""
        row = ChapterListBoxRow.get_instance(manga, stream_id, chapter  )
        if row != None:     
            row.RowWidgets["Remove Button"].set_label(button_text)
            row.RowWidgets["Remove Button"].set_tooltip_text(tooltip_text)
            row.RowWidgets["Remove Button"].set_sensitive(sensitive)

    @staticmethod
    def _update_download_button(manga, stream_id, chapter ,button_text, tooltip_text,sensitive):
        "" Updates a particuler ChapterListBoxRow instance download button.
            Assumes the ChapterListBoxInstance is still valid.
        ""
        row = ChapterListBoxRow.get_instance(manga, stream_id, chapter  )
        if row != None:
            row.RowWidgets["Download Button"].set_label(button_text)
            row.RowWidgets["Download Button"].set_tooltip_text(tooltip_text)
            row.RowWidgets["Download Button"].set_sensitive(sensitive)

    @staticmethod
    def downloader_runner(manga,stream_id,chapter,location,parent):
        # Chapter download thread worker function
        while parent.ChapterQueue.empty() == False:
            if parent._killThreads[0] == True:
                return
            
            task = parent.ChapterQueue.get()

            pass

        data = (manga, stream_id, chapter, location, parent)

        row = ChapterListBoxRow.get_instance(manga, stream_id, chapter)
        id = hash(row)
        if row != None:
            if( ChapterListBoxRow.active[ id ]["Instance"] != None ):
                GObject.idle_add( ChapterListBoxRow._update_spinner,manga, stream_id, chapter, True )

        code = manga.Download_Manga_Chapter(stream_id,chapter.get_chapter_number(), location)
        
        if code != 0:
            GObject.idle_add( parent.update_status, False, "Failed to download" + str(chapter))
            return

        row = ChapterListBoxRow.get_instance(manga, stream_id, chapter)
        id = hash(row)
        if row != None:
            if( ChapterListBoxRow.active[ id ]["Instance"] != None ):
                GObject.idle_add( ChapterListBoxRow._update_spinner,manga, stream_id, chapter, False )
                GObject.idle_add( ChapterListBoxRow._update_download_button,manga,stream_id,chapter, "Downloaded", "Chapter is Downloaded",False)
                GObject.idle_add( ChapterListBoxRow._update_remove_button,manga,stream_id,chapter, "Remove", str(chapter) + " is not downloaded",True)
                GObject.idle_add( ChapterListBoxRow._update_view_button,manga,stream_id,chapter, "View", "View " + str(chapter),True)
        
        ChapterListBoxRow.active[id]["Thread"] = None

    def add_to_active(self):
        #"" add current instance to ChapterListBoxRow.active dictionary""
        id = hash(self)

        if ChapterListBoxRow.active.get(id) != None:
            if ChapterListBoxRow.active[id]["Instance"] == None:
                ChapterListBoxRow.active[id]["Instance"] = self
                return 0
            else:
                return 1
        else:
            ChapterListBoxRow.active[id] = {
                "Viewer" : None,
                "Thread" : None,
                "Instance" : self
            }
            return 0


    def _on_Download_button(self, widget):
        #"" Callback function for download button ""
        #print( "_on_Download_button" )
        #id = hash(self)
        if self.downloaded == False:
            self.parent_window.ChapterQueue.put( (self.manga,self.stream_id,self.chapter,self.chapters_path,self.parent_window) )
            if parent.ChapterQueue.empty() == True: 
                self.downloaded = True
                self.RowWidgets["Download Button"].set_label("Downloading..")
                self.RowWidgets["Download Button"].set_tooltip_text("Chapter is Downloading")
                self.RowWidgets["Download Button"].set_sensitive(False)
                parent.threads["Chapter"] = threading.Thread(target=self.downloader_runner, args=(self.manga,self.stream_id,self.chapter,self.chapters_path,self.parent_window))
                ChapterListBoxRow.active[ self.id ]["Thread"] = parent.threads["Chapter"]
                download_thread.start()
            else:
                #parent.ChapterQueue.
                self.RowWidgets["Download Button"].set_label("Pending...")
                self.RowWidgets["Download Button"].set_tooltip_text("waiting to be downloaded")
                self.RowWidgets["Download Button"].set_sensitive(False)

    def _on_view_button(self,widget):
        #"" Callback function for view button ""
        if self.chapter.is_downloaded(self.chapters_path) == True:
            if self.add_to_active() == 1:
                if ChapterListBoxRow.active[self.id]["Viewer"] == None:
                    viewer_window = ViewerWindow(self.parent_window, "Manga_Reader_Viewer_window.glade",self.manga,self.stream_id,self.chapter,self.chapters_path)
                    ChapterListBoxRow.active[self.id]["Viewer"] = viewer_window
                    self.RowWidgets["View Button"].set_label("Viewing")
                    self.RowWidgets["View Button"].set_sensitive(False)
                else:
                    popup = Warning_Popup(self.parent_window,str(self.chapter) + " is already open")
                    popup.run()
                    popup.destroy()
        else:
            popup = Info_Popup(self.parent_window,"Chapter not download", "Please Download chapter before reading")
            popup.run()
            popup.destroy()

    def _on_Delete_Button(self, widget):
        #""Callback function for delete button
        if self.downloaded == True:
            #print(self.chapters_path+'/'+self.chapter.directory+ '.zip')
            if os.path.isfile(self.chapters_path+'/'+self.chapter.directory+ '.zip') == True:
                os.remove(self.chapters_path+'/'+self.chapter.directory+ '.zip')
                self.RowWidgets["Download Button"].set_tooltip_text("Download " + str(self.chapter))
                self.RowWidgets["Download Button"].set_label(" Download ")
                self.RowWidgets["Download Button"].set_sensitive(True)
                self.RowWidgets["Remove Button"].set_tooltip_text("Chapter " + str(self.chapter)+ " is not downloaded")
                self.RowWidgets["Remove Button"].set_sensitive(False)
                self.RowWidgets["View Button"].set_tooltip_text("Download " + str(self.chapter) + " before viewing")
                self.RowWidgets["View Button"].set_sensitive(False)
                self.downloaded = False
     
    def _on_keep_toggle(self, widget): 
        if self.RowWidgets["Keep Toggle"].get_active() == True:
            self.emit("Keep_Toggled", True, self.manga, self.stream_id, self.chapter)

        elif self.RowWidgets["Keep Toggle"].get_active() == False:
            self.emit("Keep_Toggled", False, self.manga, self.stream_id, self.chapter)

    def get_chapter_number(self):
        return self.chapter_number

    def set_is_downloaded(self, is_downloaded=False):
        self.downloaded = is_downloaded

    def is_downloaded(self):
        return self.downloaded

    @staticmethod
    def delete_viewer( manga_key,stream_id,chapter_key ):
        #print("in delete viewer")
        instance = ChapterListBoxRow.get_instance( manga_key, stream_id, chapter_key )
        #print(instance.id)
        if instance != None:
            ChapterListBoxRow.active[instance.id]["Viewer"] = None
            if ChapterListBoxRow.active[instance.id]["Instance"] != None:
                ChapterListBoxRow._update_view_button( manga_key,stream_id,chapter_key, "View","View " + str(chapter_key), True  )
            elif(ChapterListBoxRow.active[instance.id]["Thread"] == False and 
                ChapterListBoxRow.active[instance.id]["Instance"] == None):
                del ChapterListBoxRow.active[instance.id]


    def __lt__(self, other):
        if isinstance(other, ChapterListBoxRow):
            if self.chapter_number < other.chapter_number:
                return True
        return False
    def __gt__(self, other):
        if isinstance(other, ChapterListBoxRow):
            if self.chapter_number > other.chapter_number:
                return True
        return False
    
    def __hash__(self):
        return hash( (self.manga, self.stream_id, self.chapter_number) ) 

    def isEqual(self, other):
        if isinstance(other, ChapterListBoxRow) == True:
            if self.manga == other.manga:
                if self.stream_id == other.stream_id:
                    if self.chapter_number == other.chapter_number:
                        return True
        return False

"""

#---------------------------------------------------------------------------------------------------------------------
"""
class ViewerWindow(gtk.Window):
    
    def __init__(self, caller_widget ,glade_file,manga_object, stream_id, chapter_object,save_location='./', *args, **kwargs):
        super(ViewerWindow, self).__init__(*args, **kwargs)
        self.caller = caller_widget
        self.current_page_number = 1
        self.number_of_pages = -1
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)
        self.chapter = chapter_object
        self.stream_id = stream_id
        self.manga = manga_object
        self.save_location = save_location
        self.page_image = {}
        self.zoom_percentage = 5
        self.zoom_step = 1
        self.base_width = 1500
        self.base_height = 1200
        self.width = self.base_width *  ( self.zoom_percentage / 10)
        self.height = self.base_height * ( self.zoom_percentage / 10)
        self.Widgets={
            "Viewer Window"     : self.builder.get_object("Viewer_Window"),
            "Window Title"      : self.builder.get_object("Window_Title"),
            "Quit"              : self.builder.get_object("Quit_Button"),
            "Back"              : self.builder.get_object("Back_Button"),
            "Next"              : self.builder.get_object("Forward_Button"),
            "Page Image"        : self.builder.get_object("Page_Image"),
            "Page Number Label" : self.builder.get_object("Page_Number_Label"),
            "Zoom Label" : self.builder.get_object("Zoom_Label")
        }
        self.Widgets["Quit"].connect("clicked",self._on_quit)
        self.Widgets["Quit"].connect("delete-event",self._on_quit)
        #self.Widgets["Back"].connect("clicked",self._on_back)
        #self.Widgets["Next"].connect("clicked",self._on_next)

        self.Widgets["Window Title"].set_title(self.manga.get_title() )
        sub = "Chapter " + str( self.chapter.get_chapter_number() )  + ": " + self.chapter.get_chapter_name()
        self.Widgets["Window Title"].set_subtitle( sub )

        if chapter_object.is_downloaded(self.save_location) != True:
            popup = Error_Popup(self,"Failed to find chapter pages")
            popup.run()
            popup.destroy()
            self.error_quit()
        
        self.extract_zip()
        self.update_page(self.current_page_number)

        #print("Opening viewer")
        self.Widgets["Viewer Window"].show_all()

    def _on_back(self,widget):
        #print("back button pressed")
        if self.current_page_number != 1:
            self.current_page_number -= 1
            self.update_page(self.current_page_number)
            self.Widgets["Next"].set_sensitive(True)

    def _on_next(self,widget):
        #print("next button pressed")
        if self.current_page_number != self.number_of_pages:
            self.current_page_number += 1
            self.update_page(self.current_page_number)
            self.Widgets["Back"].set_sensitive(True)

    def extract_zip(self):
        #print("extracting..")
        #print(self.save_location + '/'+self.chapter.get_full_title() + '.zip' )
        with ZipFile(self.save_location + '/'+self.chapter.get_full_title() + '.zip','r') as zip:
            zip.extractall(self.save_location+'/'+self.chapter.get_full_title() )
        pages = os.listdir(self.save_location+'/'+self.chapter.get_full_title() )
        self.number_of_pages = len(pages)
        for page in pages:
            elements = re.split('[_.]',page)
            #print(elements)
            num = int(elements[1])
            self.page_image[ num ] = page

    def remove_pages(self):
        #print("removing pages")
        #print( self.save_location+'/'+self.chapter.get_directory() )
        shutil.rmtree( self.save_location+'/'+self.chapter.get_directory() )
        #print("pages removed")

    def update_page(self, page_number):
        self.Widgets["Page Image"].clear()
        if self.page_image.get(page_number) != None:
            path = self.save_location +'/'+ self.chapter.get_directory() +"/"+ self.page_image[page_number] 
            #print(path)
            if os.path.isfile(path) == False or page_number == -1: 
                self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)
            else:
                pb = None
                if sys.version_info.major == 3:
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, width=self.width,height=self.height, preserve_aspect_ratio=True)
                elif sys.version_info.major == 2:
                    pb = GdkPixbuf.Pixbuf.new_from_file(path)
                    self.base_width = pb.get_width()
                    self.base_height = pb.get_height()
                    #print("Base_Width: " + str(self.base_width))
                    #print("Base_Height: " + str(self.base_height))
                    #print("Zoom %: " + str( self.zoom_percentage * 10 ))
                    #print(  self.zoom_percentage / 10.0 )
                    self.width = self.base_width * ( self.zoom_percentage / 10.0)
                    self.height = self.base_height * ( self.zoom_percentage / 10.0)
                    #print(self.width)
                    #print(self.height)
                    pb = pb.scale_simple(dest_width=self.width,dest_height=self.height,interp_type = 2)
                self.Widgets["Page Image"].set_from_pixbuf( pb )
                self.Widgets["Page Number Label"].set_label( "Page: " + str(page_number) + "/"+ str(self.number_of_pages) )
        else:
            self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)
        if page_number == 1:
            self.Widgets["Back"].set_sensitive(False)
        elif page_number == self.number_of_pages:
            self.Widgets["Next"].set_sensitive(False)

    def _on_zoom_decrease(self, widget):
        #print(self.zoom_percentage)
        if self.zoom_percentage == 1:
            return
        elif self.zoom_percentage > 1:
            self.zoom_percentage -= self.zoom_step
            #print("\t"+str(self.zoom_percentage))
            percentage_value = self.zoom_percentage/10.0
            precentage_text = str( int ( percentage_value * 100))
            self.Widgets["Zoom Label"].set_label( "Zoom: " + precentage_text + "%")
            self.width = self.base_width * percentage_value
            self.height = self.base_height * percentage_value
            self.update_page(self.current_page_number)
    def _on_zoom_increase(self,widget):
        #print(self.zoom_percentage)
        if self.zoom_percentage < 10:
            self.zoom_percentage += self.zoom_step
            #print("\t"+str( self.zoom_percentage))
            percentage_value = self.zoom_percentage/10.0
            precentage_text = str( int ( percentage_value * 100)) 
            self.Widgets["Zoom Label"].set_label( "Zoom: " + precentage_text + "%" )
            self.width = self.base_width * percentage_value
            self.height = self.base_height * percentage_value
            self.update_page(self.current_page_number)

    def error_quit(self):
        self.Widgets["Viewer Window"].destroy()
        self.destroy()

    def _on_quit(self, widget):
        #print("exiting")
        self.remove_pages()
        ChapterListBoxRow.delete_viewer(self.manga,self.stream_id,self.chapter)
        self.Widgets["Viewer Window"].destroy()
"""