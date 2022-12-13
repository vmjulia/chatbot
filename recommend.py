import numpy as np
import csv
import rdflib
import pandas as pd
from sklearn.metrics import pairwise_distances
import random
from embedding import EmbeddingService 
from graph import Graph

class Recommender():
    
    def __init__(self, graph, embeddingService):
        self.graph = graph
        self.RDFS = rdflib.namespace.RDFS
        self.WD = rdflib.Namespace('http://www.wikidata.org/entity/')
        self.embeddingService =  embeddingService
        
        
    def findSimilarEmbeddings(self, matches):
        entity =  self.graph.entityToURI(matches[0])
        entity  = self.WD[entity[len("wd:"):]]  
        entity = self.embeddingService.entity_emb[self.embeddingService.ent2id[entity]]
        
        dist = pairwise_distances(entity.reshape(1, -1), self.embeddingService.entity_emb).reshape(-1)
        sim = dist.argsort()[1:20]        
        return sim
    
    # peak 20 most similar from embeddings and select same genre and or same director
    # if this returns none then just same genre and or director actor ect
    
if __name__ == '__main__':
    embed = EmbeddingService()
    graph =  Graph(False)
    r = Recommender(graph,  embed)
    matches = ["wd:Q235347"]
    res = r.findSimilarEmbeddings(matches)
    print(res)