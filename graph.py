import os
import re
import rdflib
import dill as pickle
from rdflib import Namespace, URIRef
import pandas as pd
import constant
import numpy as np

class Graph:
    def __init__(self, createNew=False):
        
        self.properties = pd.read_csv("utildata/graph_properties_expanded.csv")
        self.entities = pd.read_csv("utildata/graph_entities.csv")
        
        if createNew:
            self.graph = rdflib.Graph()
            self.graph.parse('data/14_graph.nt', format='turtle')
            self.dump()
        else:       
            with open('data/graph.pkl', 'rb') as file:
                self.graph = pickle.load(file)
        self.WD = Namespace('http://www.wikidata.org/entity/') # entities
        self.WDT = Namespace('http://www.wikidata.org/prop/direct/') # predicate, relation
        self.RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#') # label
        self.DDIS = Namespace('http://ddis.ch/atai/') # tags 

    def dump(self):
        with open('data/graph.pkl', 'wb') as file:
            pickle.dump(self.graph, file)            
    
    def query_wh(self, predicates, entities):
        graph = self.graph
        targets = []       
        dir1 = []
        dir2 = []
        for i in range(len(entities)):
            match = entities[i]
            predicate = predicates[i] 
            #find a matching predicate - todo, do it in the parser            
            dir1 += [(s, p, o) for s, p, o in graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %match))))]
            dir2 += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %match)), rdflib.term.URIRef('%s'%predicate), None))]

            if predicate == self.WDT.P31 : #or re.search("type|class|parent|indirectSubclassOf|sub class", relation)s
                        for s, p, o in dir1 + dir2:
                                if graph.value(s, self.RDFS.label):
                                    s_label = self.graph.value(s, self.RDFS.label)
                                    p_label = self.graph.value(p, self.RDFS.label)
                                    o_label = self.graph.value(o, self.RDFS.label) 
                                    targets.append((s, o, p, s_label, o_label, p_label))                                     
                                    
            else:
                for s, p, o in dir1 + dir2:
                    #print("difference between predicate and p", p, predicate)
                    if graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                        p_label = self.graph.value(p, self.RDFS.label)
                        o_label = self.graph.value(o, self.RDFS.label)
                        targets.append((s, o, p, s_label, o_label, p_label))

        df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
        #df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
        df = df.drop_duplicates()
        #print(df)
        return df
    
    def query_yes_no(self, entity1, entity2):
       
        graph = self.graph
        targets = []       
        dir = []      
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity1)), None, ( rdflib.term.URIRef('%s' %entity2))))]
        dir += [(s, p, o) for o, p, s in graph.triples((( rdflib.term.URIRef('%s' %entity2)), None, ( rdflib.term.URIRef('%s' %entity1))))]

        for s, p, o in dir:
                    #print("difference between predicate and p", p, predicate)
                    if graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                        p_label = self.graph.value(p, self.RDFS.label)
                        o_label = self.graph.value(o, self.RDFS.label)
                        #print("subject", s_label)
                        #print("object", o_label)
                        #print("predicate", p_label)
                        targets.append((s, o, p, s_label, o_label, p_label))

        df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
        #df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
        df = df.drop_duplicates()
        #print(df)
        return df
    
    def predicatToURI(self, p):
        uri = self.properties.loc[self.properties['PropertyLabel'] == p,'Property' ].values[0]
        return uri
    
    def entityToURI(self, e):
        uri = self.entities.loc[self.entities['EntityLabel'] == e,'Entity' ].values[0]
        return 'http://www.wikidata.org/entity/'+ uri
    
    def formulateAnswer(self, entities):
        if(entities == None or len(entities) == 0):
            return np.random.choice(constant.DID_NOT_FIND_ANSWER)
        elif(len(entities) == 1):
            return np.random.choice(constant.SINGLE_ANSWER)+entities[-1] +'.'
        elif(len(entities) > 1):
            text = np.random.choice(constant.MULTIPLE_ANSWER)
            for i, e in enumerate(entities):
                if(i < len(entities) - 2):
                    text += e + ", "
                elif(i < len(entities) - 1):
                    text += e + " and " + entities[-1]+"." 
        return text
    
    
if __name__ == '__main__':
    #graph1 = Graph(True)
    #graph1.dump()
    
    graph = Graph(False)
    p = "director"
    e1 = "Nonzee Nimibutr"
    e2 = "Jan Dara"
    #uri_predicate = graph.predicatToURI(p)
    #uri_entitiy_1 = graph.entityToURI(e1)
    #uri_entitiy_2 = graph.entityToURI(e2)
    #df = graph.query_yes_no(uri_entitiy_1, uri_entitiy_2)
    toUser = graph.formulateAnswer(entities = ["director", "director"])
    print(toUser)