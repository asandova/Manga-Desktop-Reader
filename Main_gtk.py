#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Main_gtk.py                                                   #
#description     :contains the driver script                                    #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :the driver script using gtk3 GUI library                      #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk
from src.TitleSource import TitleSource

from gtk3.MainWindow import MainWindow
from src.Chapter import Chapter

import os, platform, json

if __name__ == '__main__':
    if os.path.exists("config.json") == True:
        with open("config.json",'r') as f:
            config_string = f.read()
            MainWindow.set_config_dict(json.loads(config_string)) 
    else:
        MainWindow.set_config("Hide Cache Files", True)
        MainWindow.set_config("Hide Download Directory",False)
        MainWindow.set_config("Cashe Save Location",".")
        MainWindow.set_config("Default Download Location","./Manga")
        MainWindow.set_config("Webdriver Location","./WebDrivers")
        MainWindow.set_config("Browser Version","2.45")
        MainWindow.set_config("Browser","Chrome")
        MainWindow.set_config("Search Location(s)", [])
        
    appConfig = MainWindow.get_config()

    if os.path.isdir(appConfig["Default Download Location"]) == False:
        os.makedirs( appConfig["Default Download Location"] )

    Chapter.Driver_path = appConfig["Webdriver Location"] +'/'+appConfig["Browser"] +'/'+ appConfig["Browser Version"] +'/'
    Chapter.Driver_type = appConfig["Browser"]
    if Chapter.Driver_type == "Chrome":
        Chapter.Driver_path += "chromedriver"
    elif Chapter.Driver_type == "Firefox":
        Chapter.Driver_path += "geckodriver"

    if platform.system() == "Windows":
        Chapter.Driver_path += ".exe"
    elif platform.system() == "Linux":
        Chapter.Driver_path += "_Linux"
    #elif platform.system() == "MacOS":
    #    Chapter.Driver_path += "_mac"
    TitleSource.set_default_save_location(appConfig["Default Download Location"])
    main = MainWindow(appConfig["UI"]["Main"], "Manga_Reader_Viewer_window.glade", "Manga_Reader_add_manga_dialog.glade")
    #main = Main(config["UI"]["Main"], "Manga_Reader_Viewer_window.glade", "Manga_Reader_add_manga_dialog.glade")
    gtk.main()
