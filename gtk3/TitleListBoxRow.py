#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :TitleListBoxRow.py                                            #
#description     :contains a custom ListBoxRow widget                           #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :defineds a custom ListBoxRow widget                           #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, GObject

class TitleListBoxRow(gtk.ListBoxRow):
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

    def get_text(self):
        return self.text