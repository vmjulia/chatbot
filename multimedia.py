import json
import os
import re
import time
import pandas as pd
from rdflib import Namespace
from graph import Graph
import rdflib


class MultimediaService:
    def __init__(self, graph):
        f = open('data/multimedia/images.json')
        self.images = json.load(f)
        self.types = ['behind_the_scenes', 'still_frame', 'publicity', 'event', 'poster', 'production_art', 'product', 'unknown', 'user_avatar']
        self.graph = graph
        
    # if a list of entities is given, iterate until some image is found and return. If no images are still found use wikipedia.
    # for movie type make classification task what the person wants to see: behind the scenes/poster etc.
    
    def getAnswer(self, entities):

        id = self.queryImage(entities[0])
        if id is None or len(id) == 0:
            answer = "there is no picture unfurtunately"
            res = self.queryImage_from_Wikidata(id)
            if res is not None:
                answer = answer + " But I found one in wikidata, could you have a look" + res
            
        else:
             answer = "image:"+self.getImage(id[0], "person")
        return  answer  
        
    
    def getImage(self, imdb_id, context = 'movie', image_type= None):
        id_key = 'movie'
        if(context == 'person'):
            id_key = 'cast'
            image_type = "poster"

            #first try to get poster
            for e in self.images:
                if imdb_id in e[id_key] and image_type == e['type']:
                    return e['img']
                
            #if there was no poster just get smth 
            for e in self.images:
                if imdb_id in e[id_key]:
                    return e['img']
                    
        else:
            id_key = 'cast'
            if image_type is None:
                image_type = "still_frame"

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
    #TODO:fix
    def queryImage_from_Wikidata(self, id):
        dir = []
        predicate = self.graph.predicatToURI("image")
        entity = self.graph.entityToURI(id)
        #dir += [s for o, p, s in self.graph.graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity))))]
        dir += [o for s, p, o in self.graph.graph.triples((( rdflib.term.URIRef('%s' %entity)), rdflib.term.URIRef('%s'%predicate), None))]
        return [ str(result) for result in dir]
    
    # returns list of imdb id, if there are none -> list is empty
    def queryImage(self, id):
        dir = []
        predicate = self.graph.predicatToURI("IMDb ID")
        entity = self.graph.entityToURI(id)
        #dir += [s for o, p, s in self.graph.graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity))))]
        dir += [o for s, p, o in self.graph.graph.triples((( rdflib.term.URIRef('%s' %entity)), rdflib.term.URIRef('%s'%predicate), None))]
        return [ str(result) for result in dir]
    

if __name__ == '__main__':
    #res = ms.getImage("nm0000246", context= "person" )
    #print(res)
    g = Graph()  
    id = "Q2680"
    ms = MultimediaService(g)
    res = ms.queryImage_from_Wikidata(id)
    id = ms.queryImage(id)
    if id is None or len(id) == 0:
        answer = "there is no picture unfurtunately"
        res = ms.queryImage_from_Wikidata(id)
        if res is not None:
            answer = answer + " But I found one in wikidata, could you have a look" + res
            
    else:
        res = ms.getImage(id[0], "person")
        print(res)
    #print( ms.queryImage_from_Wikidata(id))

    