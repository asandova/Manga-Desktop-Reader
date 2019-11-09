#!/usr/bin/python3
# -*- coding: utf-8 -*-
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

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