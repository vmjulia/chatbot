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
        
        
   # accepts label as input
    def findSimilarEmbeddings(self, entity):
        # form URI
        entity =  self.graph.entityToURINamespace(entity)
        entity = self.embeddingService.entity_emb[self.embeddingService.ent2id[entity]]       
        dist = pairwise_distances(entity.reshape(1, -1), self.embeddingService.entity_emb).reshape(-1)
        sim = dist.argsort()[1:10]
        # save that as entities URIs and labels
        sim = [self.embeddingService.id2ent[s] for s in sim]  
        labels =[self.embeddingService.ent2lbl[self.graph.entityURINamespacetoCode(s)] for s in sim]  
        return sim, labels
    
    # accepts label as input
    def check_directors(self, initial_entity, list_similar):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("director")
        director_query = self.graph.querySpecial(self.graph.graph, initial_entity, director_predicate )
        print("the director of the given movie is ", director_query)
    
if __name__ == '__main__':
    graph =  Graph(False)
    embed = EmbeddingService(graph)
    r = Recommender(graph,  embed)
    res1, res2 = r.findSimilarEmbeddings('Star Wars')
    r.check_directors('Star Wars', res2)
    
    
    # once the kind of question was determined, update the matched entities for media and recommender.
    # if type is media get longest overlap with human, if none than with movie
    # if  type is recommender get the longest overlap with movie, if non peak random
    # if those are equal to stored entities than all good, if not try both and choose smth 