import json
import os
import re
import time
import pandas as pd
from rdflib import Namespace


class MultimediaService:
    def __init__(self):
        f = open('data/multimedia/images.json')
        self.images = json.load(f)
        
        
    def getImage(self, imdb_id, context = 'movie', image_type= None):
        id_key = 'movie'
        if(context == 'human'):
            id_key = 'cast'
        for e in self.images:
            if imdb_id in e[id_key]:
                print(e['type'])
                return e['img']
        return ''


if __name__ == '__main__':
    ms = MultimediaService()
    res = ms.getImage("nm0000246", context= "human" )
    print(res)
    