import json
import os
import re
import time
import pandas as pd
from rdflib import Namespace
from graph import Graph


class MultimediaService:
    def __init__(self, graph):
        f = open('data/multimedia/images.json')
        self.images = json.load(f)
        self.types = ['behind_the_scenes', 'still_frame', 'publicity', 'event', 'poster', 'production_art', 'product', 'unknown', 'user_avatar']
        self.graph = graph
        
    # if a list of entities is given, iterate until some image is found and return. If no images are still found use wikipedia.
    # for movie type make classification task what the person wants to see: behind the scenes/poster etc.
    
    def getAnswer(self, entities):
        # first get the id, then get the image and return it
        return    
        
    
    def getImage(self, imdb_id, context = 'movie', image_type= None):
        id_key = 'movie'
        if(context == 'human'):
            id_key = 'cast'
            image_type = "poster"

            #first try to get poster
            for e in self.images:
                if imdb_id in e[id_key] and image_type == e['type']:
                    print(e)
                    return e['img']
                
            #if there was no poster just get smth 
            for e in self.images:
                if imdb_id in e[id_key]:
                    
                    return e['img']
        return ''
    
    # a function in case  imdb id did not work, then link to wikipedia image is provided
    def queryImage_from_Wikidata(self, id):
        sparql_query = """
            PREFIX wd: <http://www.wikidata.org/entity/> 
            PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
            SELECT ?item
            WHERE {
            wd:%s wdt:P18 ?item .
            }
            """ % (id)
        results = self.graph.graph.query(sparql_query)
        if results is None (len(results) == 0):
            return results
        return [ str(result.item) for result in results]
    
    
    # returns list of imdb id, if there are none -> list is empty
    def queryImage(self, id):
        res =   self.graph.graph.query('''
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
        
        SELECT ?imdb_id 
        WHERE {
            wd:%s wdt:P345 ?imdb_id .
        }
        ''' % (id))
        
        df = pd.DataFrame(res, columns=res.vars)
        print(df)
        if res is not None and (len(res) != 0):
            return [ str(result.imdb_id) for result in res]
        return res
    


if __name__ == '__main__':
    ms = MultimediaService()
    #res = ms.getImage("nm0000246", context= "human" )
    #print(res)
    g = Graph()  
    id = "Q2680"
    ms = MultimediaService(g)
    print( ms.queryImage(id))
    print( ms.queryImage_from_Wikidata(id))

    