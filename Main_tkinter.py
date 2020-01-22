#!/usr/bin/python3
# -*- coding: utf-8 -*-
#from tkinter import *
from tkinter import Tk, Button, Frame,Entry,Label, Listbox, Menubutton, Menu, Message,Scrollbar,PanedWindow,LabelFrame,StringVar,Canvas, Text
from tkinter import LEFT, RIGHT, CENTER, TOP, BOTTOM, BOTH, X, Y, N, NE, E, SE, S, SW, W, NW, WORD, DISABLED, INSERT, END, NORMAL,SINGLE,VERTICAL,HORIZONTAL
from tkinter import FLAT, RAISED, SUNKEN, GROOVE, RIDGE
from tkinter import font
from tk.ScrollableFrame import *
from tkinter.ttk import *
from PIL import Image, ImageTk

class Main_Window(Tk):
    
    Verdana_Normal_15 = None
    Verdana_Normal_12 = None
    Verdana_Normal_10 = None
    Verdana_Bold_20 = None

    def __init__(self, *args, **kwargs):
        Tk.__init__(self,*args, **kwargs)
        Main_Window.Verdana_Normal_15 = font.Font(family="Verdana",size=15,weight="normal")
        Main_Window.Verdana_Normal_12 = font.Font(family="Verdana",size=12,weight="normal")
        Main_Window.Verdana_Normal_8 = font.Font(family="Verdana",size=10,weight="normal")
        Main_Window.Verdana_Bold_20 = font.Font(family="Verdana",size=20,weight="bold")
        self.Widgets = {}
        self.title("Mange Reader")
        self.minsize(900,500)
        self["height"] = 500
        self["width"] = 1200
        self["bd"] = 5
        #self["bg"] = "#5c5c5c"
        self.Widgets["Menu"] = Menu_Bar(master=self)
        self.Widgets["Main Frame"] = Frame(master=self)
        self.Widgets["Panel Frames"] = PanedWindow(master=self.Widgets["Main Frame"])
        self.Widgets["Panel Frames"].pack(side = LEFT,fill="both",expand=1)
        #self.Widgets["Panel Frames"]["showhandle"] = True
        self.Widgets["Status Bar"] = StatusBar(master=self)
        self.Widgets["Status Bar"]["height"] = 25
        self.Widgets["Main Frame"].pack(side = TOP,fill="both", expand=1)
        self.Widgets["Status Bar"].pack(side = "bottom", fill=X,expand=0)
        #self.Widgets["Status Bar"]["bg"] = "gray"

        self.Widgets["Title Panel"] = TitleFrame(master=self.Widgets["Panel Frames"])
        self.Widgets["Title Panel"]["width"] = 200
        self.Widgets["Title Panel"]["height"] = 500
        #self.Widgets["Title Panel"]["bg"] = "gray"
        self.Widgets["Panel Frames"].add(self.Widgets["Title Panel"])

        self.Widgets["Info Panel"] = InfoFrame(master=self.Widgets["Panel Frames"])
        self.Widgets["Info Panel"]["width"] = 1000
        self.Widgets["Info Panel"]["height"] = 500
        #self.Widgets["Info Panel"]["bg"] = "#949494"

        self.Widgets["Panel Frames"].add(self.Widgets["Info Panel"])
        self.config(menu = self.Widgets["Menu"])

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
    def __init__(self,master,*args, **kwargs):
        Frame.__init__(self,master,*args, **kwargs)
        self["relief"] = "groove"
        self.Widgets = {}
        self.Widgets["Search Container"] = Frame(master=self)
        self.Widgets["Search Label"] = Label(master=self.Widgets["Search Container"],font=Main_Window.Verdana_Normal_10,text="Search")
        self.Widgets["Search Label"].pack(side=LEFT)

        self.Widgets["Search Bar"] = Entry(master=self.Widgets["Search Container"],font=Main_Window.Verdana_Normal_10)
        self.Widgets["Search Bar"].pack(fill=X,side=LEFT,expand=1)
        self.Widgets["Search Bar"]["width"] = 20
        self.Widgets["Search Container"].pack(fill=X,side=TOP)

        self.Widgets["Title VScroll"] = Scrollbar(master=self)
        self.Widgets["Title VScroll"]["orient"] = VERTICAL
        self.Widgets["Title VScroll"].pack(side = LEFT, fill=Y)

        self.Widgets["Title HScroll"] = Scrollbar(master=self)
        self.Widgets["Title HScroll"]["orient"] = HORIZONTAL
        self.Widgets["Title HScroll"].pack(side = BOTTOM, fill=X)

        self.Widgets["Titles"] = Listbox(master=self,yscrollcommand=self.Widgets["Title VScroll"].set,xscrollcommand=self.Widgets["Title HScroll"].set,font=Main_Window.Verdana_Normal_10)
        self.Widgets["Titles"]["bg"] = "#b0b0b0"
        self.Widgets["Titles"]["font"] = Main_Window.Verdana_Normal_15
        self.Widgets["Titles"]["selectmode"] = SINGLE
        self.Widgets["Titles"]["relief"] = GROOVE
        self.Widgets["Titles"].pack(fill=BOTH,side=LEFT, expand=1)

        self.Widgets["Titles"].insert(END, "asdafasdfsfasf")
        self.Widgets["Title VScroll"].config(command=self.Widgets["Titles"].yview)
        self.Widgets["Title HScroll"].config(command=self.Widgets["Titles"].xview)

    def add_title(self):
        pass
    def remove_title(self):
        pass

