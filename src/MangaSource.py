#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .MangaStream import Manga_Stream

import json, platform, requests
from bs4 import BeautifulSoup

platform_type = platform.system()

class Manga_Source:

    hide_cache_file = False

    default_save_location = '.'

    def __init__(self):    
        self.site_url = ""
        self.site_domain = ""
        self.manga_extention = ""
        self.save_location = Manga_Source.default_save_location
        self.Title = ""
        self.directory = self.Title.replace(' ', '_')
        if self.directory != "":
            self.save_location += '/' + self.directory
        self.authors = []
        self.artists = []
        self.genres = []
        self.streams = []
        self.summary = ""
        self.html_source = ""
        self.cover_location = ""
        self.keep = {}

    @staticmethod
    def find_site_domain(url):
        domain = ""
        url_elements = url.split("/")
        #print(url_elements)
        if len(url_elements) < 3:
            return None
        domain = url_elements[2]
        return domain

    def request_manga(self, url):
        self.site_url = url
        r = requests.get(url)
        if r.ok != True:
            return r.status_code
        else:
            #print("Extracting Manga from " + url)
            self.site_html = BeautifulSoup( r.text, 'lxml' )
            self.site_url = url
            #print("Extraction complete")
            return 0
    
    def extract_manga(self):
            self._extract_domain(self.site_url)
            self._extract_title()
            self._extract_cover()
            self._extract_managa_info()
            self._extract_summary()
            self._extract_streams()

    def _extract_domain(self, url):
        url_elements = url.split('/')
        #print(url_elements)
        self.site_domain = "https://" + url_elements[2]
        #print(self.site_domain)
        self.manga_extention = "/" + url_elements[3] +'/'+url_elements[4]
        #print(self.manga_extention)

    def update(self):
        pass

    def update_streams(self):
        r = requests.get(self.site_url)
        if r.ok != True:
            return r.status_code
        else:
            self.site_html = BeautifulSoup( r.text, 'lxml' )
            self.streams = []
            self._extract_streams()
            return 0

    def _extract_title(self):
        pass
    def _extract_cover(self):
        pass
    def _extract_managa_info(self):
        pass
    def _extract_summary(self):
        pass
    def _extract_streams(self):
        pass

    def get_directory(self):
        return self.directory

    def get_title(self, group=0):
        if group > 0:
            s = self.Title.split(" ")
            temp = s[0]
            for i in range(1, len(s)):
                if i % group == 0 and i != 0:
                    temp += "\n" + s[i]
                else:
                    temp += " " + s[i]
            return temp
        else:
            return self.Title
    
    def get_summary(self):
        return self.summary

    def has_Author(self, author):
        for a in self.authors:
            if a == author:
                return True
        return False
    def get_Authors(self):
        return self.authors
    def get_Authors_str(self, group=0):
        authors_str = ""
        num_of_authors = len(self.authors)
        
        for i in range (0 ,num_of_authors):
            if i % group == 0 and i > 0 and i != num_of_authors:
                authors_str += '\n\t'
            authors_str += self.genres[i]
            if i+1 != num_of_authors:
                authors_str += ', '
        return authors_str

    def has_Artist(self, artist):
        for a in self.artists:
            if a == artist:
                return True
        return False
    def get_Artists(self):
        return self.artists
    def get_Artists_str(self, group=0):
        artists_str = ""
        num_of_artists = len(self.artists)

        for i in range (0 ,num_of_artists):
            if i % group == 0 and i > 0 and i != num_of_artists:
                artists_str += '\n\t'
            artists_str += self.genres[i]
            if i+1 != num_of_artists:
                artists_str += ', '

        return artists_str

    def has_Genre(self, genre):
        for g in self.genres:
            if g == genre:
                return True
        return False

    def get_Genres(self):
        return self.genres

    def get_Genres_str(self, group=0):
        Genres_str = ""
        num_of_genres = len(self.genres)
        for i in range (0 , num_of_genres):
            if i % group == 0 and i > 0 and i != num_of_genres:
                Genres_str += '\n\t'
            Genres_str += self.genres[i]
            if i+1 != num_of_genres:
                Genres_str += ', '
 
        return Genres_str

    def get_cover_location(self):
        return self.cover_location

    def get_streams(self):
        return self.streams

    def get_stream_with_name(self,name):
        for s in self.streams:
            if s.name == name:
                return s
        return None
        
    def get_stream_with_id(self,id):
        for s in self.streams:
            if s.id == id:
                return s
        return None

    def get_stream_with_id_and_name(self,id,name):
        for s in self.streams:
            if s.id == id and s.name == name:
                return s
        return None

    def add_stream(self, stream):
        if isinstance(stream, Manga_Stream):
            print("adding stream " + stream.name)
            self.streams.append(stream)
        else:
            raise Exception("Attemting to add a non Manga_Stream object")

    def download_stream(self, stream_name):
        pass

    def is_keeped(self,stream_id, chapter):
        stream = self.get_stream_with_id(stream_id)
        if self.keep.get(stream.name) == None:
            return False
        else:
            if self.keep[stream.name].count() == 0:
                return False
            else:
                return True

    def remove_from_keep(self,stream_id=None,chapter=None):
        if stream_id == None and chapter == None:
            self.keep = {}
            return
        
        stream = self.get_stream_with_id(stream_id)
        if chapter != None:
            if self.keep.get(stream.name) != None:
                for c in self.keep[stream.name]:
                    if c == chapter.get_chapter_number():
                        self.keep[stream.name].remove(c)
        else:
            if self.keep.get(stream.name) != None:
                self.keep[stream.name] = []


    def add_to_keep(self,stream_id,chapter=None):
        stream = self.get_stream_with_id(stream_id)
        if self.keep.get(stream.name) == None:
            self.keep[stream.name] = []

        if chapter == None:
            chapters = stream.get_chapters()
            for c in chapters:
                chap_num = c.get_chapter_number()
                if self.keep[stream.name].count(chap_num) == 0:
                    self.keep[stream.name].append(chap_num)
        else:
            if self.keep[stream.name].count(chapter.get_chapter_number()) == 0:
                self.keep[stream.name].append(chapter.get_chapter_number())

    @staticmethod
    def set_default_save_location( location):
        Manga_Source.default_save_location = location

    def to_dict(self):
        dic = {}
        dic["Site URL"] = self.site_url
        dic["Site Domain"] = self.site_domain
        dic["Manga Extention"] = self.manga_extention
        dic["Title"] = self.Title
        dic["Manga Stream(s)"] = []
        for s in self.streams:
            dic["Manga Stream(s)"].append( s.to_dict() )
        dic["Summary"] = self.summary
        dic["Cover Location"] = self.cover_location
        dic["Keep"] = self.keep
        return dic

    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        self.Title = dictionary["Title"]
        self.directory = self.Title.replace(' ', '_')
        self.summary = dictionary["Summary"]
        self.cover_location = dictionary["Cover Location"]
        self.keep = dictionary["Keep"]
        for s in dictionary["Manga Stream(s)"]:
            stream = Manga_Stream()
            stream.from_dict( s )
            self.streams.append( stream )

    def to_json_file(self, save_location):
        print(save_location)
        print(self.directory)
        manga_dict = self.to_dict()
        filename = self.directory
        if Manga_Source.hide_cache_file == True:
            if platform_type == "Windows":
                filename = "$"+self.Title
            else:
                filename = "."+self.Title
        with open(save_location +"/" + self.directory +'/' +filename+ ".json", 'w') as f:
            f.write(json.dumps( manga_dict, indent=1 ))
            f.close()
        print(save_location +"/" + self.directory +'/' +filename + ".json : has been written to")

    def from_json(self, json_string):
        manga_dict = json.loads(json_string)
        self.from_dict( manga_dict )
