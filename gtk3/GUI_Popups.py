#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :ChapterListRow.py                                             #
#description     :creates a custom gtk popups                                   #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :Defines a custom gtk popups                                   #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk

import os, platform

class About_Popup(gtk.AboutDialog):
    def __init__(self, *args, **kwargs):
        gtk.AboutDialog.__init__(self,*args, **kwargs)
        self.set_program_name("Manga Desktop Reader")
        self.set_version("verison 0.4b")
        self.set_copyright("Copyright (c) 2019 August B. Sandoval")
        self.set_comments("NOTICE:\nAll Manga/Comics viewed within this program belong to their respective owner(s).")
        self.set_website_label("Source Code")
        self.set_website("https://gitlab.com/asandova/manga-desktop-reader")
        self.set_authors(["August B. Sandoval"])
        self.set_license_type(7)
        self.set_license("MIT License\n\nCopyright (c) 2020 August B. Sandoval\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
        self.set_wrap_license(True)
        self.run()
        self.destroy()

class add_Popup(gtk.Dialog):
    def __init__(self, parent,glade_file):
        self.url = ""
        self.parent = parent
        gtk.Dialog.__init__(self, "Enter Title URL",parent,gtk.DialogFlags.MODAL,
        (gtk.STOCK_CANCEL,gtk.ResponseType.CANCEL,
         gtk.STOCK_OK, gtk.ResponseType.OK))

        self.set_default_size(200,100)
        self.set_border_width(30)
        area = self.get_content_area()
        label = gtk.Label("Enter URL of the title page for the comic.\nSeparate mulitple URLs with comma (\",\")")
        entry = gtk.Entry()
        entry.set_placeholder_text("Title URL")
        entry.set_icon_from_icon_name(0,"gtk-connect")
        entry.connect( "changed", self._on_entry_update)
        entry.connect( "paste_clipboard", self._on_entry_update)
        area.add(label)
        area.add(entry )
        self.show_all()

    def _on_entry_update(self,widget):
        #print(widget.get_text())
        self.parent.entered_url = widget.get_text()

class Preference_Window(gtk.Window):
    
    def __init__(self, parent, template="" ,*args, **kwargs):
        gtk.Window.__init__(self, *args, **kwargs)
        self.parent = parent
        self.Widgets = {}
        self.signals = {}
        self.drivers = []
        self.plugins = []
        self.search_locations = []
        self.__selected_location = None

        if template != "":
            self._build_from_template(template)
        self.Widgets["DL Entry"].set_text(  self.parent.appConfig["Default Download Location"]  )
        self.Widgets["Driver Entry"].set_text( self.parent.appConfig["Webdriver Location"] )

    def _build_from_template(self, template):
        self.builder = gtk.Builder()
        self.builder.add_from_file(template+".glade")
        self.Widgets["Pref Window"] = self.builder.get_object("Pref_Window")
        self.Widgets["Close"] = self.builder.get_object("CloseButton")
        self.Widgets["Status Label"] = self.builder.get_object("Status_Label")
        self.Widgets["Status Label"].set_text("")
        self.Widgets["DL Entry"] = self.builder.get_object("DL_Entry")
        self.Widgets["SL Entry"] = self.builder.get_object("SL_Entry")
        self.Widgets["DL Browse"] = self.builder.get_object("DL_Browse")
        self.Widgets["SL Browse"] = self.builder.get_object("SL_Browse")
        self.Widgets["SL Add"] = self.builder.get_object("SL_Add_Button")
        self.Widgets["SL Remove"] = self.builder.get_object("SL_Remove_Button")
        self.Widgets["Search List"] = self.builder.get_object("Search_List")
       
        for l in self.parent.appConfig["Search Location(s)"]:
            self.add_search_location(location=l)
        
        self.Widgets["Plugin List"] = self.builder.get_object("Plugin_List")
        self.Widgets["Driver List"] = self.builder.get_object("Driver_List")
        self.Widgets["Driver Entry"] = self.builder.get_object("DriverEntry")
        self.Widgets["Driver Select"] = self.builder.get_object("Driver_Select_Button")
        self.Widgets["Driver Browse"] = self.builder.get_object("Driver_Browse")
        
        self.signals["SL Browse"] = self.Widgets["SL Browse"].connect("file-set", self._on_SL_browse)
        self.signals["Driver Browse"] = self.Widgets["Driver Browse"].connect("file-set", self._on_driver_browse)
        self.signals["Driver Select"] = self.Widgets["Driver Select"].connect("clicked", self._on_drivers_loc_set)
        self.signals["Search List"] = self.Widgets["Search List"].connect("row-selected", self._on_search_select)
        self.signals["SL Add"] = self.Widgets["SL Add"].connect("clicked", self._on_add_search)
        self.signals["SL Remove"] = self.Widgets["SL Remove"].connect("clicked", self._on_remove_search)
        self.signals["DL Browse"] = self.Widgets["DL Browse"].connect("file-set", self._on_DL_browse)
        self.signals["Pref Window"] = self.Widgets["Pref Window"].connect("delete-event", self._on_close)
        self.signals["Close"] = self.Widgets["Close"].connect("clicked", self._on_close)
        self.Widgets["Pref Window"].show()

        self.update_plugin_list()
        self.update_driver_list()

    def add_search_location(self, location=""):
        row = Preference_Window.LocationRowBox(location)
        self.search_locations.append(row)
        self.Widgets["Search List"].add(row)

    def remove_search_location(self, widget):
        if self.__selected_location != None:
            self.Widgets["Search List"].remove(self.__selected_location)
            self.search_locations.remove(self.__selected_location)
            self.__selected_location = None

    def update_driver_list(self):
        driver_location = self.parent.appConfig["Webdriver Location"]
        if len( self.drivers ) != 0:
            for d in self.drivers:
                self.Widgets["Driver List"].remove(d)
            self.drivers = []
        drivers = {}
        if os.path.exists(driver_location) == False:
            return
        browsers = os.listdir(driver_location)
        
        for b in browsers:
            if b.lower() == "chrome":
                drivers["Chrome"] = self.find_drivers(b, driver_location, "chromedriver")
            elif b.lower() == "firefox":
                drivers["Firefox"] = self.find_drivers(b, driver_location, "geckodriver")                

        for d in drivers.keys():
            selected = ""
            if d == self.parent.appConfig["Browser"]:
                selected = self.parent.appConfig["Browser Version"]
            driver = Preference_Window.DriverFrame(browser_name=d, version_list=drivers[d], selected_version=selected, command=self._on_driver_select )
            self.Widgets["Driver List"].add(driver)
            if d == self.parent.appConfig["Browser"]:
                driver.set_active(False)
            self.drivers.append(driver)

    def update_plugin_list(self):
        plugin_list = self.parent.PluginManager.get_plugin_list()
        for p in plugin_list:
            discription = self.parent.PluginManager.get_plugin_by_name( p ).TitlePlugin.description
            plugin = self.PluginFrame(name=p, discription=discription, command=self._on_reload)
            self.plugins.append(plugin)
            self.Widgets["Plugin List"].add(plugin)

    def find_drivers(self, browser, path, drivername):
        version_list = []
        browser_path = os.path.join(path, browser)
        versions = os.listdir(browser_path)
        for v in versions:
            version_path = os.path.join(browser_path, v)
            suffix = ""
            p = platform.system()
            if p == "Windows":
                suffix = ".exe"
            elif p == "Linux":
                suffix = "_Linux"
            else:
                continue 
            if os.path.isfile( version_path + "/" + drivername + suffix ) == True:
                version_list.append(v)
        return version_list

    def _on_add_search(self, widget):
        if self.Widgets["SL Entry"].get_text() != "":
            for s in self.search_locations:
                if s.get_location() == self.Widgets["SL Entry"].get_text():
                    return
            self.add_search_location( location=self.Widgets["SL Entry"].get_text() )
            self.Widgets["SL Entry"].set_text("")

    def _on_drivers_loc_set(self, widget):
        if  self.Widgets["Driver Entry"].get_text() != "":
            self.parent.appConfig["Webdriver Location"] = self.Widgets["Driver Entry"].get_text()
            self.update_driver_list()

    def _on_remove_search(self, widget):
        if self.__selected_location != None:
            self.search_locations.remove(self.__selected_location)
            self.Widgets["Search List"].remove(self.__selected_location)
            self.__selected_location = None
            
    def _on_close(self, widget=None, data=None):
        self.parent.appConfig["Search Location(s)"] = []
        for l in self.search_locations:
            self.parent.appConfig["Search Location(s)"].append(l.get_location())
        self.Widgets["Pref Window"].destroy()
        self.destroy()

    def _on_driver_browse(self, widget):
        self.Widgets["Driver Entry"].set_text(widget.get_filename())
        self.parent.appConfig["Webdriver Location"] = widget.get_filename()
        self.update_driver_list()

    def _on_driver_select(self, data):
        for d in self.drivers:
            if d.browser_name == data:
                if d.selected_version != "":
                    d.set_active(False)
                    self.parent.appConfig["Browser"] = data
                    self.parent.appConfig["Browser Version"] = d.selected_version
                else:
                    return
            else:
                d.set_active(True) 

    def _on_DL_browse(self, widget):
        self.Widgets["DL Entry"].set_text = widget.get_filename()
        self.parent.appConfig["Default Download Location"] = widget.get_filename()
        self.update_driver_list()

    def _on_reload(self, name):
        print(name)
        if self.parent.PluginManager.reload_plugin(name) != 0:
            self.Widgets["Status Label"].set_text("Failed to reload plugin \"" + name + "\"")
        else:
            self.Widgets["Status Label"].set_text("Reloaded plugin \"" + name + "\" successfully")
    
    def _on_search_select(self, widget, data):
        self.__selected_location = data

    def _on_SL_browse(self, widget):
        print(widget.get_filename())
        self.Widgets["SL Entry"].set_text(widget.get_filename())

    class PluginFrame(gtk.Frame):
        def __init__(self, name="", discription="", command=None):
            gtk.Frame.__init__(self)
            self.Widgets = {}
            self.name = name
            self.discritpion = discription
            self.command = command
            self.set_label(name)
            self._build()
            self.Widgets["Reload Button"].connect("clicked", self._on_command)
            self.show_all()

        def _build(self):
            self.Widgets["Container"] = gtk.Box()
            self.Widgets["Plugin Discription"] = gtk.Label()
            self.Widgets["Plugin Discription"].set_text(self.discritpion)
            self.Widgets["Plugin Discription"].set_justify(gtk.Justification.LEFT)
            self.Widgets["Reload Button"] = gtk.Button.new_with_label("Reload")
            self.Widgets["Container"].pack_start(self.Widgets["Plugin Discription"], True, False, 0)
            self.Widgets["Container"].pack_start(self.Widgets["Reload Button"], False, False, 0)
            
            self.add( self.Widgets["Container"] )

        def _on_command(self, widget):
            if self.command != None:
                self.command(self.name)

    class DriverFrame(gtk.Frame):
        
        def __init__(self,browser_name="", version_list=[], selected_version="", command=None):
            gtk.Frame.__init__(self)
            self.Widgets = {}
            self.browser_name = browser_name
            self.version_list = version_list
            self.selected_version = selected_version
            self.command = command
            self._build()
            self.Widgets["Select Button"].connect("clicked", self._on_command)
            self.show_all()

        def _build(self):
            self.Widgets["Container"] = gtk.Box()
            self.add(self.Widgets["Container"])
            self.Widgets["Driver Label"] = gtk.Label()
            self.Widgets["Driver Label"].set_text(self.browser_name)
            self.Widgets["Driver Version Select"] = gtk.ComboBoxText.new_with_entry()
            self.Widgets["Driver Version Select"].get_child().set_text( self.selected_version)
            self.Widgets["Driver Version Select"].get_child().set_editable(False)
            self.Widgets["Driver Version Select"].connect("changed", self._on_version_select)
            for v in self.version_list:
                self.Widgets["Driver Version Select"].append_text(v)

            self.Widgets["Select Button"] = gtk.Button.new_with_label("Select")
            self.Widgets["Container"].pack_start(self.Widgets["Driver Label"], True, False, 0)
            self.Widgets["Container"].pack_start(self.Widgets["Driver Version Select"], False, False, 0)
            self.Widgets["Container"].pack_start(self.Widgets["Select Button"], False, False, 0)

        def set_active(self, state=False):
            if state == True:
                self.Widgets["Select Button"].set_sensitive(True)
            else:
                self.Widgets["Select Button"].set_sensitive(False)

        def _on_command(self, widget):
            if self.command != None:
                self.command(self.browser_name)

        def _on_version_select(self, widget):
            print(widget.get_active_text())
            self.selected_version = widget.get_active_text()

    class LocationRowBox(gtk.ListBoxRow):

        def __init__(self, location):
            gtk.ListBoxRow.__init__(self)
            self.label = gtk.Label()
            self.label.set_text(location)
            self.location = location
            self.add(self.label)
            self.label.show()
            self.show()

        def get_location(self):
            return self.location

        def __str__(self):
            return "Location Row: " + self.location


class ask_Popup(gtk.Dialog):
    def __init__(self, parent, title, message):
        self.parent = parent
        gtk.Dialog.__init__(self, title,parent,gtk.DialogFlags.MODAL,
        (gtk.STOCK_CANCEL,gtk.ResponseType.CANCEL,
         gtk.STOCK_OK, gtk.ResponseType.OK))

        self.set_default_size(150, 100)
        label = gtk.Label( message )
        box = self.get_content_area()
        box.add(label)
        self.show_all()

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