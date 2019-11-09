#!/usr/bin/python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

import requests,traceback, sys, os, shutil

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
opts = Options()
opts.set_headless()
assert opts.headless

class Chapter:

    def __init__(self, name, number):
        self.chapter_name = name
        self.directory = "Chapter_" + str(number)
        self.number_of_Pages = 0
        self.pages = {}
        if type(number) is float:
            num_str = str(number)
            #print(num_str)
            if num_str[-1] is '0':
                self.chapter_number = int(number)
            else:
                self.chapter_number = number
        elif type(number) is int:
            self.chapter_number = number
        else:
            raise Exception("Chapter number must be a integer or float")
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

    def set_chapter_name(self, name):
        if type(name) == str:
            self.chapter_name = name
    def get_chapter_name(self):
        return self.chapter_name

    def get_directory(self):
        return self.directory

    def download_chapter(self, save_location):

        try:
            #display = Display(visible=0, size=(800,600))
            #display.start()
            browser = webdriver.Chrome(executable_path="./WebDrivers/Chrome/chromedriver",options=opts)
            browser.get(self.chapter_link)
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
                save_path = save_location+'/'+self.directory
                if self.chapter_name != "":
                    save_path += ":" + self.chapter_name
                if os.path.exists(save_path) != True:
                    os.makedirs(save_path)
                save_path += "/"
                for p in pages:
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
                    print(save_path+filename)
                    with open(save_path+filename, 'wb') as f:
                        f.write(img.content)
                        f.close()
                    self.pages[int(num)] = filename
                print("Download of " + self.chapter_name + ": complete")
                browser.quit()
                return 0
            #display.quit()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print("Error occured: " + str(e))
            return -1
            #print(e )
            #p rint("Failed to download chapter")

    def delete_chapter(self, save_location):
        chapter_path = save_location+"/Chapter_"+str(self.chapter_number)
        if self.chapter_name != "":
            chapter_path += ":" + self.chapter_name 

        if os.path.isdir(chapter_path)== True:
            try:
                shutil.rmtree(chapter_path,False)
                self.pages = {}
                return 0
            except:
                return -1
        else:
            return 1

    def is_downloaded(self,save_location="."):
        print(self.pages)
        if len(self.pages) == 0:
            print("no chapters downloaded")
            return False
        
        path = save_location+'/'+self.directory
        print(path)
        if self.chapter_name != "":
            path += ":" + self.chapter_name
        if os.path.isdir(path) == False:
            print("path is not a directory")
            return False
        else:
            pages = os.listdir(path)
            print(pages)
            num = 0
            for p in pages:
                for dp in self.pages.values():
                    if p == dp:
                        num += 1
            if num != len(self.pages):
                return False
        return True


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
