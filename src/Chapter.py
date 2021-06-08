#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Chapter.py                                                    #
#description     :Contains a generic chapter object definition                  #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-18                                                     #
#version         :0.3                                                           #
#usage           :Mdefins the chapter class                                     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
from bs4 import BeautifulSoup

import requests,traceback, sys, os, shutil, logging
from PIL import Image
from zipfile import ZipFile
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/Chapter.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class Chapter:

    Driver_path = None
    Driver_type = None
    Driver_extentions = None
    Driver_allow_extentions = False

    def __init__(self, name, number):
        self.chapter_name = name
        self.number_of_Pages = 0
        if type(number) is float:
            num_str = str(number)
            #print(num_str)
            if num_str[-1] == '0':
                self.chapter_number = int(number)
            else:
                self.chapter_number = number
        elif type(number) is int:
            self.chapter_number = number
        else:
            raise Exception("Chapter number must be a integer or float")
        self.directory = "Chapter_" + str(self.chapter_number)
        self.chapter_link = ""

    def set_chapter_number(self, num):
        """Sets the chapter number
        
        Arguments:
            num {int} -- chapter's number
        """
        if type(num) == float or type(num) == int:
            self.chapter_number = num
    def get_chapter_number(self):
        """returns the chapters number
        
        Returns:
            int -- chapter's number
        """
        return self.chapter_number

    def set_link(self,link):
        """sets the chapter url link
        
        Arguments:
            link {string} -- chapter's url link
        """
        if type(link) == str:
            self.chapter_link = link
    def get_link(self):
        """returns the chapter's url link
        
        Returns:
            string -- chapter's url link
        """
        return self.chapter_link

    def get_full_title(self):
        """returns the chapter's full title (e.g. Chapter [number] - [title])
        
        Returns:
            string -- chapter's full title
        """
        full = "Chapter_" + str(self.chapter_number)
        if self.chapter_number == "":
            full += ":_"+ self.chapter_name.replace(' ', '_')
        return full

    def set_chapter_name(self, name):
        """sets the chapter's name
        
        Arguments:
            name {string} -- name of chapter
        """
        if type(name) == str:
            self.chapter_name = name
    def get_chapter_name(self):
        """returns the chapter's name
        
        Returns:
            string -- chapter's name
        """
        return self.chapter_name

    def get_directory(self):
        """returns the chapter's save location
        
        Returns:
            string -- chapter's save location
        """
        return self.directory

    def download_chapter(self, save_location, killDownload=[False]):
        logger.warning("Called parent version of download_chapter. Please override this in derived classes.")
        pass


    @staticmethod
    def _convert_webp_to_jpeg(infile,outfile):
        try:
            logger.info("Converting page to jpeg format")
            jpeg = Image.open(infile).convert("RGB")
            jpeg.save(outfile)
        except IOError:
            logger.exception("Conversion Failed: ")
            #print("cannot convert", infile)
    @staticmethod
    def _load_browser_extentions(BrowserOpts):
        print("Searching for extentions")
        e
        return BrowserOpts

    def delete_chapter(self, save_location):
        chapter_path = save_location+"/"+self.get_full_title() + '.zip'
        if os.path.isfile(chapter_path) == True:
            try:
                os.remove(chapter_path)
                return 0
            except:
                return -1
        else:
            return 1

    def is_downloaded(self,save_location="."):
        save_location += "/" + self.get_full_title() + '.zip'
        if os.path.isfile(save_location) == True:
            return True
        else:
            return False

    def __lt__(self, chap):
        if isinstance(chap, Chapter):
            if self.chapter_number < chap.chapter_number:
                return True
            else:
                return False
        else:
            raise Exception("Cannot compare Chapter object and "  + str(type(chap)))
    
    def __eq__(self, chap):
        if isinstance(chap, Chapter):
            if self.chapter_number == chap.chapter_number:
                return True
            else:
                return False
        elif chap == None:
            return False
        else:
            raise Exception("Cannot compare Chapter object and "  + str(type(chap)))

    def __ne__(self, chap):
        if isinstance(chap, Chapter):
            if self.chapter_number != chap.chapter_number:
                return True
            else:
                return False
        elif chap == None:
            return True
        else:
            raise Exception("Cannot compare Chapter object and "  + str(type(chap)))

    def __gt__(self, chap):
        if isinstance(chap, Chapter):
            if self.chapter_number > chap.chapter_number:
                return True
            else:
                return False
        else:
            raise Exception("Cannot compare Chapter object and "  + str(type(chap)))

    def __hash__(self):
        return hash( ( self.chapter_number, self.chapter_name, self.chapter_link ) )

    def __str__(self):
        #print("converting Chapter to string")
        chapter_string = "Chapter " + str(self.chapter_number)
        if self.chapter_name != "":
            chapter_string += ": " + self.chapter_name
        #print("converted Chapter to string")
        return chapter_string

    def to_dict(self):
        dic = {}
        dic["Chapter Name"] = self.chapter_name
        dic["Chapter Link"] = self.chapter_link
        dic["Chapter Number"] = self.chapter_number
        return dic

    def from_dict(self,dictionary):
        if type(dictionary) is dict:
            self.chapter_name = dictionary["Chapter Name"]
            self.chapter_number = dictionary["Chapter Number"]
            self.directory =  "Chapter_" + str(self.chapter_number)
            self.chapter_link = dictionary["Chapter Link"]
