#!/usr/bin/python3
# -*- coding: utf-8 -*-
#===============================================================================#
#title           :Stream.py                                                     #
#description     :contains the Stream class                                     #
#author          :August B. Sandoval (asandova)                                 #
#date            :2020-3-2                                                      #
#version         :0.1                                                           #
#usage           :defineds the Stream class                                     #
#notes           :                                                              #
#python_version  :3.6.9                                                         #
#===============================================================================#
from .Chapter import Chapter

class Stream:
    def __init__(self, name="", id=-1):
        self.name = name
        self.directory = name.replace(' ', '_')
        self.chapters = {}
        self.id = id

    def add_chapter(self, chap):
        if isinstance(chap,Chapter):
            if self.chapters.get(chap.get_chapter_number()) != None:
                #print("duplicate chapter number")
                #self.chapters.insert(i,chap)
                return
            else:
                self.chapters[chap.get_chapter_number()] = chap
        else:
            raise Exception("Attemted to add non Chapter object to chapter list")

    def get_chapters(self):
        chapters = []
        for k in self.chapters.keys():
            chapters.append(self.chapters[k])
        return chapters
    def get_chapter(self,chapter_number):
        return self.chapters[chapter_number]

    def get_name(self):
        return self.name
    def get_directory(self):
        return self.directory
    def get_id(self):
        return self.id

    def __str__(self):
        #print("converting Manga_Stream to string")
        stream_string = "--------" + self.name + "--------\n"
        #print(len(self.chapters))
        for k in self.chapters.keys():
            stream_string += str( self.chapters[k]  ) + '\n'
        #print("converted Manga_Stream to string")
        return stream_string

    def size(self):
        return len(self.chapters)


    def to_dict(self):
        dic = {}
        dic["Stream Name"] = self.name
        dic["Stream ID"] = self.id
        dic["Chapters"] = []
        for k in self.chapters.keys():
            dic["Chapters"].append( self.chapters[k].to_dict() )
        return dic

    def from_dict(self, dictionary):
        if type(dictionary) is dict:
            self.name = dictionary["Stream Name"]
            self.directory = self.name.replace(' ','_')
            self.id = dictionary["Stream ID"]
            self.chapters = {}
            for c in dictionary["Chapters"]:
                #print(type(c))
                chap = Chapter('',-1)
                chap.from_dict( c )
                self.chapters[chap.get_chapter_number()] = chap

