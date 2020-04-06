#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :controller.py                                                 #
#description     :Defines a abstract parent class for Mainwindows for tkinter   #
#                :and GTK                                                       #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :defines a abstract parent class for functions and variables   #
#                :used for both Main Windows tkinter and GTK                    #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
import json, os, sys, platform
from queue import Queue
from collections import deque
try:
    #from src.MangaPark import MangaPark_Source
    from src.pluginManager import Manager
    from src.TitleSource import TitleSource
except:
    #from .MangaPark import MangaPark_Source
    from .pluginManager import Manager
    from .TitleSource import TitleSource


class control():

    appConfig = {}
    instance = None

    def __init__(self):
        if control.instance != None:
            raise Exception("Only one control object can be instanciated")
        else:    
            control.instance = self
            self.selection = {
                "Title" : None,
                "Stream" : None,
                "Chapter" : None
            }
            self.threads = {
                "Title" : None,
                "Stream" : None,
                "Chapter" : None
            }
            self._current_task = {
                "Title" : None,
                "Chapter" : None
            }
            self.page_location = {
                "current" : 0,
                "end" : 0
            }
            self.chapter_per_page = 50
            self.Title_Dict = {}
            self.Streams = []
            self.search_locations = set()
            self.Widgets = {}
            self.Chapter_List = []
            self._KillThreads = [False]
            self._sort = False
            self.ChapterQueue = deque()
            self.TitleQueue = deque()
            self.PluginManager = Manager(TitleSource)
            self.PluginManager.discover_sources()

    def in_chapter_queue(self, hash_id):
        for i in self.ChapterQueue:
            if i[4] == hash_id:
                return True
        return False

    def add_title_entry(self, name):
        pass

    def update_status(self, message):
        pass

    def _get_title_list_from_file(self, json_file="tracking_list.json"):

        if control.appConfig["Hide Cache Files"] == True:
            if platform.system() == "Linux":
                json_file = "." + json_file

        if os.path.exists(control.appConfig["Cashe Save Location"] +'/'+json_file) == True:
            cache_string = ""
            with open(control.appConfig["Cashe Save Location"] +'/'+ json_file, 'r') as f:
                cache_string = f.read()
                f.close()
            dic = json.loads(cache_string)
            if(len(dic) != 0):
                for l in dic["Title List"].keys():
                    self.search_locations.add(l)
                    for m in dic["Title List"][l]:
                        _m = m.replace(" ", "_")
                        cache_path = _m + "/" + _m + ".json"
                        if self.check_title_cache_exists(l,cache_path) == True:
                            title_object = self.read_title_cache(l + '/' + cache_path)
                            if title_object != None:
                                self.Title_Dict[m] = title_object

        print("Searching for untracked Manga")
        for search in control.appConfig["Search Location(s)"]:
            dirs = os.listdir(search)
            for d in dirs:
                path = search + '/'+ d + "/" + d + '.json'
                _d = d.replace('_', ' ')
                if os.path.isfile(path) == True and self.Title_Dict.get(_d) == None:
                    title_object = self.read_title_cache( path )
                    if title_object != None:
                        if self.Title_Dict.get(title_object.get_title()) == None:
                            self.search_locations.add(search)
                            print("Discovered: " + title_object.get_title() + " in " + search)
                            self.Title_Dict[title_object.get_title()] = title_object

    def _export_title_list_to_file(self, export_file="tracking_list.json"):
        if self.appConfig['Hide Cache Files']== True:
            if platform.system()  == "Linux":
                export_file = "." + export_file

        dic = { "Number of titles": len(self.Title_Dict), "Search Location(s)" : [], "Title List" : {} }
        for l in self.search_locations:
            dic["Search Location(s)"].append(l)

        for m in self.Title_Dict.keys():
            location = self.Title_Dict[m].save_location
            if dic["Title List"].get(location) == None:
                dic["Title List"][location] = []
            dic["Title List"][location].append(m)

        with open(self.appConfig["Cashe Save Location"] +'/'+ export_file, 'w') as f:
            f.write(json.dumps(dic, separators=(",", " : "), indent=4))
            f.close()

    @staticmethod
    def _load_config( config_file="config.json"):
        if os.path.exists( config_file) == True:
            with open(config_file, "r") as f:
                config_string = f.read()
                control.appConfig = json.loads(config_string)
        else:
            control.appConfig["Hide Cache Files"] = True
            control.appConfig["Hide Download Directory"] = False
            control.appConfig["Cashe Save Location"] = "."
            control.appConfig["Default Download Location"] = "./Manga"
            control.appConfig["tktheme"] = "clam"
            control.appConfig["Webdriver Location"] = "./WebDrivers"
            control.appConfig["Browser Version"] = "2.45"
            control.appConfig["Browser"] = "Chrome"
            control.appConfig["Search Location(s)"] = []

    @staticmethod
    def _export_config( config_file="config.json"):
        with open(config_file, "w") as f:
            f.write( json.dumps( control.appConfig, separators=(",", " : "), indent=4 ) )

    def _load_title_entry(self):
        pass

    def _update_location_bounds(self):
        self.page_location["current"] = 0
        self.page_location["end"] = int( len( self.selection["Stream"] ) / self.chapter_per_page )
        
        if len( self.selection["Stream"] ) % self.chapter_per_page != 0:
            self.page_location["end"] += 1 

    def _update_title_details(self):
        pass

    # Signal callback methods ---------------------------------------------------------------#
    
    def about(self, widget):
        pass

    def _on_beginning(self):
        self.page_location["current"] = 0
        self._update_location_controls()
        self._update_chapter_list(length=self.chapter_per_page ,offset=self.page_location["current"])

    def _on_end(self):
        self.page_location["current"] = self.page_location["end"]-1
        self._update_location_controls()
        self._update_chapter_list(length=self.chapter_per_page ,offset=self.page_location["current"])

    def _on_menu_add(self, widget):
        pass

    def _on_next(self):
        if self.page_location["current"] < self.page_location["end"]-1:
            self.page_location["current"] += 1
            self._update_location_controls()
            self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"] )

    def _on_list_select(self, data=None):
        pass

    def _on_location_change(self, event=None):
        pass

    def _on_prev(self):
        if self.page_location["current"] > 0:
            self.page_location["current"] -= 1
            self._update_location_controls()
            self._update_chapter_list(length=self.chapter_per_page, offset=self.page_location["current"] )

    def _on_quit(self):
        pass

    def _on_remove(self):
        pass

    def _on_search_change(self, widget):
        pass

    def _on_sort(self):
        self._sort = not self._sort
        self._update_chapter_list()

    def _on_stream_change(self, event):
        pass

    def _on_update(self):
        pass

    def _update_chapter_list(self):
        pass 
 
    def _update_stream_dropdown(self):
        pass

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def check_title_cache_exists( search_location, title_name ):
        if os.path.isfile(search_location+'/'+ title_name):
            return True
        else:
            return False

    @staticmethod
    def get_config():
        return control.appConfig
        
    @staticmethod
    def read_title_cache(json_file):
        title_string = ""
        with open(json_file, 'r') as f:
            title_string = f.read()
            f.close()
        Title_Dict = json.loads(title_string)
        if  control.instance.PluginManager.is_source_supported( Title_Dict["Site Domain"] ):
            title = control.instance.PluginManager.create_instance( Title_Dict["Site Domain"] )
            title.from_dict(Title_Dict)
            return title
        else:
            return None

    @staticmethod
    def set_config(key, value):
        control.appConfig[key] = value

    @staticmethod
    def set_config_dict(json_dict):
        control.appConfig =  json_dict

    # Thread worker methods -----------------------------------------------------------------#

    def _add_title_from_url_runner( self ):
        pass

    def _download_chapter_runner(self):
        pass
    
    def _update_stream_runner( self, title ):
        pass

