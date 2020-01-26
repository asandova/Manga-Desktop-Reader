#!/usr/bin/python3
# -*- coding: utf-8 -*-
#from tkinter import *
try:
    from tkinter import Tk, Button, Frame,Entry,Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text
    from tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from tkinter import font
    from tkinter.ttk import *
except:
    from Tkinter import Tk, Button, Frame,Entry,Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text
    from Tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
    from Tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
    from Tkinter import font
    from Tkinter.ttk import *

from tk.ScrollableFrame import *
from tk.ScrollableListBox import *
from PIL import Image, ImageTk

class Main_Window(Tk):
    
    Verdana_Normal_15 = None
    Verdana_Normal_12 = None
    Verdana_Normal_10 = None
    Verdana_Bold_20 = None

    def __init__(self, *args, **kwargs):
        Tk.__init__(self,*args, **kwargs)
        self.__MainFrame = Frame(master=self)
        self.__MainFrame.pack(side=TOP,expand=1,fill=BOTH)
        Main_Window.Verdana_Normal_15 = font.Font(family="Verdana",size=15,weight="normal")
        Main_Window.Verdana_Normal_12 = font.Font(family="Verdana",size=12,weight="normal")
        Main_Window.Verdana_Normal_8 = font.Font(family="Verdana",size=10,weight="normal")
        Main_Window.Verdana_Bold_20 = font.Font(family="Verdana",size=20,weight="bold")
        self.Widgets = {}
        self.title("Mange Reader")
        self.minsize(900,500)
        self["height"] = 500
        self["width"] = 1200
        #self.grid()
        #self["bd"] = 5
        #self["bg"] = "#5c5c5c"
        self.__Menu = Menu_Bar(master=self)

        self.__MainFrame.rowconfigure(0, weight=1)
        self.__MainFrame.columnconfigure(0,weight=1)

        self.__ContentPanels = PanedWindow(master=self.__MainFrame,orient="horizontal")
        self.__ContentPanels.grid(row=0, column=0,columnspan=1, sticky=N+E+W+S)
        #self.__ContentPanels["showhandle"] = True
        self.__TitlePanel = TitleFrame(master=self.__ContentPanels,font=Main_Window.Verdana_Normal_10)
        self.__TitlePanel.pack(side=LEFT,fill=BOTH,expand=1)

        self.__InfoPanel = InfoFrame(master=self.__ContentPanels)
        self.__InfoPanel.pack(side=RIGHT, fill=BOTH, expand=1)

        self.__ContentPanels.add(self.__TitlePanel)
        self.__ContentPanels.add(self.__InfoPanel)

        self.__StatusBar = StatusBar(master=self.__MainFrame)
        self.__StatusBar.grid(row=1,column=0,sticky=E+W)
        #self.Widgets["Menu"] = Menu_Bar(master=self)
        #self.Widgets["Main Frame"] = Frame(master=self)
        #self.Widgets["Panel Frames"] = PanedWindow(master=self.__MainFrame,orient="horizontal")
        #self.Widgets["Panel Frames"].pack(side = TOP,fill="both",expand=1)
        #self.Widgets["Panel Frames"]["showhandle"] = True
        #self.Widgets["Status Bar"] = StatusBar(master=self)
        #self.Widgets["Status Bar"]["height"] = 25
        #self.Widgets["Main Frame"].pack(side = TOP,fill="both", expand=1)
        #self.Widgets["Status Bar"].pack(side = "bottom", fill=X,expand=0)
        #self.Widgets["Status Bar"]["bg"] = "gray"

        #self.Widgets["Title Panel"] = TitleFrame(master=self.Widgets["Panel Frames"],font=Main_Window.Verdana_Normal_10)
        #self.Widgets["Title Panel"]["width"] = 200
        #self.Widgets["Title Panel"]["height"] = 500
        #self.Widgets["Title Panel"]["bg"] = "gray"
        #self.Widgets["Panel Frames"].add(self.Widgets["Title Panel"])

        #self.Widgets["Info Panel"] = InfoFrame(master=self.Widgets["Panel Frames"])
        #self.Widgets["Info Panel"]["width"] = 1000
        #self.Widgets["Info Panel"]["height"] = 500
        #self.Widgets["Info Panel"].pack(side=RIGHT,expand=1, fill=BOTH)
        #self.Widgets["Info Panel"]["bg"] = "#949494"

        #self.Widgets["Panel Frames"].add(self.Widgets["Info Panel"])
        self.config(menu=self.__Menu)
        #self.config(menu = self.Widgets["Menu"])

