#!/usr/bin/python3
# -*- coding: utf-8 -*-

import importlib
import os, sys, re
import logging
from types import ModuleType

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

    def get_plugin_list(self):
        return list(self.titleSources.keys())

    def reload_plugin(self, module):
        try:
            if type( module ) == str:
                key_list = list(self.titleSources.keys())
                if module in key_list:
                    self.titleSources[module] = importlib.reload(self.titleSources[module])
                    logger.info("Plugin with name \"" + module + "\" successfully reloaded")
                    return 0
                else:
                    logger.error( "Plugin with name \"" + module + "\" does not exist in current list" )
            elif type(module) == ModuleType:
                for p in self.titleSources.keys():
                    if module == p:
                        self.titleSources[p] = importlib.reload(self.titleSources[p])
                        return 0
                logger.error( "Plugin with name \"" + module + "\" could not be found" )
                return 1
            else:
                logger.warning("reload_plugin:Passed in type other than module or string")
        except Exception:
            logger.exception("Failed to reload plugin " + module)
            return 1
        except:
            logger.Error("Failed to reload plugin " + module)
            return 1
            
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

    def get_plugin_by_domain(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return self.titleSources[s].TitlePlugin
        return None
    
    def get_plugin_by_name(self, name):
        if name in self.titleSources.keys():
            return self.titleSources[name]
        else:
            logger.warning( "Failed to find Plugin with name \"" + module + "\"" )
            return None

    def get_chapter_plugin(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return self.titleSources[s].ChapterPlugin
        logger.error("Failed to find chapter plugin that supports domain \"" + domain + "\"")
        return None

    def is_source_supported(self, domain):
        for s in self.titleSources.keys():
            if self.titleSources[s].TitlePlugin.is_domain_supported(domain):
                return True
        logger.error("Failed to find plugin that supports domain \"" + domain + "\"")
        return False