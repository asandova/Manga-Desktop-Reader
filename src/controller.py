#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :controller.py                                                 #
#description     :Defines a abstract parent class for Mainwindows for tkinter   #
#                :and GTK                                                       #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :defines a abstract parent class for functions and variables   #
#                :used for both Main Windows tkinter and GTK                    #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#

import json, os, sys, platform
from queue import Queue
from collections import deque
try:
    from src.MangaPark import MangaPark_Source
except:
    from .MangaPark import MangaPark_Source
    
class control():

    appConfig = {}

    def __init__(self):
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
        self.Title_Dict = {}
        self.Streams = []
        self.search_locations = set()
        self.Widgets = {}
        self.Chapter_List = []
        self._KillThreads = [False]
        self._sort = False
        self.ChapterQueue = deque()
        self.TitleQueue = deque()

    @staticmethod
    def get_config():
        return control.appConfig

    @staticmethod
    def set_config(key, value):
        control.appConfig[key] = value

    @staticmethod
    def set_config_dict(json_dict):
        control.appConfig =  json_dict

    def in_chapter_queue(self, hash_id):
        #if self._current_task["Chapter"] != None:
        #    title = self._current_task["Chapter"][0]
        #    stream = self._current_task["Chapter"][1]
        #    chapter = self._current_task["Chapter"][2]
        #    current_id = hash( ( title, stream, chapter) )
        #    if hash_id == current_id:
        #        return True

        for i in self.ChapterQueue:
            if i[4] == hash_id:
                return True
        return False

    def add_title_entry(self,name):
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

    def _load_title_entry(self):
        pass

    def _update_title_details(self):
        pass

    # Signal callback methods ---------------------------------------------------------------#

    def about(self):
        pass

    def _on_menu_add(self):
        pass

    def _on_quit(self):
        pass

    def _on_list_select(self, data=None):
        pass

    def _on_remove(self):
        pass

    def _on_search_change(self, event=None):
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
    def read_title_cache(json_file):
        manga_string = ""
        with open(json_file, 'r') as f:
            manga_string = f.read()
            f.close()
        Title_Dict = json.loads(manga_string)
        if Title_Dict["Site Domain"] == "https://mangapark.net":
            manga = MangaPark_Source()
            manga.from_dict(Title_Dict)
            return manga
        else:
            return None

    # Thread worker methods -----------------------------------------------------------------#

    def _add_title_from_url_runner( self ):
        pass

    def _download_chapter_runner(self):
        pass
    
    def _update_stream_runner( self, manga_object ):
        pass