class Menu_Bar(Menu):
    def __init__(self, master,*args, **kwargs):
        Menu.__init__(self, master,*args, **kwargs)
        self["activeborderwidth"] = 2
        self.Widgets = {}
        #self["bg"] = "#949494"
        self.Widgets["File"] = Menu(self,tearoff=0)
        self.Widgets["File"]["activeborderwidth"] = 3
        self.Widgets["File"].add_command(label="Add Manga (url)",command=Menu_Bar.place_holder)
        self.Widgets["File"].add_separator()
        self.Widgets["File"].add_command(label="quit",command=master.quit)
        self.add_cascade(label="File",menu=self.Widgets["File"])
        self.Widgets["Help"] = Menu(self, tearoff=0)
        self.Widgets["Help"]["activeborderwidth"] = 3
        self.Widgets["Help"].add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help",menu=self.Widgets["Help"])

    @staticmethod
    def place_holder(self):
        pass
    def show_about(self):
        pass

class StatusBar(Frame):
    def __init__(self, master,*args, **kwargs):
        Frame.__init__(self, master,*args, **kwargs)
        self["relief"] = RIDGE
        #self["bd"] = 2
        self.Widgets = {}
        self.Widgets["View Button"] = Button(master=self, text="View Chapter")
        self.Widgets["Download Button"] = Button(master=self, text="Download Chapter")
        self.Widgets["Remove Button"] = Button(master=self,text="Remove Chapter")
        self.Widgets["Remove Button"].pack(side=RIGHT)
        self.Widgets["Download Button"].pack(side=RIGHT)
        self.Widgets["View Button"].pack(side=RIGHT)
        self.Widgets["Status Label"] = Label(master=self)
        self.Widgets["Status Label"].pack(side=LEFT,fill=BOTH,expand=1)

class ChapterListBox(Frame):
    def __init__(self,master,*args, **kwargs):
        Frame.__init__(self,master,*args, **kwargs)
        self.Widgets = {}
        self.Widgets["Scroll"] = Scrollbar(master=self)
        self.Widgets["Scroll"].pack(side=LEFT,fill=Y)
        self.Widgets["Chapter List"] = Listbox(master=self, yscrollcommand=self.Widgets["Scroll"].set )
        self.Widgets["Chapter List"]["selectmode"]=SINGLE
        self.Widgets["Chapter List"].pack(side=LEFT,fill=BOTH,expand=1)
        self.Widgets["Scroll"].config(command = self.Widgets["Chapter List"].yview)

    def add_chapter(self):
        pass

    def update_chapter_entry(self):
        pass

    def remove_chapter(self):
        pass

    def clear(self):
        pass
    
class TitleFrame(Frame):
    def __init__(self,master,font=None,*args, **kwargs):
        Frame.__init__(self,master,*args, **kwargs)
        self["relief"] = "groove"
        self.Widgets = {}
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        self.columnconfigure(0,weight=0)
        self.columnconfigure(1,weight=1)

        self.__SearchLabel = Label( master=self, text="Search" )
        self.__SearchEntry = Entry(master=self)
        self.__TitleList = ScrollableListboxGrid(master=self)

        if font != None:
            self.__SearchEntry["font"] = font
            self.__SearchLabel["font"] = font

        self.__SearchLabel.grid(row=0, column=0,sticky=W)
        self.__SearchEntry.grid(row=0, column=1, sticky=E+W+N)
        self.__TitleList.grid(row=1, column=0, columnspan=2, sticky=N+S+E+W)

    def add_title(self,position, name):
        self.__TitleList.insert(position, name)

    def remove_title(self):
        pass

