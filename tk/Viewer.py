#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Viewer.py                                                     #
#description     :contains the definition for a custom toplevel widget          #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :defines the viewer toplevel widget                            #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
try:
    from tkinter import Toplevel, Label, Button, Frame, Grid, N, W, E, S, StringVar, Canvas, TOP, CENTER
    from tkinter.ttk import Label, Button, Frame
except:
    from Tkinter import Toplevel, Label, Button, Frame, Grid, N, W, E, S, StringVar, Canvas, TOP, CENTER
    from Tkinter.ttk import Label, Button, Frame

try:
    from ScrollableFrame import ScrollableFrame
except:
    from tk.ScrollableFrame import ScrollableFrame

from PIL import Image, ImageTk
from pygubu.builder import Builder
from zipfile import ZipFile
import shutil, re, os, platform
import pygubu
import logging

logger = logging.getLogger(__name__)
logger.propagate = False
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/tk.viewer.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class Viewer(Toplevel):
    OpenViewers = {}
    Config = {}

    def __init__(self, title, stream, chapter,UI_Tamplate=None,master=None,config=None, **kw):
        if Viewer.get_instance(title, stream, chapter) != None:
            raise Exception("Viewer already open for this Chapter")
        else:
            Toplevel.__init__(self, master=master, **kw)
            self.transient(master)
            self.protocol("WM_DELETE_WINDOW",self.__on_exit)
            self.minsize(200,500)
            self.number_of_pages = -1
            self.current_page_number = 1
            self.chapter = chapter
            self.title = title
            self.stream = stream
            self.save_location =  os.path.join(title.save_location, title.get_directory() )
            self.save_location = os.path.join( self.save_location, stream.get_directory() )
            self.page_image = {}
            self.zoom_percentage = 10
            self.zoom_step = 1
            self.base_width = 1500
            self.base_height = 1200
            self.window_width = 200
            self.window_height = 500

            if Viewer.Config != None:
                if Viewer.Config.get("ViewerLast") != None:
                    #print(Viewer.Config["ViewerLast"])
                    self.window_width = Viewer.Config["ViewerLast"][0]
                    self.window_height = Viewer.Config["ViewerLast"][1]

                if Viewer.Config.get("ZoomPercentage") != None:
                    self.zoom_percentage = Viewer.Config["ZoomPercentage"]

            self.width = self.base_width *  ( self.zoom_percentage / 10)
            self.height = self.base_height * ( self.zoom_percentage / 10)
            self.pageText = StringVar()
            self.pageZoom = StringVar()
            self.Chapter_Title = StringVar()
            self.Chapter_Subtitle = StringVar()
            self.pageZoom.set( str(int( self.zoom_percentage*10)) + "%" )
   
            self.geometry("%dx%d+%d+%d" % (
                    self.window_width,
                    self.window_height,
                    master.winfo_rootx() + (master.winfo_width()/2 - self.window_width),
                    master.winfo_rooty() + (master.winfo_height()/2 - self.window_height)
                )
            )   
            
            if UI_Tamplate != None:
                self.__Load_from_template(UI_Tamplate)
            else:
                self.__Load_default_template()

            self.extract_zip()
            self.pageText.set( str(self.current_page_number) +"/"+str(self.number_of_pages))
            self.update_page(self.current_page_number)

            self.bind("<Right>", self.__on_next)
            self.bind("<Next>", self.__on_next)
            self.bind("<Left>", self.__on_previous)
            self.bind("<Prior>", self.__on_previous)
            self.bind("=", self.__on_scale_increase)
            self.bind("-", self.__on_scale_decrease)
            self.bind("<Configure>", self.__on_window_change)
            self.__PreviousButton["state"] = "disabled"
            Viewer.OpenViewers[hash(self)] = self

    def __Load_from_template(self, template):
        """Loads the viewer widget with custom layout
        
        Arguments:
            template {String} -- name of the template file (without extention)
        """
        self.builder = pygubu.Builder()
        self.builder.add_from_file(template + ".ui")
        self.Chapter_Title = self.builder.tkvariables["Title"]
        self.Chapter_Subtitle = self.builder.tkvariables["Subtitle"]
        self.Chapter_Title.set(self.title.get_title())
        self.Chapter_Subtitle.set("Chapter " + str(self.chapter.get_chapter_number()) +": " + self.chapter.get_chapter_name())

        self.__Nextbutton = self.builder.get_object("NextButton")
        self.__PreviousButton = self.builder.get_object("PrevButton")
        #self.__MainLabel = self.builder.get_object("Title")
        self.__MainLabel.config(textvariable=self.Chapter_Title)
        #self.__SubLabel = self.builder.get_object("Subtitle")
        self.__SubLabel["textvariable"] = self.Chapter_Subtitle
        self.__ExitButton = self.builder.get_object("ExitButton")

        self.__PageNumber = self.builder.get_object("PageLabel")
        self.__Scale = self.builder.get_object("ScaleLabel")
        self.__PlusButton = self.builder.get_object("PlusButton")
        self.__MinusButton = self.builder.get_object("MinusButton")
        self.__pageArea = self.builder.get_object("PageArea")

        self.builder.connect_callbacks(self)

    def __Load_default_template(self):
        """Loads the widget with a default hardcoded layout
        """
        self.__ControlFrame = Frame(master=self, height=20)
        self.__ControlFrame["relief"] = "raised"
        self.__StatusFrame = Frame(master=self)
        self.__StatusFrame["relief"] = "sunken"
        self.Chapter_Title = StringVar()
        self.Chapter_Subtitle = StringVar()
        self.Chapter_Title.set(self.title.get_title())
        self.Chapter_Subtitle.set("Chapter " + str(self.chapter.get_chapter_number()) +": " + self.chapter.get_chapter_name())

        self.__Nextbutton = Button(     master=self.__ControlFrame, width=6, text="Next", command=self.__on_next)
        self.__PreviousButton = Button( master=self.__ControlFrame, width=6, text="Prev",command=self.__on_previous)
        self.__MainLabel = Label(   master=self.__ControlFrame, textvariable=self.Chapter_Title, font=("Verdana", 10, "bold"))
        self.__SubLabel = Label(    master=self.__ControlFrame, textvariable=self.Chapter_Subtitle ,font=("Verdana", 10, "normal"))
        self.__ExitButton = Button( master=self.__ControlFrame, width=6, text="Exit",command=self.__on_exit)

        self.__PageNumber = Label(  master=self.__StatusFrame, textvariable=self.pageText)
        self.__Scale = Label(       master=self.__StatusFrame, textvariable=self.pageZoom)
        self.__PlusButton = Button( master=self.__StatusFrame, width=3, text="+",command=self.__on_scale_increase)
        self.__MinusButton = Button(master=self.__StatusFrame, width=3, text="-",command=self.__on_scale_decrease)
        
        self.__pageArea = ScrollableFrame(master=self)

        Grid.grid_columnconfigure(self, 0, weight=1)
        Grid.grid_rowconfigure(self, 0, weight=0)
        Grid.grid_rowconfigure(self, 1, weight=1)
        Grid.grid_columnconfigure(self.__ControlFrame, 1, weight=1)
        Grid.grid_columnconfigure(self.__StatusFrame, 1, weight=1)

        self.__ControlFrame.grid(   row=0,column=0, sticky=E+W+N)
        self.__Nextbutton.grid(     row=0, column=4, rowspan=2, sticky=N+S)
        self.__PreviousButton.grid( row=0, column=3, rowspan=2, sticky=N+S)
        self.__MainLabel.grid(      row=0, column=1, pady=1)
        self.__SubLabel.grid(       row=1, column=1, pady=1)
        self.__ExitButton.grid(     row=0, column=0, rowspan=2, sticky=N+S)

        self.__StatusFrame.grid(row=2, column=0, sticky=E+W+S, pady=4)
        self.__PageNumber.grid( row=3, column=1)
        self.__Scale.grid(      row=3, column=2, sticky=E)
        self.__PlusButton.grid( row=3, column=4, sticky=E, padx=2, pady=2)
        self.__MinusButton.grid(row=3, column=3, sticky=E, padx=2, pady=2)
        
        self.__pageArea.grid(   row=1, column=0, columnspan=5,sticky=N+E+W+S)
        self.__PageCanvas = Canvas(master=self.__pageArea.get_attach_point(),width=self.width, height=self.height)
        self.__PageCanvas.pack(side=TOP)

    def __hash__(self):
        return hash( (self.title, self.stream.get_id(), self.chapter.get_chapter_number() ) )

    def extract_zip(self):
        zip_path = os.path.join( self.save_location,self.chapter.get_full_title() )
        
        with ZipFile( zip_path + '.zip','r') as zip:
            zip.extractall( zip_path )
            zip.close()
        pages = os.listdir( zip_path )
        self.number_of_pages = len(pages)
        for page in pages:
            elements = re.split('[_.]',page)
            num = int(elements[1])
            self.page_image[ num ] = page

    def remove_pages(self):
        """Removes page images after the viewer closes
        """
        path = os.path.join( self.save_location, self.chapter.get_directory() )
        try:
            shutil.rmtree( path )
        except:
            print("failed to remove pages in location:\n\t" + path)

    def update_page(self, page_number, reset=False):
        """Updates the pages canvas to page with given page number
        
        Arguments:
            page_number {int} -- page number (positive and non-zero)
        """
        if self.page_image.get(page_number) != None:
            path = os.path.join( self.save_location, self.chapter.get_directory() )
            path = os.path.join( path, self.page_image[page_number] )
            #print(path)
            if os.path.isfile(path) == False or page_number == -1:
                pass
                #self.Widgets["Page Image"].set_from_icon_name("gtk-missing-image", 30)
            else:
                load = Image.open(path)
                swidth = int( load.width * ( self.zoom_percentage / 10.0) ) #/  load.width
                sheight = int( load.height * ( self.zoom_percentage / 10.0) )# /  load.height
                load = load.resize((swidth,sheight), Image.ANTIALIAS)
                render = ImageTk.PhotoImage(load)
                self.__PageCanvas["width"] = swidth
                self.__PageCanvas["height"] = sheight
                self.__PageCanvas.create_image(swidth/2,sheight/2,anchor=CENTER, image=render)
                self.__PageCanvas.image = render
                logger.info( f"scaled dimentions - w: {swidth}, h: {sheight}\nwindow dimentions - w: {self.window_width}, h: {self.window_height}" )
                

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def get_instance(title, stream, chapter):
        """Returns the viewer instance with the provided title, stream and chapter
        
        Arguments:
            title {MangaPark object} -- Holds entire title infomation (e.g. title, authors, artists, etc)
            stream {MangaStream object} -- Holds the chapter list for a partitular stream in a Title
            chapter {Chapter object} -- Containts the chapters number, and page list
        
        Returns:
            Viewer inststance or None -- The assosiated active viewer attached to a given title, stream and chapter
        """
        obj_hash = hash( (title, stream.get_id(), chapter.get_chapter_number()))
        return Viewer.OpenViewers.get(obj_hash)
    
    @staticmethod
    def load_config(config):
        """Set the Viewer Config Dictionary
        
        Arguments:
            config {Dictionary object} -- Is a Dictionary that viewer configuration
        """        
        if type( config ) == dict:
            Viewer.Config = config

    # Signal callback methods ---------------------------------------------------------------#

    def __on_window_change(self, event=None):
        self.window_width = self.winfo_width()
        self.window_height = self.winfo_height()


    def __on_next(self, event=None):
        """Signal catcher method for the next button
        
        Keyword Arguments:
            event {tkinter event} -- not used, but to provides compatability for keyboard events binded to this method (default: {None})
        """
        #print("Next button pressed")
        if self.current_page_number < self.number_of_pages:
            self.current_page_number += 1
            self.pageText.set( str(self.current_page_number) +"/"+str(self.number_of_pages))
            self.update_page(self.current_page_number)
            self.__PreviousButton["state"] = "normal"
            if self.current_page_number == self.number_of_pages:
                self.__Nextbutton["state"] = "disable"

    def __on_previous(self, event=None):
        """Signal catcher method for the Previous button
        
        Keyword Arguments:
            event {tkinter event} -- not used, but to provides compatability for keyboard events binded to this method (default: {None})
        """
        #print("Previous button pressed")
        if self.current_page_number > 1:
            self.current_page_number -= 1
            self.pageText.set( str(self.current_page_number) +"/"+str(self.number_of_pages))
            self.update_page(self.current_page_number)
            self.__Nextbutton["state"] = "normal"
            if self.current_page_number == 1:
                self.__PreviousButton["state"] = "disable"

    def __on_scale_decrease(self, event=None):
        """Signal catcher method for the minus button
        
        Keyword Arguments:
            event {tkinter event} -- not used, but to provides compatability for keyboard events binded to this method (default: {None})
        """
        #print("scale decrease button pressed")
        if self.zoom_percentage > 1:
            self.zoom_percentage -= 1
            self.__on_scale()

    def __on_scale_increase(self, event=None):
        """Signal catcher method for the plus button
        
        Keyword Arguments:
            event {tkinter event} -- not used, but to provides compatability for keyboard events binded to this method (default: {None})
        """
        #print("scale increase button pressed")
        if self.zoom_percentage < 20:
            self.zoom_percentage += 1
            self.__on_scale()
            
    def __on_scale(self):
        """scales the current page to specified scale percentage
        """
        self.pageZoom.set( str(int( self.zoom_percentage*10)) + "%" )
        self.update_page(self.current_page_number)

    def __on_exit(self):
        """Custom exit method for when the quit button or X button is activated
        """
        #print("exit button pressed")
        self.remove_pages()
        self.destroy()
        del Viewer.OpenViewers[ hash(self) ]
        if len( Viewer.OpenViewers ) == 0:
            print(f"width: {self.width}, height: {self.height}, Zoom: {self.zoom_percentage}")
            Viewer.Config["ViewerLast"][0] = self.window_width
            Viewer.Config["ViewerLast"][1] = self.window_height
            Viewer.Config["ZoomPercentage"] = self.zoom_percentage
            