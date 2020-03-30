#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ChapterListRow.py                                             #
#description     :creates a custom gtk ListRowBox and Window  widget            #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
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
                if tooltip != None:
                    self.RowWidgets["Remove Button"].set_tooltip_text(tooltip)
            self.RowWidgets["Remove Button"].set_sensitive(active)

        elif button == "download":
            #print("changing download button")
            if text != None:
                self.RowWidgets["Download Button"].set_label(text)
                if tooltip != None:
                    self.RowWidgets["Download Button"].set_tooltip_text(tooltip)
            self.RowWidgets["Download Button"].set_sensitive(active)
        elif button == "view":
            #print("changing view button")
            if text != None:
                self.RowWidgets["View Button"].set_label(text)
                if tooltip != None:
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