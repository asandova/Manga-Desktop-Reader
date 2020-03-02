#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ChapterListRow.py                                             #
#description     :creates a custom gtk popups                                   #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Defines a custom gtk popups                                   #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

class About_Popup(gtk.AboutDialog):
    def __init__(self, *args, **kwargs):
        gtk.AboutDialog.__init__(self,*args, **kwargs)
        self.set_program_name("Manga Desktop Reader")
        self.set_version("verison 0.1b1")
        self.set_copyright("Copyright (c) 2019 August B. Sandoval")
        self.set_comments("NOTICE:\nAll Manga/Comics viewed within this program belong to their respective owner(s).")
        self.set_website_label("Source Code")
        self.set_website("https://gitlab.com/asandova/manga-desktop-reader")
        self.set_authors(["August B. Sandoval"])
        self.set_license_type(7)
        self.set_license("MIT License\n\nCopyright (c) 2019 August B. Sandoval\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
        self.set_wrap_license(True)
        self.run()
        self.destroy()

class add_Popup(gtk.Dialog):
    def __init__(self, parent,glade_file):
        self.url = ""
        self.parent = parent
        gtk.Dialog.__init__(self, "Enter Manga URL",parent,gtk.DialogFlags.MODAL,
        (gtk.STOCK_CANCEL,gtk.ResponseType.CANCEL,
         gtk.STOCK_OK, gtk.ResponseType.OK))

        self.set_default_size(200,100)
        self.set_border_width(30)
        area = self.get_content_area()
        entry = gtk.Entry()
        entry.set_placeholder_text("Manga URL")
        entry.set_icon_from_icon_name(0,"gtk-connect")
        entry.connect( "changed", self._on_entry_update)
        entry.connect( "paste_clipboard", self._on_entry_update)
        area.add(entry )
        self.show_all()

    def _on_entry_update(self,widget):
        #print(widget.get_text())
        self.parent.entered_url = widget.get_text()

class Error_Popup(gtk.MessageDialog):
    def __init__(self,parent,error_message_primary, error_message_secondary=None,*args,**kwargs):
        gtk.MessageDialog.__init__(self, parent, 0, gtk.MessageType.ERROR, gtk.ButtonsType.CANCEL, error_message_primary)
        if error_message_secondary != None:
            self.format_secondary_text(error_message_secondary)
        self.show_all()

class Warning_Popup(gtk.MessageDialog):
    def __init__(self,parent,warning_message_primary, warning_message_secondary=None,*args,**kwargs):
        gtk.MessageDialog.__init__(self, parent, 0, gtk.MessageType.WARNING, gtk.ButtonsType.CANCEL, warning_message_primary)
        if warning_message_secondary != None:
            self.format_secondary_text(warning_message_secondary)
        self.show_all()

class Info_Popup(gtk.MessageDialog):
    def __init__(self,parent,info_message_primary, info_message_secondary=None,*args,**kwargs):
        gtk.MessageDialog.__init__(self, parent, 0, gtk.MessageType.INFO, gtk.ButtonsType.CANCEL, info_message_primary)
        if info_message_secondary != None:
            self.format_secondary_text(info_message_secondary)
        self.show_all()