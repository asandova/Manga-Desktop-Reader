#!/usr/bin/python3
# -*- coding: utf-8 -*-
from .MangaChapter import Chapter
from .MangaSource import Manga_Source
from .MangaStream import Manga_Stream

from bs4 import BeautifulSoup
import requests, re, json, os


class MangaPark_Source(Manga_Source):

    Versions = {
        "Duck"  :    4,
        4   :   "Duck",
        "Rock"  :    6,
        6   : "Rock",
        "Fox"   :   1,
        1   : "Fox",
        "Panda" :   3,
        3   : "Panda"
    }

    def __init__(self):
        Manga_Source.__init__(self)
        self.site_url = "https://www.mangapark.net"
        self.site_domain = "https://www.mangapark.net"


    def from_dict(self, dictionary):
        self.site_url = dictionary["Site URL"]
        self.site_domain = dictionary["Site Domain"]
        self.manga_extention = dictionary["Manga Extention"]
        self.Title = dictionary["Title"]
        self.directory = self.Title.replace(' ', '_')
        self.summary = dictionary["Summary"] 
        self.authors = dictionary["Author(s)"] 
        self.artists = dictionary["Artist(s)"]
        self.genres = dictionary["Genre(s)"] 
        self.cover_location = dictionary["Cover Location"]
        for s in dictionary["Manga Stream(s)"]:
            stream = Manga_Stream()
            stream.from_dict( s )
            self.streams.append( stream )
        
    def to_dict(self):
        dic = {}
        dic["Site URL"] = self.site_url
        dic["Site Domain"] = self.site_domain
        dic["Manga Extention"] = self.manga_extention
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

    def Download_Manga(self, location="",keep=False):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            for c in s.chapters:
                if keep == True:
                    if self.keep.get(s) == False:
                        self.keep[s.name] = []
                        self.keep[s.name].append(c.get_chapter_number)
                    else:
                        if self.keep[s.name].count(c.get_chapter_number) == 0:
                            self.keep[s.name].append(c.get_chapter_number)
                #title = self.Title.replace(" ", '_')
                stream_name = s.name.replace(' ', '_')
                c.download_chapter( save_location +'/'+self.directory+'/'+ stream_name)

    def Download_Manga_stream(self, stream_id, location="",Keep=False):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            if s.id == stream_id:
                for c in s.chapters:
                    if Keep == True:
                        if self.keep.get(s) == False:
                            self.keep[s.name] = []
                            self.keep[s.name].append(c.get_chapter_number)
                        else:
                            if self.keep[s.name].count(c.get_chapter_number) == 0:
                                self.keep[s.name].append(c.get_chapter_number)

                    #title = self.Title.replace(" ", '_')
                    stream_name = self.streams[stream_id].name.replace(' ', '_')
                    c.download_chapter( save_location +'/'+self.directory+'/'+ stream_name)
                return
    def Download_Manga_Chapter(self, stream_id, chapter_number, location="",keep=False):
        save_location = self.save_location
        if location != "":
            save_location == location
        for s in self.streams:
            if s.id == stream_id:
                for k in s.chapters.keys():
                    if  s.chapters[k].get_chapter_number() == chapter_number:
                        if keep == True:
                            if self.keep.get(s.name) == False:
                                self.keep[s.name] = []
                                self.keep[s.name].append(chapter_number)
                            else:
                                if self.keep[s.name].count(chapter_number) == 0:
                                    self.keep[s.name].append(chapter_number)
                        #title = self.Title.replace(" ", '_')
                        stream = self.get_stream_with_id(stream_id)
                        stream_name = stream.name.replace(' ', '_')
                        code =  s.chapters[k].download_chapter(save_location +'/'+self.directory+'/'+ stream_name)
                        return code
                return -1
        return -2

    def _extract_cover(self):
        cover_data = self.site_html.find('div', class_="w-100 cover")
        
        #title = self.Title.replace(' ','_')
        if os.path.exists(self.save_location+'/'+self.directory) == False:
            os.mkdir(self.save_location+'/'+self.directory)
        cover_image_link = cover_data.img["src"]
        cover = requests.get("https:"+ cover_image_link)
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
        self.directory = self.Title.replace(' ', '_')

    def _extract_summary(self):
        s = self.site_html.find('p', class_='summary').text
        self.summary = s

    def _extract_managa_info(self):
        table = self.site_html.find('table', class_="attr")
        Author_data = table.find('th', text="Author(s)").parent
        Artist_data = table.find('th', text="Artist(s)").parent
        Genre_data = table.find('th', text="Genre(s)").parent
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
            manga_stream = Manga_Stream(version_name, stream_id)
            chapters = s.find_all('a', class_="ml-1 visited ch")
            for c in chapters:
                
                link = c.parent.parent
                link = link.find('a', text="all")["href"]
                number_str = c.text
                number_str_elements = re.compile("[vV]ol(ume)*[.]*[ ]*[0-9]+[ ]").split(number_str)
                #print(number_str_elements)
                number_start = -1
                number_end = -1
                #print(number_str_elements[-1])
                for num in range(0, len(number_str_elements[-1])):
                    if number_start == -1 and number_str_elements[-1][num].isnumeric():
                        number_start = num
                    elif number_start != -1 and number_str_elements[-1][num].isnumeric() == False:
                        if number_str_elements[-1][num+1].isnumeric() == True:
                            continue
                        else:
                            number_end = num
                        #print(number_end)
                        break
                #print(number_str_elements)
                #print(f"start Number: {number_start}\tend Number: {number_end}")
                if number_end != -1:
                    number = float(number_str_elements[-1][number_start:number_end])
                elif number_end == -1 and number_start == -1:
                    print("encountered non-numbered chapter")
                    continue
                else:
                    number = float(number_str_elements[-1][number_start:])
                number_str_elements = number_str_elements[-1].split(': ')
                name = ""
                if len( number_str_elements) > 1:
                    name = number_str_elements[-1]
                else:
                    #if stream_id == 4:
                        #print(c.parent.parent.prettify())
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

                chap = Chapter(name, number)
                chap.set_link( self.site_domain + link)
                #print(f"adding chapter {chap.get_full_title()}")
                manga_stream.add_chapter(chap)
            #print("adding stream " + manga_stream.name)
            self.add_stream(manga_stream)
        print("extraction of streams: Complete")

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
            s += str(stream) + "\n"
        return s

if __name__ == "__main__":
    
    #test = MangaPark_Source()
    
    test2 = MangaPark_Source()
    test2.set_default_save_location('./Manga')
    #test.request_manga("https://mangapark.net/manga/ryoumin-0-nin-start-no-henkyou-ryoushusama-fuurou")
    test2.request_manga("https://mangapark.net/manga/tensei-shitara-ken-deshita")
    test2.extract_manga()
    with open('test.json', 'w') as f:
        f.write( json.dumps( test2.to_dict(),indent=1 ) ) 

    test2.Download_Manga_Chapter(stream_id=MangaPark_Source.Versions["Fox"],chapter_number=1 , location="./Manga")