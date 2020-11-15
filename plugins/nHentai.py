#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :nhentai.py                                                    #
#description     :contains the TitlePlugin for nhentai                          #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :defineds the TitlePlugin for nhentai                          #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
from src.Chapter import Chapter
from src.TitleSource import TitleSource
from src.Stream import Stream

from bs4 import BeautifulSoup
import requests, re, json, os, logging, shutil
from zipfile import ZipFile

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
chromeopts = ChromeOptions()
chromeopts.set_headless()
assert chromeopts.headless

firefoxopts = FirefoxOptions()
firefoxopts.set_headless()
assert firefoxopts.headless

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/nHentai.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class TitlePlugin(TitleSource):

    _supported_domains = ["nhentai.net"]

    description = "Allows for extraction of titles from nHentai.net"

    def __init__(self):
        TitleSource.__init__(self)
        self.site_name = "nHentai"
        self.page_links = []

    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        self.Title = dictionary["Title"]
        if dictionary.get("Download Time") == None:
            self.download_time = ""
        else:
            self.download_time = dictionary["Download Time"]
        self.directory = self.Title.replace(' ', '_')
        self.summary = dictionary["Summary"] 
        self.authors = dictionary["Author(s)"] 
        self.artists = dictionary["Artist(s)"]
        self.genres = dictionary["Genre(s)"] 
        self.cover_location = dictionary["Cover Location"]

        for s in dictionary["Manga Stream(s)"]:
            stream = Stream()
            stream.from_dict( s, ChapterPlugin )
            self.streams.append( stream )
        
    def to_dict(self):
        dic = {}
        dic["Site URL"] = self.site_url
        dic["Site Domain"] = self.site_domain
        dic["Manga Extention"] = self.manga_extention
        dic["Title"] = self.Title
        dic["Download Time"] = self.download_time
        dic["Summary"] = self.summary
        dic["Author(s)"] = self.authors
        dic["Artist(s)"] = self.artists
        dic["Genre(s)"] = self.genres
        dic["Cover Location"] = self.cover_location
        dic["Manga Stream(s)"] = []
        for s in self.streams:
            dic["Manga Stream(s)"].append( s.to_dict() )
        return dic

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

    def _extract_cover(self):
        cover_data = self.site_html.find('div', id="cover")

        if os.path.exists(self.save_location+'/'+self.directory) == False:
            os.mkdir(self.save_location+'/'+self.directory)
        cover_image_link = cover_data.a.img["data-src"]
        cover = requests.get(cover_image_link)
        ext_loc = 0
        for i in range(0,len(cover_image_link)):
            if cover_image_link[i] == '.':
                ext_loc = i
        extention = cover_image_link[ext_loc:]
        if cover.ok != True:
            print("Failed to download cover")
            return
        self.cover_location = self.save_location+'/'+self.directory+"/cover"+extention
        with open(self.cover_location, 'wb') as f:
            f.write(cover.content)
            f.close()

    def _extract_title(self):
        self.Title = self.site_html.find("div" , id="info").h1.text.strip()
        self.directory = re.sub(TitlePlugin.replace_illegal_character_pattern, "-", self.Title)
        self.directory = re.sub(TitlePlugin.replace_space, "_", self.directory)

    def _extract_summary(self):
        self.summary = "N/A"

    def _extract_title_info(self):
        container = self.site_html.find("section", id="tags")
        subcontainer = container.find_all("div",class_="tag-container field-name ")
        number_replace = re.compile( "([0-9]+\w{0,1})" )
        for sub in subcontainer:
            if "Artists:" in sub.text:
                artists = sub.find_all("a")
                for a in artists:
                    artist = a.text.strip()
                    artist = re.sub(number_replace,"",artist)
                    self.artists.append( artist)
                    self.authors.append( artist )

            if "Tags:" in sub.text:
                genres = sub.find_all("a")
                print(len(genres))
                for g in genres:
                    genre = g.text.strip()
                    genre = re.sub(number_replace,"",genre)
                    self.genres.append( genre)
        
    def _extract_streams(self):
        page_container = self.site_html.find("div", id="thumbnail-container")
        pages = page_container.find_all("div", class_="thumb-container")
        title_stream = Stream("nhentai", id=69)
        for p in pages:
            #p.prettify()
            self.page_links.append( "https://" + self.site_domain + p.a["href"])

        chap = ChapterPlugin("", 1)
        chap.set_link(self.page_links)
        #chap.set_link("https://" + self.site_domain+link)
        #print(chap)
        title_stream.add_chapter(chap)
        self.add_stream(title_stream)

    # Static Methods ------------------------------------------------------------------------#

    @staticmethod
    def is_domain_supported(domain):
        for d in TitlePlugin._supported_domains:
            if domain == d:
                return True
        return False

    @staticmethod
    def get_supported_domains():
        return TitlePlugin._supported_domains

