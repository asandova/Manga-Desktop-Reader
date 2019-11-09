#!/usr/bin/python3
# -*- coding: utf-8 -*-
from manga_chapter import Chapter

class Manga_Stream:
    def __init__(self, name="", id=-1):
        self.name = name
        self.directory = name.replace(' ', '_')
        self.chapters = []
        self.id = id

        
    def add_chapter(self, chap):
        if isinstance(chap,Chapter):
            if len(self.chapters) == 0:
                self.chapters.append(chap)
                return
            for i in range(0, len( self.chapters) ):
                if chap == self.chapters[i]:
                    #print("duplicate chapter number")
                    #self.chapters.insert(i,chap)
                    return
                elif chap < self.chapters[i]:
                    self.chapters.insert(i, chap)
                    return
            
            #print("adding to end of Chapter list")
            self.chapters.append(chap)
        else:
            raise Exception("Attemted to add non Chapter object to chapter list")

    def get_chapters(self):
        return self.chapters
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
        for chap in self.chapters:
            stream_string += str(chap) + '\n'
        #print("converted Manga_Stream to string")
        return stream_string

    def size(self):
        return len(self.chapters)


    def to_dict(self):
        dic = {}
        dic["Stream Name"] = self.name
        dic["Stream ID"] = self.id
        dic["Chapters"] = []
        for c in self.chapters:
            dic["Chapters"].append( c.to_dict() )
        return dic

    def from_dict(self, dictionary):
        if type(dictionary) is dict:
            self.name = dictionary["Stream Name"]
            self.directory = self.name.replace(' ','_')
            self.id = dictionary["Stream ID"]
            self.chapters = []
            for c in dictionary["Chapters"]:
                #print(type(c))
                chap = Chapter('',-1)
                chap.from_dict( c )
                self.chapters.append(chap)

