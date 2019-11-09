#!/usr/bin/python
import sys, getopt, requests, os

urls = []

def get_urls(filename):
    with open(filename, "r") as line:
        content = line.readlines()
    #print(content)
    for c in content:
        urls.append( remove_newline_character(c) )

def remove_newline_character(_str):
    if _str[-1] == '\n':
        _str = _str.replace('\n', '')
    return _str

def resolve_same_name(fname, location):
    num = 1
    is_extention = False
    extention = ""
    name = ""
    for c in fname:
        if c == '.':
            is_extention = True
        
        if is_extention == True:
            extention += c
        else:
            name += c
    #print("name: " + name)
    #print("ext: " + extention)
    exist = os.path.isfile( location + "/" + fname )
    if exist == True:
        while True:
            new_name = name + "(" + str(num) + ")" + extention
            if os.path.isfile( location + "/" + new_name ) == False:
                #print("new name: " + new_name)
                return new_name
            num += 1

def does_file_exist(name, location):
    if os.path.isfile( location + "/" + name):
        return True
    else:
        return False

def extract_name_from_url(url):
    temp = ""
    for c in url:
        if c == '/':
            temp = ""
        else:
            temp += c
    return temp

def download_from_url(url, location):
    r = requests.get(url)
    if r.ok != True:
        print("URL: " + str(url) + " responded with error: " + str(r.status_code) )
    else:
        name = extract_name_from_url(url)
        if does_file_exist(name, location):
            name = resolve_same_name(name, location)

        with open( location +'/'+ name, 'wb') as f:
            f.write(r.content)
        print("Download competed: " + url)
def main(argv):
    inputfile = ''
    outputDir = 'downloads'
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "odir"])
    except getopt.GetoptError:
        print("test.py -i <inputfile> -o <outputDireargsctory>" )
        sys.exit()
    for opt, arg in opts:
        if opt == '-h':
            print("test.py -i <inputfile> -o <outputDirectory>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--odir"):
            outputDir = arg

    print("input file is " + str(inputfile))
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    get_urls(inputfile)
    for u in urls:
        download_from_url(u, outputDir)

if __name__ == "__main__":
    main(sys.argv[1:])
