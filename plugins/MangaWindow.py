#!/usr/bin/python3
# -*- coding: utf-8 -*-

from src.Chapter import Chapter
from src.TitleSource import TitleSource
from src.Stream import Stream

from bs4 import BeautifulSoup
import requests, re, json, os, logging, shutil
from logging.handlers import RotatingFileHandler
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
logger.propagate = False
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/"+__name__+".log"
rotating_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
os.makedirs(os.path.dirname( log_file ), exist_ok=True)
formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

class TitlePlugin(TitleSource):

    _supported_domains = ["mangawindow.net", "bato.to"]

    description = "Allows for extraction of titles from MangaWindow.net and bato.to"
    plugin_id = "MangaWindow"


    def __init__(self):
        TitleSource.__init__(self)
        self.site_name = "Manga Window/Bato.to"

    def _extract_cover(self):
        cover_data = self.site_html.find('img', class_="shadow-6")

        if os.path.exists(self.save_location+'/'+self.directory) == False:
            os.mkdir(self.save_location+'/'+self.directory)
        cover_image_link = cover_data["src"]
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
        self.Title = self.site_html.find('h3', class_="item-title").a.text
        self.directory = re.sub(TitlePlugin.replace_illegal_character_pattern, "-", self.Title)
        self.directory = re.sub(TitlePlugin.replace_space, "_", self.directory)

    def _extract_summary(self):
        summary_class = "col-24 col-sm-16 col-md-18 mt-4 mt-sm-0 attr-main"
        container = self.site_html.find("div", class_=summary_class)
        summary = self.site_html.find('pre')
        if summary != None:
            self.summary = summary.text
        else:
            self.summary = "N/A"

    def _extract_title_info(self):
        title_containter_class = "col-24 col-sm-16 col-md-18 mt-4 mt-sm-0 attr-main"
        container = self.site_html.find("div", class_= title_containter_class)
        Author_data = container.find('b', text="Authors:").parent
        Genre_data = container.find('b', text="Genres:").parent.span
        Genre_data = Genre_data.find_all("span")
        self.artists = ["N/A"]
        for a in Author_data.find_all('a'):
            self.authors.append( a.text )
        Genre_list = []
        for g in Genre_data:
            Genre_list.append(g.text)
        print(Genre_list)
        
        self.genres = Genre_list

    def _extract_streams(self):
        Chapter_list_class = "p-2 d-flex flex-column flex-md-row item"

        chapter_container = self.site_html.find("div", class_="main")
        #print(chapter_container.prettify())
        chapter_list =  chapter_container.find_all("div", class_=Chapter_list_class)
        chapter_list += chapter_container.find_all("div", class_=Chapter_list_class + " ")
        chapter_list += chapter_container.find_all("div", class_=Chapter_list_class + " is-new")
        chapter_list += chapter_container.find_all("div", class_=Chapter_list_class + "  is-new")
        #print(len( chapter_list ))
        title_stream = Stream("Manga Window", id=1)
        for c in chapter_list:
            link = c.a["href"]
            num_str = c.find("b").text
            number = self.extract_chapter_number(num_str)
            title = c.a.text
            title_elements = title.split(":")
            title = title_elements[-1]
            start = 0
            end = -1
            for i in range(0, len(title) ):
                if title[i].isalpha() == True:
                    start = i
                    break
            for i in range(len(title)-1, 0, -1):
                if title[i].isspace() == False:
                    end = i+1
                    break

            chap =  ChapterPlugin(title[start:end], number)
            chap.set_link("https://" + self.site_domain+link)
            #print(chap)
            title_stream.add_chapter(chap)
        self.add_stream(title_stream)
        
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
        
    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        if dictionary.get("Download Time") == None:
            self.download_time = ""
        else:
            self.download_time = dictionary["Download Time"]
        self.Title = dictionary["Title"]
        self.summary = dictionary["Summary"]
        self.authors = dictionary["Author(s)"]
        self.artists = dictionary["Artist(s)"]
        self.genres = dictionary["Genre(s)"]
        self.cover_location = dictionary["Cover Location"]

        for s in dictionary["Manga Stream(s)"]:
            stream = Stream()
            stream.from_dict( s, ChapterPlugin )
            self.streams.append( stream )

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
            viewer = site_source.find('div', {"class" : "d-flex flex-column align-items-center align-content-center",'id': 'viewer'})
            pages = viewer.find_all('div', class_="item invisible")
                
            if len(pages) == 0:
                logger.info("Failed to find chapter pages. --- Terminiating Borwser.")
                browser.quit()
                return 1
            else:
                page_name = 'page_'
                logger.info( "Begining Download of Chapter " + str( self.chapter_number) )
                save_path = os.path.join( save_location, self.get_full_title() ) 
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
                        url = p.img['src']
                        num_str = p.span.text
                        num_str_elements = num_str.split("/")
                        num = num_str_elements[0]
                        img = requests.get(url)
                        url_elements = url.split('.')
                        extention = url_elements[-1].split("?")
                        filename = page_name + num +'.'+ extention[0]
                        if(img.ok == False):
                            logger.info("Image URL responded with error:" + str(img.status_code) + " --- Terminating Borwser.")
                            browser.quit()
                            return 2
                        if num == -1:
                            browser.quit()
                            return 3
                        if os.path.isdir(save_path) == False:
                            os.makedirs(save_path)
                        image_save_path = os.path.join(save_path, filename)
                        with open( image_save_path, 'wb') as f:
                            f.write(img.content)
                            f.close()
                        if url_elements[-1] == "webp":
                            jpeg_name = page_name + num +'.jpeg'
                            out_path = os.path.join(save_path, jpeg_name)
                            Chapter.__convert_webp_to_jpeg( infile=image_save_path, outfile=save_path+jpeg_name )
                            os.remove(image_save_path)
                #save_path = save_location+'/'
                zip_name = self.get_full_title() +".zip"

                zip_file = ZipFile( os.path.join( save_path,zip_name) ,'w')
                logger.info("Archiving Chapter...")
                with zip_file:
                    pages = os.listdir( os.path.join( save_path,self.directory)  )
                    page_path = os.path.join(save_path,self.directory)
                    for p in pages:
                        if p != zip_name:
                            page_full_path = os.path.join( page_path, p )
                            zip_file.write( page_full_path, p ) 
                            os.remove(page_full_path)
                zip_file.close()
                logger.info("Archive Complete")
                logger.info("Cleaning download space")
                os.removedirs( os.path.join( save_path, self.directory ) )
                logger.info("Download of chapter_"+ str(self.chapter_number)+ ": complete --- Terminiating Browser")
                browser.quit()
                return 0
        except Exception:
            logger.exception("Error occured: ")
            return -1