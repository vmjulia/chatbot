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
            with open('data/crowd_graph.pkl', 'rb') as file:
                self.crowd_graph = pickle.load(file)
                
        self.WD = Namespace('http://www.wikidata.org/entity/') # entities
        self.WDT = Namespace('http://www.wikidata.org/prop/direct/') # predicate, relation
        self.RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#') # label
        self.DDIS = Namespace('http://ddis.ch/atai/') # tags 

    def dump(self):
        with open('data/graph.pkl', 'wb') as file:
            pickle.dump(self.graph, file)            
    
    def querySpecial(self, graph,  predicate, entity):
       # graph = self.graph
        targets = []     
        entities = []       
        dir = []
        
        #find a matching predicate - todo, do it in the parser  
        # s is found, o is given          
        dir += [(s, p, o) for s, p, o in graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity))))]
        dir += [(s, p, o) for o, p, s in graph.triples((( rdflib.term.URIRef('%s' %entity)), rdflib.term.URIRef('%s'%predicate), None))]

        if predicate == self.WDT.P31 : #or re.search("type|class|parent|indirectSubclassOf|sub class", relation)s
            for s, p, o in dir:
                if self.graph.value(s, self.RDFS.label):
                                    for s, p, o in dir:
                                        if self.graph.value(s, self.RDFS.label):
                                            s_label = self.graph.value(s, self.RDFS.label)
                                        else:
                                            s_label = s
                                        if self.graph.value(o, self.RDFS.label):
                                            o_label = self.graph.value(o, self.RDFS.label)
                                        else:
                                            o_label = o
                                        if self.graph.value(p, self.RDFS.label):
                                            p_label = self.graph.value(p, self.RDFS.label)
                                        else:
                                            p_label = p    
                                        targets.append((s, o, p, s_label, o_label, p_label))
                                        entities.append(s_label)                                                           
                                    
        else:
                for s, p, o in dir:
                    if self.graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                    else:
                        s_label = s
                    if self.graph.value(o, self.RDFS.label):
                        o_label = self.graph.value(o, self.RDFS.label)
                    else:
                        o_label = o
                    if self.graph.value(p, self.RDFS.label):
                        p_label = self.graph.value(p, self.RDFS.label)
                    else:
                        p_label = p    
                    targets.append((s, o, p, s_label, o_label, p_label))
                    entities.append(s_label)                       

        print(dir)
        if len(dir)>0:
            df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
            #df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
            df = df.drop_duplicates()
            print("resulting df",s, o, p, s_label, o_label, p_label)
            return df, entities
        return None, None
    
    def queryGeneral(self, graph, entity1, entity2, predicate):
       
        #graph = self.graph
        targets = []       
        dir = []      
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity1)), rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity2))))]
        dir += [(s, p, o) for o, p, s in graph.triples((( rdflib.term.URIRef('%s' %entity2)), rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity1))))]

        for s, p, o in dir:
                    #print("difference between predicate and p", p, predicate)
                    if graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                        p_label = self.graph.value(p, self.RDFS.label)
                        o_label = self.graph.value(o, self.RDFS.label)
                        targets.append((s, o, p, s_label, o_label, p_label))

        df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
        #df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
        df = df.drop_duplicates()
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
            r = np.random.choice(constant.SINGLE_ANSWER) +entities[-1]+ '.'
            return r
        elif(len(entities) > 1):
            text = np.random.choice(constant.MULTIPLE_ANSWER)
            for i, e in enumerate(entities):
                if(i < len(entities) - 2):
                    text += e + ", "
                elif(i < len(entities) - 1):
                    text += e + " and " + entities[-1]+"." 
        return text
    
    def getAnswer(self, questiontype, predicate, types, matches):
        uri_entitiy_1 = None
        uri_entitiy_2 = None
        uri_predicate = None
        
        if len(matches)>=1:
             uri_entitiy_1 = self.entityToURI(matches[0])
        if len(matches)>=2:
             uri_entitiy_2 = self.entityToURI(matches[1])
             

        # todo: make it in a loop
        uri_predicate = self.predicatToURI(predicate[0])
            
        if questiontype == "general" and uri_predicate is not None and uri_entitiy_1 is not None and uri_entitiy_2 is not None:
            res_graph= self.queryGeneral(self.graph, uri_entitiy_1, uri_entitiy_2, uri_predicate )
            res_crowd= self.queryGeneral(self.crowd_graph, uri_entitiy_1, uri_entitiy_2, uri_predicate )
            
            if len(res_crowd) == 0:
                second = ""
            else:
                second = "This question also asked to the crowd."
            
            if len(res_graph) == 0:
                return False, "The satement is wrong according to the initial knowledge graph. "+second, res_crowd
            else: 
                return True, "The satement is correct according to the initial knowledge graph. "+ second, res_crowd
            
        elif questiontype == "special":
            df, entities_graph = self.querySpecial(self.graph, uri_predicate, uri_entitiy_1)
            df_crowd, entities_crowd = self.querySpecial(self.crowd_graph, uri_predicate, uri_entitiy_1)
            answer = self.formulateAnswer(entities = entities_graph)
            if len(entities_crowd) == 0:
                second = ""
            else:
                second = " This question was asked to the crowd. The answer %s was used in the crowd asking." %entities_crowd[0]
            return entities_graph, answer + second, df_crowd            
            
    def getCardinality(self, entity1, predicate):
        graph = self.graph
        dir = []
        dir += [(s, p, o) for s, p, o in graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity1))))]
        dir += [(s, p, o) for o, p, s in graph.triples((( rdflib.term.URIRef('%s' %entity1)), rdflib.term.URIRef('%s'%predicate), None))]
        if len(dir) == 0:
            return "Not Found"
        if len(dir) ==1:
            return "Single"
        else:
            return "Multiple"

        
    
if __name__ == '__main__':
    #graph1 = Graph(True)
    #graph1.dump()
    
    graph = Graph(False)
    p = "director"
    e1 = "Weathering with You"
    e2 = "Jan Dara"
    uri_predicate = graph.predicatToURI(p)
    uri_entitiy_1 = graph.entityToURI(e1)
    uri_entitiy_2 = graph.entityToURI(e2)
    df = graph.queryGeneral(uri_entitiy_1, uri_entitiy_2, uri_predicate)
    toUser = graph.formulateAnswer(entities = ["director", "director"])
