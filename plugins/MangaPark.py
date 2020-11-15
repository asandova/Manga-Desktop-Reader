#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :MangaPark.py                                                  #
#description     :contains the TitlePlugin for MangaPark                        #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.3                                                           #
#usage           :defineds the TitlePlugin for MangaPark                        #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
from src.Chapter import Chapter
from src.TitleSource import TitleSource
from src.Stream import Stream

from bs4 import BeautifulSoup
from datetime import datetime
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

log_file = "logs/MangaPark.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class TitlePlugin(TitleSource):

    _supported_domains = ["mangapark.net","https://mangapark.net"]

    description = "Allows for extraction of titles from MangaPark.net"

    def __init__(self):
        TitleSource.__init__(self)
        self.site_name = "Manga Park"

    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        self.Title = dictionary["Title"]
        if dictionary.get("Download Time") == None:
            self.download_time = ""
        else:
            self.download_time = dictionary["Download Time"]
        self.directory = re.sub(TitlePlugin.replace_illegal_character_pattern, "-", self.Title)
        self.directory = re.sub(TitlePlugin.replace_space, "_", self.directory)
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
        dic["Download Time"] = self.download_time
        dic["Title"] = self.Title
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
        cover_data = self.site_html.find('div', class_="w-100 cover")

        if os.path.exists(self.save_location+'/'+self.directory) == False:
            os.mkdir(self.save_location+'/'+self.directory)
        cover_image_link = cover_data.img["src"]
        cover = requests.get( cover_image_link)
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
        self.Title = self.site_html.find('div', class_="pb-1 mb-2 line-b-f hd").h2.a.text
        self.directory = re.sub(TitlePlugin.replace_illegal_character_pattern, "-", self.Title)
        self.directory = re.sub(TitlePlugin.replace_space, "_", self.directory)

    def _extract_summary(self):
        s = self.site_html.find('p', class_='summary').text
        self.summary = s

    def _extract_title_info(self):
        table = self.site_html.find('table', class_="attr")
        Author_data = table.find('th', text="Author(s)").parent
        Artist_data = table.find('th', text="Artist(s)").parent
        Genre_data = table.find('th', text="Genre(s)").parent
        self.authors = []
        self.artists = []
        self.genres = []
        for a in Author_data.find_all('a', target='_blank'):
            self.authors.append( a.text )
        for a in Artist_data.find_all('a', target="_blank"):
            self.artists.append( a.text )
        for g in Genre_data.find_all('a', target='_blank'):
            if g.b != None:
                self.genres.append(g.b.text)
            else:
                self.genres.append(g.text)

    def _extract_streams(self):
        stream_list = self.site_html.find('div', class_='book-list-1')
        streams = stream_list.find_all('div', class_='mt-3 stream')
        streams += stream_list.find_all('div', class_='mt-3 stream collapsed')
        for s in streams:
            stream_id_str = s['id'].split('_')
            stream_id = int(stream_id_str[-1])
            version_tag = "ml-1 stream-text-" + str(stream_id)
            version_name = s.find('span', class_=version_tag).text
            manga_stream = Stream(version_name, stream_id)
            chapters = s.find_all('a', class_="ml-1 visited ch")
            for c in chapters:

                link = c.parent.parent
                link = link.find("a", text="all")["href"]

                number_str = c.text
                number_str_elements = re.compile("[vV]ol(ume)*[.]*[ ]*[0-9]+[ ]").split(number_str)
                number = self.extract_chapter_number( number_str )

                number_str_elements = number_str_elements[-1].split(': ')
                name = ""
                if len( number_str_elements) > 1:
                    name = number_str_elements[-1]
                else:
                    Title_tag = c.parent.parent.find('div', class_="d-none d-md-flex align-items-center ml-0 ml-md-1 txt")
                    if Title_tag != None:
                        #print(Title_tag.text)
                        name = Title_tag.text
                        start = 0
                        for c in name:
                            if c.isalpha() == True:
                                break
                            start += 1
                        name = name[start:]
                        #print(name)
                    else:
                        name = ""
                    if len(name) > 0:
                        end = len(name)-1
                        for i in range( len(name)-1, -1,-1 ):
                            #print(name[i])
                            if name[i] != ' ':
                                end = i+1
                                break
                        name = name[0:end]

                chap = ChapterPlugin(name, number)
                print("https://" + self.site_domain + link)
                chap.set_link( "https://" + self.site_domain + link)
                manga_stream.add_chapter(chap)
            self.add_stream(manga_stream)
        logger.info("extraction of streams: Complete")

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

    def download_chapter(self, save_location, killDownload=[False]):
        webp_pattern = re.compile("webp.*")

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
            logger.info("Navigating to " + self.chapter_link)
            browser.get(self.chapter_link)
            site_source = BeautifulSoup(browser.page_source, 'lxml')
            viewer = site_source.find('section', {"class" : "viewer",'id': 'viewer'})
            pages = viewer.find_all('a',class_='img-link')
                
            if len(pages) == 0:
                logger.info("Failed to find chapter pages.--- Terminiating Borwser.")
                browser.quit()
                return 1
            else:
                page_name = 'page_'
                logger.info( "Begining Download of Chapter " + str( self.chapter_number) )
                save_path = save_location+'/'+self.get_full_title() + "/"
                for p in pages:
                    if killDownload[0] == True:
                        logger.info("Download Kill singal received. Clearing download")
                        if os.path.isdir(save_path):
                            shutil.rmtree(save_path)
                        logger.info("Terminiating Browser")  
                        browser.quit()
                        return 4
                    else:
                        self.number_of_Pages += 1
                        #print(p.prettify())
                        url = p.img['src']
                        num = p.img["i"]
                        img = requests.get(url)
                        url_elements = url.split('.')
                        filename =page_name + num +'.'+ url_elements[-1]
                        if(img.ok == False):
                            logger.info("Image URL responded with error:" + str(img.status_code) + " --- Terminating Borwser.")
                            browser.quit()
                            return 2
                        if num == -1:
                            browser.quit()
                            return 3
                        if os.path.isdir(save_path) == False:
                            os.makedirs(save_path)
                        with open(save_path+filename, 'wb') as f:
                            f.write(img.content)
                            f.close()
                        if re.match(webp_pattern, url_elements[-1]):
                        #if url_elements[-1] == "webp":
                            jpeg_name = page_name + num +'.jpeg'
                            ChapterPlugin._convert_webp_to_jpeg( infile=save_path+filename, outfile=save_path+jpeg_name )
                            os.remove(save_path+filename)
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
            logger.exception("Error occured: ")
            return -1
