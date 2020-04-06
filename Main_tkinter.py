#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Main_tkinter.py                                               #
#description     :The Main driver script for tkinter interface for this project.#
#author          :August B. Sandoval (asandova)                                 #
#date            :22020-3-18                                                     #
#version         :0.3                                                           #
#usage           :Main python script for Manga Desktop Reader using TKinter     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

from tk.MainWindow import MainWindow

import json, os, platform
from src.TitleSource import TitleSource
from src.Chapter import Chapter

def main():
    #config = {}
    MainWindow._load_config()
    """
    if os.path.exists("config.json") == True:
        with open("config.json",'r') as f:
            config_string = f.read()
            MainWindow.appConfig = json.loads(config_string)
    else:
        MainWindow.appConfig["Hide Cache Files"] = True
        MainWindow.appConfig["Hide Download Directory"] = False
        MainWindow.appConfig["Cashe Save Location"] = "."
        MainWindow.appConfig["Default Download Location"] = "./Manga"
        MainWindow.appConfig["Webdriver Location"] = "./WebDrivers"
        MainWindow.appConfig["Browser Version"] = "2.45"
        MainWindow.appConfig["Browser"] = "Chrome"
        MainWindow.appConfig["Search Location(s)"] = []
    """

    if os.path.isdir(MainWindow.appConfig["Default Download Location"]) == False:
        os.makedirs( MainWindow.appConfig["Default Download Location"] )

    TitleSource.hide_cache_file = MainWindow.appConfig["Hide Cache Files"]

    Chapter.Driver_path = MainWindow.appConfig["Webdriver Location"] +'/'+MainWindow.appConfig["Browser"] +'/'+ MainWindow.appConfig["Browser Version"] + '/'
    Chapter.Driver_type = MainWindow.appConfig["Browser"]
    if Chapter.Driver_type == "Chrome":
        Chapter.Driver_path += "chromedriver"
    elif Chapter.Driver_type == "Firefox":
        Chapter.Driver_path += "geckodriver"
    #print(Chapter.Driver_path)
    if platform.system() == "Windows":
        Chapter.Driver_path += ".exe"
    elif platform.system() == "Linux":
        Chapter.Driver_path += "_Linux"
    TitleSource.set_default_save_location(MainWindow.appConfig["Default Download Location"])
    main = MainWindow( UI_Template=MainWindow.appConfig["UI"]["Main"], title="Manga Reader", theme=MainWindow.appConfig["tktheme"] )

    main.mainloop()


if __name__ == "__main__":
    main()