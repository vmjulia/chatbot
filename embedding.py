import csv
import os
import re

import numpy as np
import pandas as pd
import rdflib
from rdflib import Namespace
from sklearn.metrics import pairwise_distances
from graph import Graph

class EmbeddingService:
    def __init__(self):
        self.WD_uri = 'http://www.wikidata.org/entity/'
        self.WD = Namespace(self.WD_uri)
        self.WDT = Namespace('http://www.wikidata.org/prop/direct/')
        self.RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        self.DDIS = Namespace('http://ddis.ch/atai/')

        # load the embeddings
        dirname = os.path.dirname(__file__)
        self.entity_emb = np.load('data/ddis-graph-embeddings/entity_embeds.npy')
        self.relation_emb = np.load('data/ddis-graph-embeddings/relation_embeds.npy')
        

        # load the dictionaries
        with open('data/ddis-graph-embeddings/entity_ids.del', 'r') as ifile:
            self.ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')}
            self.id2ent = {v: k for k, v in self.ent2id.items()}
        with open('data/ddis-graph-embeddings/relation_ids.del', 'r') as ifile:
            self.rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')}
            self.id2rel = {v: k for k, v in self.rel2id.items()}
        #self.ent2lbl = {ent: str(lbl) for ent, lbl in graph.subject_objects(self.RDFS.label)}
        #self.lbl2ent = {lbl: ent for ent, lbl in self.ent2lbl.items()}

        # define entity type and predicate maps
        self.entity_type_map = {
            'TITLE': [self.WD.Q11424, self.WD.Q24856, self.WD.Q5398426, self.WD.Q7725310, self.WD.Q15416],
            'DIRECTOR': [self.WD.Q2526255, self.WD.Q3455803],
            'CHARACTER': [self.WD.Q95074, self.WD.Q15773347, self.WD.Q15632617],
            'ACTOR': [self.WD.Q33999, self.WD.Q10800557],
            'GENRE': [self.WD.Q483394]
        }
        self.entity_predicate_map = {
            'TITLE': self.WDT.P31,
            'DIRECTOR': self.WDT.P106,
            'CHARACTER': self.WDT.P31,
            'ACTOR': self.WDT.P106,
            'GENRE': self.WDT.P31
        }
        print("EmbeddingService initialized")
        
        
        
    # returns list of the entities from the triple
    # if the len of the returned list is one it means that the relation is single
    def answer_general_question(self, s, p, cardinality):
        sub = self.WD[s[len("wd:"):]]
        if re.search("ddis:", p):
            pred = self.DDIS[p[len("ddis:"):]]
        else:
            pred = self.WDT[p[len("wdt:"):]]
       # obj = self.WD[o[len("wd:"):]] if re.search("wd:", o) else o
       
        if sub in self.ent2id and pred in self.rel2id:
             # given head and rel find tail
            head = self.entity_emb[self.ent2id[sub]]
            pred = self.relation_emb[self.rel2id[pred]]
            
            lhs = head + pred
            dist1 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist1.argsort()
            if cardinality == "Single" or cardinality == "Not Found":
                idx1 = most_likely[0]
                idx1 = [idx1]
            else:
                idx1 = most_likely[:5]
            
            # given tail and rel find head
            lhs = head - pred
            dist2 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist2.argsort()
            if cardinality == "Single" or cardinality == "Not Found":
                idx2 = most_likely[0]
                idx2 = [idx2]
            else:
                idx2 = most_likely[:5]
            
            if len(idx1) == 1 and len(idx2)==1: 
                if dist1[idx1[0]]<dist2[idx2[0]]:
                    return  self.id2ent[idx1[0]]
                else: 
                    return  self.id2ent[idx2[0]]
            
            else: 
                if dist1[idx1[0]]<dist2[idx2[0]]:
                    res = []
                    for el in idx1:
                        res.append(self.id2ent[el])
                    return  res
                else: 
                    res = []
                    for el in idx2:
                        res.append(self.id2ent[el])
                    return  res
        else:
            return ("Unfortunately, seems I dont have this in my embeddings, could you try to rephrase, maybe then I can find....")
            
    def answer_special_question(self, s, p, o ):
        sub = self.WD[s[len("wd:"):]]
        if re.search("ddis:", p):
            pred = self.DDIS[p[len("ddis:"):]]
        else:
            pred = self.WDT[p[len("wdt:"):]]
        obj = self.WD[o[len("wd:"):]] if re.search("wd:", o) else o
       
        if sub in self.ent2id and pred in self.rel2id:
             # given head and rel find tail
            head_1 = self.entity_emb[self.ent2id[sub]]
            pred_1 = self.relation_emb[self.rel2id[pred]]
            lhs = head_1 + pred_1

            dist1 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist1.argsort()
            idx1 = most_likely[0]
            print(self.id2ent[idx1], dist1[idx1])
            
            # given tail and rel find head
            lhs = head_1 - pred_1
            dist2 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist2.argsort()
            idx2 = most_likely[0]
            
            if self.id2ent[idx1] == obj or self.id2ent[idx2] == obj:
                return True, "According to my embeddings data, it is correct"
            
            
        if obj in self.ent2id and pred in self.rel2id:
             
             # given head and rel find tail
            head = self.entity_emb[self.ent2id[obj]]
            pred = self.relation_emb[self.rel2id[pred]]
            lhs = head + pred

            dist1 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist1.argsort()
            idx1 = most_likely[0]
            print(self.id2ent[idx1], dist1[idx1])
            
            # given tail and rel find head
            lhs = head - pred
            dist2 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist2.argsort()
            idx2 = most_likely[0]
            
            if self.id2ent[idx1] == sub or self.id2ent[idx2] == sub:
                return True, "According to my embeddings data, it is correct"
            else:
                print(self.id2ent[idx1] , self.id2ent[idx2], obj )
                return False, "No, Thats wrong "
        else:
            print("heress")
            return False, "Unfortunately, seems I dont have this in my embeddings, could you try to rephrase, maybe then I can find...."       
        
if __name__ == '__main__':
    embed = EmbeddingService()
    graph =  Graph(False)
   
    s = "wd:Q18665339"
    o = "wd:Q235347"
    p = "wdt:P1657"
    s_label = "NC-17"
    o_label = "Weathering with You"
    p_label = "MPAA film rating"
    
    
    uri_entity = graph.entityToURI(s_label)
    uri_predicate = graph.predicatToURI(p_label)
    res = graph.getCardinality(uri_entity, uri_predicate)
    prediction = embed.answer_general_question(s, p, res)
    print("what this  method returns", prediction)
    
    #flag, prediction = embed.answer_special_question(s, p, o)
    #print(flag, prediction)
    