class ChapterPlugin(Chapter):

    def __init__(self, name, number):
        super().__init__(name, number)
        self.page_links = {}

    def set_link(self, link):
        if type(link) == list:
            for l in link:
                #print(link)
                link_elements = l.split("/")
                #print(link_elements)
                self.page_links[ link_elements[-2] ] = l
        else:
            super().set_link(link)


    def to_dict(self):
        dic = {}
        dic["Chapter Name"] = self.chapter_name
        dic["Chapter Link"] = ""
        dic["Chapter Number"] = self.chapter_number
        dic["Page Links"] = self.page_links
        return dic

    def from_dict(self,dictionary):
        if type(dictionary) is dict:
            self.chapter_name = dictionary["Chapter Name"]
            self.chapter_number = dictionary["Chapter Number"]
            self.directory =  "Chapter_" + str(self.chapter_number)
            self.chapter_link = ""
            self.page_links = dictionary["Page Links"]

    def download_chapter(self, save_location, killDownload=[False]):
        if killDownload[0] == True:
            logger.info("Download kill signal received.")
            return 4
        
        try:
            browser = None
            if Chapter.Driver_path == None or Chapter.Driver_type == None:
                return -1
            elif Chapter.Driver_type == "Chrome":
                browser = webdriver.Chrome(executable_path=Chapter.Driver_path,options=chromeopts)
                logger.info("Starting headless Chrome Browser")
            elif Chapter.Driver_type == "Firefox":
                browser = webdriver.Firefox(executable_path=Chapter.Driver_path,options=firefoxopts)
                logger.info("Starting headless Firefox Browser")

            logger.info( "Begining Download of Chapter " + str( self.chapter_number) )
            save_path = save_location+'/'+self.get_full_title() + "/"
            page_name = "page_"
            for page_num in self.page_links.keys():
                logger.info("Downloading page " + page_num)
                if killDownload[0] == True:
                    logger.info("Download Kill singal received. Clearing download")
                    if os.path.isdir(save_path):
                        shutil.rmtree(save_path)
                    logger.info("Terminiating Browser")  
                    browser.quit()
                    return 4
                
                #logger.info("Navigating to " + self.page_links[page_num] )
                browser.get( self.page_links[page_num] )
                page_source = BeautifulSoup(browser.page_source, 'lxml')
                page_image_url = page_source.find("section", id="image-container").a.img["src"]
                img = requests.get(page_image_url)
                url_elements = page_image_url.split('.')
                filename = page_name + page_num +'.'+ url_elements[-1]
                if(img.ok == False):
                    logger.info("Image URL responded with error:" + str(img.status_code) + " --- Terminating Borwser.")
                    browser.quit()
                    return 2
                if os.path.isdir(save_path) == False:
                    os.makedirs(save_path)
                with open(save_path+filename, 'wb') as f:
                    f.write(img.content)
                    f.close()
            save_path = save_location+'/'
            zip_name = self.get_full_title() +".zip"
            zip_file = ZipFile( save_path+zip_name ,'w')
            logger.info("Archiving Chapter...")
            with zip_file:
                pages = os.listdir(save_path+self.directory+'/')
                for p in pages:
                    if p != zip_name:
                        zip_file.write( save_path+self.directory+'/' + p, p ) 
                        os.remove(save_path+self.directory+'/' +p)
            zip_file.close()
            logger.info("Archive Complete")
            logger.info("Cleaning download space")
            os.removedirs(save_path+self.directory)
            logger.info("Download of chapter_"+ str(self.chapter_number)+ ": complete --- Terminiating Browser")
            browser.quit()
            return 0
            
        except Exception:
            logger.exception("Error occured ")
            return -1
