#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Source.py                                                     #
#description     :contains the source class                                     #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :defineds the source class                                     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
try:
    from .Stream import Stream
except:
    from src.Stream import Stream
from src.pluginManager import Manager
from abc import ABC, abstractmethod
import json, platform, requests, logging, re, os
from datetime import datetime
from bs4 import BeautifulSoup

platform_type = platform.system()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/TitleSource.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)

file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class TitleSource(ABC):

    hide_cache_file = False

    default_save_location = '.'
    replace_illegal_character_pattern = re.compile( "[/<>:\"\\\?\*\|]" )
    replace_space = re.compile(" ")


    def __init__(self):
        """TitleSource Constructor.
        """
        self.site_url = ""
        self.site_domain = ""
        self.site_name = ""
        self.manga_extention = ""
        self.save_location = TitleSource.default_save_location
        self.Title = ""
        self.download_time = ""
        self.directory = re.sub(TitleSource.replace_illegal_character_pattern, "-", self.Title)
        self.directory = re.sub(TitleSource.replace_space, "_", self.directory)
        #self.directory = self.Title.replace(' ', '_')
        if self.directory != "":
            self.save_location += '/' + self.directory
        self.authors = []
        self.artists = []
        self.genres = []
        self.streams = []
        self.summary = ""
        self.html_source = ""
        self.cover_location = ""

    def request_manga(self, url):
        """This method is responsable for getting the raw html from url
        
        Arguments:
            url {string} -- URL to the title page of the title being requested
        
        Returns:
            int -- return 0 upon successful otherwise returns a HTML status code
        """
        self.site_url = url
        r = requests.get(url)
        if r.ok != True:
            return r.status_code
        else:
            #print("Extracting Manga from " + url)
            self.download_time = datetime.now().strftime("%I:%M%p\n%b %d, %Y")
            self.site_html = BeautifulSoup( r.text, 'lxml' )
            self.site_url = url
            #print("Extraction complete")
            return 0
    
    def extract_title(self):
            logger.info("Extracting Domain...")
            self._extract_domain(self.site_url)
            logger.info("Extracting Title...")
            self._extract_title()
            logger.info("extracting cover...")
            self._extract_cover()
            logger.info("Extracting title info...")
            self._extract_title_info()
            logger.info("Exracting summary...")
            self._extract_summary()
            logger.info("Extracting streams...")
            self._extract_streams()
    
    def _extract_domain(self, url):
        url_elements = url.split('/')
        self.site_domain = url_elements[2]
        self.manga_extention = "/" + url_elements[3] +'/'+url_elements[4]

    def update_streams(self):
        """This method is responsable for updating the title streams.
            This method is not to be overriden UNLESS the complete chapter list(s) are NOT
            on a single HTML page or chapter lists are not generated without a bowser
        
        Returns:
            int -- returns 0 on success else return HTML error code
        """
        try:
            r = requests.get(self.site_url)
            if r.ok != True:
                return r.status_code
            else:
                self.download_time = datetime.now().strftime("%I:%M%p\n%b %d, %Y")
                self.site_html = BeautifulSoup( r.text, 'lxml' )
                self.streams = []
                self.extract_title()
                #self._extract_streams()
                return 0
        except Exception:
            logger.exception("Failed to update")
            return -1

    def add_stream(self, stream):
        if isinstance(stream, Stream):
            print("adding stream " + stream.name)
            self.streams.append(stream)
        else:
            raise Exception("Attemting to add a non Stream object")

    def download_stream(self, stream_name):
        pass

    def download_title(self, location=""):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            for c in s.chapters:
                stream_name = s.name.replace(' ', '_')
                c.download_chapter( save_location +'/'+self.directory+'/'+ stream_name)

    def download_title_stream(self, stream_id, location=""):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            if s.id == stream_id:
                for c in s.chapters:
                    stream_name = self.streams[stream_id].name.replace(' ', '_')
                    c.download_chapter( save_location +'/'+self.directory+'/'+ stream_name)
                return

    def download_title_chapter(self, stream_id, chapter_number, location="", KillDownload=[False]):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            if s.id == stream_id:
                for k in s.chapters.keys():
                    if  s.chapters[k].get_chapter_number() == chapter_number:
                        stream = self.get_stream_with_id(stream_id)
                        stream_name = stream.name.replace(' ', '_')
                        code =  s.chapters[k].download_chapter(save_location +'/'+self.directory+'/'+ stream_name,KillDownload)
                        return code
                return -1
        return -2

    # Abstract Methods ----------------------------------------------------------------------#

    @abstractmethod
    def _extract_cover(self):
        """This method is responsable for extracting the title's cover.
        This is a url to a image that will be downloaded.
        """
        pass

    @abstractmethod
    def _extract_title(self):
        """This method is responsable for extracting the title's title.
        This must be a python string.
        """
        pass

    @abstractmethod
    def _extract_title_info(self):
        """This method is responsable for extracting the title info.
        This means it extracts the titles Author, Artist and Genre infomation.
        Author, Artist and Genre must be python lists
        """
        pass

    @abstractmethod
    def _extract_summary(self):
        """This method is responsable for extracting the title summary.
        The summary must be a python string
        """
        pass

    @abstractmethod
    def _extract_streams(self):
        """This method is respnsable for extracting the title streams.
        This means the chapter list or lists. Each chapter list must be a Stream object.
        """
        pass

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def extract_chapter_number(chapter_string):
        """This function will parse out a chapter number from a chapter string.
        a chapter string is a string containing a chapter number and or volume number.
        If no chapter number is found a -1 is returned.
        examples: "vol.4 ch.2" , "volume 4 chapter 2"
        
        Arguments:
            chapter_string {string} -- the chapter string containing the chapters number
        
        Returns:
            int or float -- returns the chapter number. if no chapter number can be found then returns -1
        """
        volume_chapter_pattern = re.compile("[vV]ol(ume)*[.]*[ ]*[0-9]+[ ]+[cC]h(apter)*[.]*[ ]*[0-9]+")
        chapter_pattern = re.compile("[cC]h(apter)*[.]*[ ]*[0-9]+")
        volume_pattern = re.compile("[vV]ol(ume)*[.]*[ ]*[0-9]+")
        if(re.match(volume_chapter_pattern, chapter_string) != None 
            or re.match(chapter_pattern, chapter_string) != None):
            num_str_elements = volume_pattern.split(chapter_string)
            number_start = -1
            number_end = -1
            #print(number_str_elements[-1])
            for num in range(0, len(num_str_elements[-1])):
                if number_start == -1 and num_str_elements[-1][num].isnumeric():
                    number_start = num
                elif number_start != -1 and num_str_elements[-1][num].isnumeric() == False:
                    if num_str_elements[-1][num+1].isnumeric() == True:
                        continue
                    else:
                        number_end = num
                    #print(number_end)
                    break

            if number_end != -1:
                return float(num_str_elements[-1][number_start:number_end])
            elif number_end == -1 and number_start == -1:
                return -1
            else:
                return float(num_str_elements[-1][number_start:])
        else:
            return -1

    @staticmethod
    def set_default_save_location( location):
        logger.debug("Setting default location to: " + location)
        TitleSource.default_save_location = location

    @staticmethod
    @abstractmethod
    def is_domain_supported(domain):
        pass

    @staticmethod
    def find_site_domain(url):
        domain = ""
        url_elements = url.split("/")
        if len(url_elements) < 3:
            return None
        domain = url_elements[2]
        return domain

    @staticmethod
    @abstractmethod
    def get_supported_domains():
        pass

    # Checkers -------------------------------------------------------------------------------#

    def has_Author(self, author):
        for a in self.authors:
            if a == author:
                return True
        return False
    
    def has_Artist(self, artist):
        for a in self.artists:
            if a == artist:
                return True
        return False

    def has_Genre(self, genre):
        for g in self.genres:
            if g == genre:
                return True
        return False

    # Setters -------------------------------------------------------------------------------#

    def set_site_name(self, name):
        if type(name) == str:
            self.site_name = name

    # Getters -------------------------------------------------------------------------------#

    def get_Artists(self):
        return self.artists
    def get_Artists_str(self, group=0):
        artists_str = ""
        num_of_artists = len(self.artists)

        for i in range (0 ,num_of_artists):
            if group > 0:
                if i % group == 0 and i > 0 and i != num_of_artists:
                    artists_str += '\n\t'
            artists_str += self.artists[i]
            if i+1 != num_of_artists:
                artists_str += ', '

        return artists_str

    def get_Authors(self):
        return self.authors

    def get_Authors_str(self, group=0):
        authors_str = ""
        num_of_authors = len(self.authors)
        
        for i in range (0 ,num_of_authors):
            if group > 0:
                if i % group == 0 and i > 0 and i != num_of_authors:
                    authors_str += '\n\t'
            authors_str += self.authors[i]
            if i+1 != num_of_authors:
                authors_str += ', '
        return authors_str

    def get_cover_location(self):
        return self.cover_location

    def get_directory(self):
        return self.directory

    def get_Genres(self):
        return self.genres

    def get_Genres_str(self, group=0):
        Genres_str = ""
        num_of_genres = len(self.genres)
        for i in range (0 , num_of_genres):
            if group > 0:
                if i % group == 0 and i > 0 and i != num_of_genres:
                    Genres_str += '\n\t'
            Genres_str += self.genres[i]
            if i+1 != num_of_genres:
                Genres_str += ', '
 
        return Genres_str
    
    def get_summary(self):
        return self.summary

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

    def get_site_name(self):
        return self.site_name

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

    # Import methods ------------------------------------------------------------------------#

    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        self.Title = dictionary["Title"]
        self.download_time = dictionary["Download Time"]
        self.directory = self.Title.replace(' ', '_')
        self.summary = dictionary["Summary"]
        self.cover_location = dictionary["Cover Location"]
        pm = Manager.instance
        for s in dictionary["Manga Stream(s)"]:
            stream = Stream()
            if pm.is_source_supported( dictionary["Site Domain"] ) == True:
                stream.from_dict( s, pm.get_chapter_plugin( dictionary["Site Domain"] ) ) 
            else:
                stream.from_dict( s )
            self.streams.append( stream )

    # Export methods ------------------------------------------------------------------------#

    def to_dict(self):
        dic = {}
        dic["Site URL"] = self.site_url
        dic["Site Domain"] = self.site_domain
        dic["Manga Extention"] = self.manga_extention
        dic["Download Time"] = self.download_time
        dic["Title"] = self.Title
        dic["Manga Stream(s)"] = []
        for s in self.streams:
            dic["Manga Stream(s)"].append( s.to_dict() )
        dic["Summary"] = self.summary
        dic["Cover Location"] = self.cover_location
        return dic

    def to_json_file(self, save_location):
        title_dict = self.to_dict()
        filename = self.directory
        if TitleSource.hide_cache_file == True:
            if platform_type == "Windows":
                filename = "$"+self.Title
            else:
                filename = "."+self.Title
                
        with open(save_location +"/" + self.directory +'/' +filename+ ".json", 'w') as f:
            f.write(json.dumps( title_dict, indent=1, separators=(","," : ") ))
            f.close()
        print(save_location +"/" + self.directory +'/' +filename + ".json : has been written to")

    def from_json(self, json_string):
        title_dict = json.loads(json_string)
        self.from_dict( title_dict )

    def __str__(self):
        s = "----------Manga Park----------\n"
        s += "Title: " + self.Title + "\n"
        s += "Author(s): "
        for a in self.authors:
            s += a + " | "
        s += "\nArtist(s): "
        for a in self.artists:
            s += a + ' | '
        s+= "\nGenre(s): "
        for g in self.genres:
            s += g + ' | '
        s += "\nSummary: "+ self.summary + "\n"
        for stream in self.streams:
            s += stream.get_name() + " -- Chapters: " + str(len(stream)) + "\n"
        return s