class InfoFrame(LabelFrame):
    def __init__(self,master,*args, **kwargs):
        LabelFrame.__init__(self,master,*args, **kwargs)
        self.Widgets = {}
        self.Widgets["Scrollable Canvas"] = Canvas(master=self)
        self.Widgets["Scroll bar"] = Scrollbar(master=self.Widgets["Scrollable Canvas"],orient="vertical", command=Canvas.yview)
        self.Info = {}
        self.Info["Title"] = StringVar()
        self.Info["Authors"] = StringVar()
        self.Info["Artists"] = StringVar()
        self.Info["Genres"] = StringVar()
        self.Info["Summary"] = StringVar()
        self["text"] = "Source Name"
        self["font"] = Main_Window.Verdana_Bold_20
        self["bd"] = 2
        #self["relief"] = "groove"
        self["labelanchor"] = "n"
        #self.Widgets["Image"] = None
        self.__create_Info_frame()
        self.__create_Control_frame()
        self.__create_chapter_frame()

    def update_frame_label(self, label):
        self["text"] = label

    def __create_Info_frame(self):

        self.Widgets["Info Container"] = Frame(master=self)
        self.Widgets["Info Container"].pack(side=TOP, fill=X)
        self.Widgets["Info Container"]["bg"] = "blue"

        self.Widgets["Image Container"] = Frame(master=self.Widgets["Info Container"])
        self.Widgets["Image Container"].pack(side=LEFT)
        self.Widgets["Image Container"]["bd"] = 5
        self.Widgets["Image"] = Canvas(master=self.Widgets["Image Container"])
        self.Widgets["Image"].pack()

        self.Widgets["Details Container"] = Frame(master = self.Widgets["Info Container"])
        self.Widgets["Details Container"].pack(side=LEFT,fill=BOTH,expand=1)
        self.Widgets["Details Container"]["bg"] = "white"
        self.Widgets["Details Container"]["height"] = 80
        
        self.Widgets["Title Label"] = Label(master=self.Widgets["Details Container"],textvariable=self.Info["Title"],font=Main_Window.Verdana_Bold_20)
        self.Widgets["Title Label"]["anchor"] = W
        self.Widgets["Title Label"]["bd"] = 5
        self.Widgets["Title Label"]["relief"] = RAISED
        self.Widgets["Title Label"]["justify"] = LEFT
        self.Widgets["Title Label"].pack(side=TOP, fill=X)

        self.Widgets["Authors Label"] = Label(master=self.Widgets["Details Container"],textvariable=self.Info["Authors"],font=Main_Window.Verdana_Normal_12)
        self.Widgets["Authors Label"]["bd"] = 2
        self.Widgets["Authors Label"]["relief"]= RIDGE
        self.Widgets["Authors Label"]["anchor"] = W
        self.Widgets["Authors Label"].pack(side=TOP,fill=X)

        self.Widgets["Artists Label"] = Label(master=self.Widgets["Details Container"],textvariable=self.Info["Artists"],font=Main_Window.Verdana_Normal_12)
        self.Widgets["Artists Label"]["bd"] = 2
        self.Widgets["Artists Label"]["relief"] = RIDGE
        self.Widgets["Artists Label"]["anchor"] = W
        self.Widgets["Artists Label"].pack(side=TOP, fill=X)

        self.Widgets["Genres Label"] = Label(master=self.Widgets["Details Container"],textvariable=self.Info["Genres"],font=Main_Window.Verdana_Normal_12)
        self.Widgets["Genres Label"]["bd"] = 2
        self.Widgets["Genres Label"]["relief"] = RIDGE
        self.Widgets["Genres Label"]["anchor"] = W
        self.Widgets["Genres Label"].pack(side=TOP,fill=X)

        self.Widgets["Summary Frame"] = LabelFrame(master=self.Widgets["Details Container"], text="Summary",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Summary Frame"]["labelanchor"] = N
        self.Widgets["Summary Frame"].pack(side=TOP,fill="both",expand=1)

        self.Widgets["Summary Label"] = Text(master=self.Widgets["Summary Frame"],font=Main_Window.Verdana_Normal_12) 
        self.Widgets["Summary Label"]["wrap"] = WORD
        self.Widgets["Summary Label"]["width"] = 10
        self.Widgets["Summary Label"]["height"] = 5
        self.Widgets["Summary Label"].pack(side=TOP,fill=BOTH,expand=1)

        self.update_title_details(cover="cover.jpg",title="Title",authors=["Authors"],artists=["Artist"],genres=["Genre"], summary="Test asdassdfaaasd\n\n\n\nsdasdagsfsdfsdfafasdfsfsaff\nasdasdadsa")

    def update_title_details(self, cover, title="",authors=[],artists=[],genres=[],summary=""):
        load = Image.open(cover)
        render = ImageTk.PhotoImage(load)
        self.Widgets["Image"]["width"] = render.width()
        self.Widgets["Image"]["height"] = render.height()
        self.Widgets["Image"].create_image(render.width()/2,render.height()/2,anchor="c", image=render)
        self.Widgets["Image"].image = render
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
        self.Widgets["Summary Label"]["state"] = NORMAL
        if self.Widgets["Summary Label"].see(END) == True:
            self.Widgets["Summary Label"].delete(INSERT,END)
        self.Widgets["Summary Label"].insert(END,summary)
        self.Widgets["Summary Label"]["state"] = DISABLED


    def __create_Control_frame(self):
        self.Widgets["Control Container"] = Frame(master=self)
        self.Widgets["Control Container"].pack(side=TOP,fill=X)
        self.Widgets["Control Container"]["bg"] = "red"
        self.Widgets["Control Container"]["bd"] = "5"
        self.Widgets["Control Container"]["height"] = 50
        #self.Widgets["Control Container"]["relief"] = "raised"
        self.Widgets["Sort Button"] = Button(master=self.Widgets["Control Container"],text="Sort",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Sort Button"].pack(side=RIGHT)
        self.Widgets["Update Button"] = Button(master=self.Widgets["Control Container"],text="Update Streams",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Update Button"].pack(side=RIGHT)
        self.Widgets["Untrack Button"] = Button(master=self.Widgets["Control Container"], text="Remove Title",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Untrack Button"].pack(side=LEFT)
        self.Widgets["Stream Button"] = Menubutton(master=self.Widgets["Control Container"],text="Select Stream",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Stream Button"].pack(side=LEFT,fill=Y)
        self.Widgets["Selection Label"] = Label(master=self.Widgets["Control Container"], text="No Stream Selected",font=Main_Window.Verdana_Normal_12)
        self.Widgets["Selection Label"]["relief"] = SUNKEN
        self.Widgets["Selection Label"]["bd"] = 4
        self.Widgets["Selection Label"].pack(side=LEFT, fill=BOTH,expand=1)

    def update_control(self):
        pass

    def __create_chapter_frame(self):
        self.Widgets["Chapters Container"] = ChapterListBox(master=self)
        self.Widgets["Chapters Container"].pack(side=TOP, fill="both",expand=1)
        self.Widgets["Chapters Container"]["bg"] = "green"

    def update_chapters(self):
        pass

    def __create_empty(self):
        if self.Widgets["Info Container"].winfo_ismapped():
            self.Widgets["Info Container"].pack_forget()
        if self.Widgets["Control Container"].winfo_ismapped():
            self.Widgets["Control Container"].pack_forget()
        if self.Widgets["Chapters Container"].winfo_ismapped():
            self.Widgets["Chapters Container"].pack_forget()
        self.Widgets["Empty"] = Label(master=self,text="No Title Selected", font=Main_Window.Verdana_Bold_20)

    def __update_Chapters(self):
        pass




if __name__ == "__main__":
    main = Main_Window()
    main.mainloop()
    #main = Tk()
    main.style = Style()
    main.style.theme_use("clam")
    #test = ScrollableFrame_pack(master=main)
    #test.pack(expand=1, fill="both")
    #for i in range(50):
    #    Label(test.get_attach_point(), text=str(i)).pack(side=LEFT)

    main.mainloop()