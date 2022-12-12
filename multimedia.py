import json
import os
import re
import time
import pandas as pd
from rdflib import Namespace
from graph import Graph


class MultimediaService:
    def __init__(self):
        f = open('data/multimedia/images.json')
        self.images = json.load(f)
        self.types = ['behind_the_scenes', 'still_frame', 'publicity', 'event', 'poster', 'production_art', 'product', 'unknown', 'user_avatar']
        
        
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
    
    def queryImage(self, id, graph):
        sparql_query = """
            PREFIX wd: <http://www.wikidata.org/entity/> 
            PREFIX wdt: <http://www.wikidata.org/prop/direct/> 
            SELECT ?item
            WHERE {
            wd:%s wdt:P18 ?item .
            }
            """ % (id)
        results = graph.query(sparql_query)
        if(len(results) == 0):
            return results
        return [str(result.item) for result in results]
    


if __name__ == '__main__':
    ms = MultimediaService()
    #res = ms.getImage("nm0000246", context= "human" )
    #print(res)
    g = Graph()  
    id = 2680
    print(ms.queryImage(id, g.graph))
    