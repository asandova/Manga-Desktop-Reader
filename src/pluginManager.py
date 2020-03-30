#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib
import os, sys, re
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s:%(name)s -- %(message)s")

log_file = "logs/PluginManager.log"
os.makedirs(os.path.dirname( log_file ), exist_ok=True)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class Manager:

    instance = None

    def __init__(self, pluginParent):
        if Manager.instance != None:
            raise Exception("Only one plugin manager can be created")
            logger.warning("Tried to make another instance of PluginManager")
        else:
            self.titleSources = {}
            self.PluginParent = pluginParent
            Manager.instance = self
        
    def discover_sources(self):
        sys.path.append( os.path.dirname(sys.executable) )
        files = os.listdir("./plugins/")
        for f in files:
            if os.path.isdir("./plugins/" + f) == False:
                fname, ext = os.path.splitext(f)
                if fname != "__init__" and ext == ".py":
                    try:
                        module = importlib.import_module( "plugins." + fname , ".")
                        source = module.TitlePlugin()
                        if isinstance( source, self.PluginParent ) == True:
                            logger.debug( "Discovered TitleSource plugin: " + fname )
                            self.titleSources[fname] = module
                        print(module)
                    except Exception:
                        logger.exception("Import of plugin " + fname + " expreience exception")
                    except:
                        logger.info("Failed to import TitleSource plugin: " + fname )

    def create_instance(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):  
                return self.titleSources[s].TitlePlugin()
        return None

    def create_chapter_instance(self, domain, name="", number=-1):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):  
                return self.titleSources[s].ChapterPlugin(name=name, number=number)
        return None

    def get_plugin(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return self.titleSources[s].TitlePlugin
        return None

    def get_chapter_plugin(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return self.titleSources[s].ChapterPlugin
        return None

    def is_source_supported(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return True
        return False