class InfoFrame(LabelFrame):
    def __init__(self,master,font = None, *args, **kwargs):
        LabelFrame.__init__(self, master, *args, **kwargs)
        self.chapterList=[]
        self.FONT = font
        #self.grid()
        self.__ScrollArea = ScrollableFramePack(master=self)
        self.__ScrollArea["bg"] = "gray"
        self.__ScrollArea["relief"] = "sunken"
        self.__ScrollArea["bd"] = 4
        self.Info = {}
        self["text"] = "Source Name"
        self["relief"] = "groove"
        self["labelanchor"] = "n"
        self.Info["Title"] = StringVar()
        self.Info["Authors"] = StringVar()
        self.Info["Artists"] = StringVar()
        self.Info["Genres"] = StringVar()
        self.Info["Summary"] = StringVar()

        self.__CoverImage = None
        self.__TitleLabel = None
        self.__AuthorLabel = None
        self.__ArtistLabel = None
        self.__GenreLabel = None
        self.__SummaryFrame = None
        self.__Summarylabel = None

        self.__create_Info_frame()
        self.__create_Control_frame()

        self.__ScrollArea.pack(fill=BOTH,expand=1)
        """
        self.__create_chapter_frame()
        """

    def update_frame_label(self, label):
        self["text"] = label

    def __create_Info_frame(self):

        self.__CoverImage = Canvas(master=self.__ScrollArea.get_attach_point())

        self.__TitleLabel = Label(master=self.__ScrollArea.get_attach_point(),
            textvariable=self.Info["Title"])
        self.__TitleLabel["anchor"] = W
        self.__TitleLabel["relief"] = RAISED
        self.__TitleLabel["justify"] = LEFT

        self.__AuthorLabel = Label(master=self.__ScrollArea.get_attach_point(),
            textvariable=self.Info["Authors"])
        self.__AuthorLabel["relief"]= RIDGE
        self.__AuthorLabel["anchor"] = W

        self.__ArtistLabel = Label(master=self.__ScrollArea.get_attach_point(),
            textvariable=self.Info["Artists"])
        self.__ArtistLabel["relief"] = RIDGE
        self.__ArtistLabel["anchor"] = W

        self.__GenreLabel = Label(master=self.__ScrollArea.get_attach_point(),
            textvariable=self.Info["Genres"])
        self.__GenreLabel["relief"] = RIDGE
        self.__GenreLabel["anchor"] = W

        self.__SummaryFrame = LabelFrame(master=self.__ScrollArea.get_attach_point(), text="Summary" )
        self.__SummaryFrame["labelanchor"] = N

        self.__Summarylabel = Text(master=self.__SummaryFrame)
        self.__Summarylabel["wrap"] = WORD
        self.__Summarylabel["width"] = 10
        self.__Summarylabel["height"] = 5

        self.__ScrollArea.grid_columnconfigure(0, weight=0)
        self.__ScrollArea.grid_columnconfigure(1, weight=1)
        self.__ScrollArea.grid_rowconfigure(5,weight=0)

        self.__CoverImage.grid(     row=0, column=0, columnspan=1, rowspan=6, sticky=N+E+S+W)
        self.__TitleLabel.grid(     row=0, column=1, columnspan=4, rowspan=1, sticky=E+W+S+N)
        self.__AuthorLabel.grid(    row=2, column=1, columnspan=4, rowspan=1, sticky=E+W+S+N)
        self.__ArtistLabel.grid(    row=3, column=1, columnspan=4, rowspan=1, sticky=E+W+S+N)
        self.__GenreLabel.grid(     row=4, column=1, columnspan=4, rowspan=1, sticky=E+W+S+N)
        self.__SummaryFrame.grid(   row=5, column=1, columnspan=4, rowspan=1, sticky=N+E+W+S)

        self.__Summarylabel.pack( fill=BOTH, expand=1 )

        self.update_title_details(cover="cover.jpg",title="Title",authors=["Authors"],artists=["Artist"],genres=["Genre"], summary="Test asdassdfaaasd\n\n\n\nsdasdagsfsdfsdfafasdfsfsaff\nasdasdadsa")

    def update_title_details(self, cover, title="",authors=[],artists=[],genres=[],summary=""):
        load = Image.open(cover)
        render = ImageTk.PhotoImage(load)
        self.__CoverImage["width"] = render.width()
        self.__CoverImage["height"] = render.height()
        self.__CoverImage.create_image(render.width()/2,render.height()/2,anchor="c", image=render)
        self.__CoverImage.image = render
        self.Info["Title"].set(title)
        authors_string = "Author(s): "
        artists_string = "Artist(s): "
        genres_string = "Genre(s): "
        for i in range(0, len(authors) ):
            authors_string += authors[i]
            if i != len(authors) - 1:
                authors_string += ","

        for i in range(0, len(artists) ):
            artists_string += artists[i]
            if i != len(artists) - 1:
                artists_string += ","

        for i in range(0, len(genres) ):
            genres_string += genres[i]
            if i != len(genres) - 1:
                genres_string += ","
        self.Info["Authors"].set(authors_string)
        self.Info["Artists"].set(artists_string)
        self.Info["Genres"].set(genres_string)
        self.__Summarylabel["state"] = NORMAL
        if self.__Summarylabel.see(END) == True:
            self.__Summarylabel.delete(INSERT,END)
        self.__Summarylabel.insert(END,summary)
        self.__Summarylabel["state"] = DISABLED

    def __create_Control_frame(self):
        self.__StreamButton = Menubutton(master=self.__ScrollArea.get_attach_point(),text="Select Stream")
        self.__SortButton = Button(master=self.__ScrollArea.get_attach_point(), text="Sort")
        self.__SortButton["width"] = 5
        self.__SelectionLabel = Label(master=self.__ScrollArea.get_attach_point(), text="No Stream Selected")
        self.__UntrackButton = Button(master=self.__ScrollArea.get_attach_point(), text="Remove Title")
        self.__UpdateButton = Button(master=self.__ScrollArea.get_attach_point(), text="Update Streams" )

        self.__ScrollArea.grid_rowconfigure(6,weight=0)

        self.__StreamButton.grid(   row=6, column=0, sticky=W)
        self.__SelectionLabel.grid( row=6, column=1)
        self.__UpdateButton.grid(   row=6, column=2)
        self.__UntrackButton.grid(  row=6, column=3)
        self.__SortButton.grid(     row=6, column=4)

    def update_control(self):
        pass

    def __create_chapter_frame(self):
        self.Widgets["Chapters Container"] = ChapterListBox(master=self)
        self.Widgets["Chapters Container"].pack(side=TOP, fill="both",expand=1)
        #self.Widgets["Chapters Container"]["bg"] = "green"

    def update_chapters(self):
        pass

    def add_chapter(self, index, name):
        pass
    def remove_chapter(self, index, name):
        pass

    def __create_empty(self):
        if self.Widgets["Info Container"].winfo_ismapped():
            self.Widgets["Info Container"].pack_forget()
        if self.Widgets["Control Container"].winfo_ismapped():
            self.Widgets["Control Container"].pack_forget()
        if self.Widgets["Chapters Container"].winfo_ismapped():
            self.Widgets["Chapters Container"].pack_forget()
        self.Widgets["Empty"] = Label(master=self,text="No Title Selected" """, font=Main_Window.Verdana_Bold_20""")

    def __update_Chapters(self):
        pass


if __name__ == "__main__":
    main = Main_Window()
    #main.mainloop()
    #main = Tk()
    main.style = Style()
    #print(main.style.theme_names())
    main.style.theme_use("clam")
    #test = ScrollableFrame_pack(master=main)
    #test.pack(expand=1, fill="both")
    #for i in range(50):
    #    Label(test.get_attach_point(), text=str(i)).pack(side=LEFT)

    main.mainloop()