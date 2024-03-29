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
    def __init__(self, graph):
        self.WD_uri = 'http://www.wikidata.org/entity/'
        self.WD = Namespace(self.WD_uri)
        self.WDT = Namespace('http://www.wikidata.org/prop/direct/')
        self.RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        #self.DDIS = Namespace('http://ddis.ch/atai/')
        self.graph = graph

        # load the embeddings
        self.entity_emb = np.load('data/ddis-graph-embeddings/entity_embeds.npy')
        self.relation_emb = np.load('data/ddis-graph-embeddings/relation_embeds.npy')
        # load the dictionaries
        with open('data/ddis-graph-embeddings/entity_ids.del', 'r') as ifile:
            self.ent2id = {rdflib.term.URIRef(ent): int(idx) for idx, ent in csv.reader(ifile, delimiter='\t')} #rdflib.term.URIRef('http://www.wikidata.org/entity/Q16883812'): 158894
            self.id2ent = {v: k for k, v in self.ent2id.items()}
        with open('data/ddis-graph-embeddings/relation_ids.del', 'r') as ifile:
            self.rel2id = {rdflib.term.URIRef(rel): int(idx) for idx, rel in csv.reader(ifile, delimiter='\t')} 
            self.id2rel = {v: k for k, v in self.rel2id.items()}
        self.ent2lbl = {row["Entity"]: str(row["EntityLabel"]) for id, row in self.graph.entities.iterrows()}
        self.lbl2ent = {lbl: ent for ent, lbl in self.ent2lbl.items()}
        print("EmbeddingService initialized")
    
    
    #always returns list of answers
    def getAnswer(self, s_uri, p_uri):
        cardinality = self.graph.getCardinality(s_uri, p_uri)
        s = self.graph.fromUriStringToEntity(s_uri)
        p = self.graph.fromUriStringToPredicate(p_uri)
        res = self.answer_general_question(s, p, cardinality)
        answer = []
        for r in res:
            code = self.graph.entityURINamespacetoCode(r)
            if code:
                entityCode = self.graph.entities.loc[self.graph.entities['Entity'] == code,'EntityLabel' ].values[0]
                answer.append(entityCode)
                
        return(answer)
               
        
        
    # returns list of the entities from the triple
    # if the len of the returned list is one it means that the relation is single
    def answer_general_question(self, s, p, cardinality):
        sub = self.WD[s[len("wd:"):]]
        if re.search("ddis:", p):
            pred = p
            return []
        else:
            pred = self.WDT[p[len("wdt:"):]]
       
        if sub in self.ent2id and pred in self.rel2id:
            
            input_id = self.ent2id[sub]
             # given head and rel find tail
            head = self.entity_emb[self.ent2id[sub]]
            pred = self.relation_emb[self.rel2id[pred]]
            
            # default values, so they are never none
            idx1 = []
            idx2 = []
            
            lhs = head + pred
            dist1 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist1.argsort()
            if most_likely is not None and len(most_likely)>0:
                if cardinality == "Single":
                    idx1 = most_likely[0]
                    idx1 = [idx1]
                    if input_id == idx1:
                        idx1 =[]
                        
                else:
                    idx1 = most_likely[:min(3, len(most_likely))]
                    for id in idx1:
                        if input_id == id:
                            idx1 =[]
            
            # given tail and rel find head
            lhs = head - pred
            dist2 = pairwise_distances(lhs.reshape(1, -1), self.entity_emb).reshape(-1)
            most_likely = dist2.argsort()
            if most_likely is not None and len(most_likely)>0:
                if cardinality == "Single":
                    idx2 = most_likely[0]
                    idx2 = [idx2]
                    if input_id == idx2:
                        idx2 =[]
                else:
                    idx2 =  most_likely[:min(3, len(most_likely))]
                    for id in idx2:
                        if input_id == id:
                            idx2 =[]
            
            if len(idx1) == 1 and len(idx2)==1: 
                if dist1[idx1[0]]<dist2[idx2[0]]:
                    return  [self.id2ent[idx1[0]]]
                else: 
                    return  [self.id2ent[idx2[0]]]
            
            else: 
                if len(idx2) == 0:
                    idx2 = idx1
                    
                if len(idx1) == 0:
                    idx1 = idx2
                    
                if len(idx2) == 0 or len(idx1) == 0:
                    return []
                    
 
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
            return ([])
            
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
    
    graph =  Graph(False)
    embed = EmbeddingService(graph)
   
    s = "wd:Q18665339"
    o = "wd:Q235347"
    p = "wdt:P1657"
    s_label = "NC-17"
    o_label = "Weathering with You"
    p_label = "MPAA film rating"
    
    
    uri_entity = graph.entityToURI(s_label)
    uri_predicate = graph.predicatToURI(p_label)
    res = graph.getCardinality(uri_entity, uri_predicate)
    prediction = embed.getAnswer("http://www.wikidata.org/entity/Q188718", "http://www.wikidata.org/prop/direct/P57")
    print("what this  method returns", prediction)
    
    #flag, prediction = embed.answer_special_question(s, p, o)
    #print(flag, prediction)
    