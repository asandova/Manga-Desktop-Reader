import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, GObject
from gi.repository import GdkPixbuf
from .GUI_Popups import Error_Popup, Warning_Popup, Info_Popup
from zipfile import ZipFile
import re, os, shutil, threading, sys


class Viewer(gtk.Window):
    
    OpenViewers = {}

    def __init__(self, caller_widget ,glade_file,manga_object, stream, chapter_object,save_location='./', *args, **kwargs):
        if Viewer.get_instance(manga_object, stream, chapter_object):
            raise Exception("Viewer already open for this chapter")
        else:
            super(Viewer, self).__init__(*args, **kwargs)
            self.caller = caller_widget
            self.current_page_number = 1
            self.number_of_pages = -1
            self.builder = gtk.Builder()
            self.builder.add_from_file(glade_file)
            self.builder.connect_signals(self)
            self.chapter = chapter_object
            self.stream = stream
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
            
            self.Widgets["Viewer Window"].show_all()
            Viewer.OpenViewers[hash(self)] = self

    def __hash__(self):
        return hash( (self.manga, self.stream.get_id(), self.chapter) )

    def extract_zip(self):
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
        shutil.rmtree( self.save_location+'/'+self.chapter.get_directory() )

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
                    self.width = self.base_width * ( self.zoom_percentage / 10.0)
                    self.height = self.base_height * ( self.zoom_percentage / 10.0)
                    pb = pb.scale_simple(dest_width=self.width,dest_height=self.height,interp_type = 2)
                self.Widgets["Page Image"].set_from_pixbuf( pb )
                self.Widgets["Page Number Label"].set_label( "Page: " + str(page_number) + "/"+ str(self.number_of_pages) )
        else:
            self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)
        if page_number == 1:
            self.Widgets["Back"].set_sensitive(False)
        elif page_number == self.number_of_pages:
            self.Widgets["Next"].set_sensitive(False)

    def _scale(self):
            percentage_value = self.zoom_percentage/10.0
            precentage_text = str( int ( percentage_value * 100)) 
            self.Widgets["Zoom Label"].set_label( "Zoom: " + precentage_text + "%" )
            self.width = self.base_width * percentage_value
            self.height = self.base_height * percentage_value
            self.update_page(self.current_page_number)

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def get_instance(title, stream, chapter):
        obj_hash = hash( ( title, stream.get_id(), chapter) )
        return Viewer.OpenViewers.get(obj_hash)

    # Signal callback methods ---------------------------------------------------------------#

    def _on_back(self,widget):

        if self.current_page_number != 1:
            self.current_page_number -= 1
            self.update_page(self.current_page_number)
            self.Widgets["Next"].set_sensitive(True)

    def _on_next(self,widget):

        if self.current_page_number != self.number_of_pages:
            self.current_page_number += 1
            self.update_page(self.current_page_number)
            self.Widgets["Back"].set_sensitive(True)

    def _on_zoom_decrease(self, widget):

        if self.zoom_percentage == 1:
            return
        elif self.zoom_percentage > 1:
            self.zoom_percentage -= self.zoom_step
            self._scale()

    def _on_zoom_increase(self,widget):

        if self.zoom_percentage < 10:
            self.zoom_percentage += self.zoom_step
            self._scale() 

    def error_quit(self):
        self.Widgets["Viewer Window"].destroy()
        self.destroy()

    def _on_quit(self, widget):

        self.remove_pages()
        del Viewer.OpenViewers[ hash(self) ]
        self.Widgets["Viewer Window"].destroy()
