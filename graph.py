import os
import re
import rdflib
import dill as pickle
from rdflib import Namespace, URIRef
import pandas as pd

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
        self.columns = ['Subject', 'SubjectLabel', 'Relation', 'RelationLabel', 'Object', 'ObjectLabel', 'Date']

    def dump(self):
        dirname = os.path.dirname(__file__)
        with open('data/graph.pkl', 'wb') as file:
            pickle.dump(self.graph, file)
            
    def format_predicate(self, p):
        if re.search(self.DDIS, p):
            p_uri = re.sub(self.DDIS, "ddis:", p.toPython())
        else:
            p_uri = re.sub(self.WDT, "wdt:", p.toPython())
        p_label = self.graph.value(p, self.RDFS.label).toPython() if self.graph.value(p, self.RDFS.label) else p_uri
        return p_uri, p_label
    
    def format_subject(self, s):
        s_uri = re.sub(self.WD, "wd:", s.toPython())
        s_label = self.graph.value(s, self.RDFS.label).toPython() if self.graph.value(s, self.RDFS.label) else s_uri
        return s_uri, s_label
    
    def format_object(self, o):
        if isinstance(o, URIRef):
            o_uri = re.sub(self.WD, "wd:", o.toPython())
            o_label = self.graph.value(o, self.RDFS.label).toPython() if self.graph.value(o, self.RDFS.label) else o_uri
        else:
            o_uri = o.toPython()
            o_label = o.toPython()
        return str(o_uri), str(o_label)
    
    def query_wh(self, predicates, entities):
        graph = self.graph
      
        targets = []
        
        dir1 = []
        dir2 = []
        for i in len(entities):
            match = entities[i]
            predicate = predicates[i] 
            #find a matching predicate - todo, do it in the parser            
            dir1 += [(s, p, o) for s, p, o in graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %match))))]
            dir2 += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %match)), rdflib.term.URIRef('%s'%predicate), None))]

            if predicate == self.WDT.P31 : #or re.search("type|class|parent|indirectSubclassOf|sub class", relation)s
                for s, p, o in dir1:
                    if graph.value(s, self.RDFS.label):
                        s_uri, s_label = self.format_subject(s)
                        p_uri, p_label = self.format_predicate(p)
                        o_uri, o_label = self.format_object(o)
                        targets.append((s_uri, s_label,
                                        p_uri, p_label,
                                        o_uri, o_label,
                                        graph.value(s, self.WDT.P577)))
            else:
                for s, p, o in dir1 + dir2:
                    if graph.value(s, self.RDFS.label):
                        s_uri, s_label = self.format_subject(s)
                        p_uri, p_label = self.format_predicate(p)
                        o_uri, o_label = self.format_object(o)
                        targets.append((s_uri, s_label,
                                        p_uri, p_label,
                                        o_uri, o_label,
                                        graph.value(s, self.WDT.P577)))

        df = pd.DataFrame(targets, columns=self.columns)
        df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
        print(df)
        print(df[:30])
        return df[:30]
    
    def predicatToURI(self, p):
        uri = self.properties.loc[self.properties['PropertyLabel'] == p,'Property' ].values[0]
        return uri
    
    def entityToURI(self, e):
        uri = self.entities.loc[self.entities['EntityLabel'] == e,'Entity' ].values[0]
        return 'http://www.wikidata.org/entity/'+ uri
    
    
    
if __name__ == '__main__':
    #graph1 = Graph(True)
    #graph1.dump()
    graph = Graph(False)
    p = "cast member"
    e = "Joan Cusack"
    uri_predicate = graph.predicatToURI(p)
    uri_entitiy = graph.entityToURI(e)
    query = graph.query_wh([uri_predicate], [uri_entitiy])
    print(uri_predicate, uri_entitiy )