#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Chapter.py                                                    #
#description     :Contains a generic chapter object definition                  #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :Mdefins the chapter class                                     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
from bs4 import BeautifulSoup

import requests,traceback, sys, os, shutil
from PIL import Image
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

class Chapter:

    Driver_path = None
    Driver_type = None

    def __init__(self, name, number):
        self.chapter_name = name
        self.number_of_Pages = 0
        self.pages = {}
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
        if type(num) == float or type(num) == int:
            self.chapter_number = num
    def get_chapter_number(self):
        return self.chapter_number

    def set_link(self,link):
        if type(link) == str:
            self.chapter_link = link
    def get_link(self):
        return self.chapter_link

    def get_full_title(self):
        full = "Chapter_" + str(self.chapter_number)
        if self.chapter_number == "":
            full += ":_"+ self.chapter_name.replace(' ', '_')
        return full

    def set_chapter_name(self, name):
        if type(name) == str:
            self.chapter_name = name
    def get_chapter_name(self):
        return self.chapter_name

    def get_directory(self):
        return self.directory

    def download_chapter(self, save_location, killDownload=[False]):

        if killDownload[0] == True:
            return 4
        
        try:
            #display = Display(visible=0, size=(800,600))
            #display.start()
            browser = None
            if Chapter.Driver_path == None or Chapter.Driver_type == None:
                return -1
            elif Chapter.Driver_type == "Chrome":
                browser = webdriver.Chrome(executable_path=Chapter.Driver_path,options=chromeopts)
            elif Chapter.Driver_type == "Firefox":
                browser = webdriver.Firefox(executable_path=Chapter.Driver_path,options=firefoxopts)
            browser.get(self.chapter_link)
            print(self.chapter_link)
            #print(browser.page_source)
            site_source = BeautifulSoup(browser.page_source, 'lxml')
            #print(self.chapter_link)
            viewer = site_source.find('section', {"class" : "viewer",'id': 'viewer'})
            pages = viewer.find_all('a',class_='img-link')
                
            if len(pages) == 0:
                print("Failed to find chapter pages")
                browser.quit()
                return 1
            else:
                page_name = 'page_'
                print("Begining Download of Chapter " + str( self.chapter_number) )
                save_path = save_location+'/'+self.get_full_title() + "/"
                for p in pages:
                    if killDownload[0] == True:
                        if os.path.isdir(save_path):
                            shutil.rmtree(save_path)
                        print("Download of chapter_"+ str(self.chapter_number)+ ": cancelled")
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
                            print("Image URL responded with error:" + str(img.status_code))
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
                        if url_elements[-1] == "webp":
                            jpeg_name = page_name + num +'.jpeg'
                            Chapter.__convert_webp_to_jpeg( infile=save_path+filename, outfile=save_path+jpeg_name )
                            os.remove(save_path+filename)
                            self.pages[int(num)] = jpeg_name
                        else:
                            self.pages[int(num)] = filename
                save_path = save_location+'/'
                zip_name = self.get_full_title() +".zip"
                zip_file = ZipFile( save_path+zip_name ,'w')
                with zip_file:
                    pages = os.listdir(save_path+self.directory+'/')
                    for p in pages:
                        if p != zip_name:
                            zip_file.write( save_path+self.directory+'/' + p, p ) 
                            os.remove(save_path+self.directory+'/' +p)
                zip_file.close()
                os.removedirs(save_path+self.directory)
                print("Download of chapter_"+ str(self.chapter_number)+ ": complete")
                browser.quit()
                return 0
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))
            return -1
    @staticmethod
    def __convert_webp_to_jpeg(infile,outfile):
        try:
            Image.open(infile).save(outfile)
        except IOError:
            print("cannot convert", infile)

    def delete_chapter(self, save_location):
        chapter_path = save_location+"/"+self.get_full_title() + '.zip'
        if os.path.isfile(chapter_path) == True:
            try:
                os.remove(chapter_path)
                self.pages = {}
                return 0
            except:
                return -1
        else:
            return 1

    def is_downloaded(self,save_location="."):
        save_location += "/" + self.get_full_title() + '.zip'
        #print(save_location)
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
        dic["Pages"] = self.pages
        return dic
    def from_dict(self,dictionary):
        if type(dictionary) is dict:
            self.chapter_name = dictionary["Chapter Name"]
            self.chapter_number = dictionary["Chapter Number"]
            self.directory =  "Chapter_" + str(self.chapter_number)
            self.chapter_link = dictionary["Chapter Link"]
            if dictionary.get("Pages") == None:
                self.pages = {}
            else:
                self.pages = dictionary["Pages"]
