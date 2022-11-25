import os
import re
import rdflib
import dill as pickle
from rdflib import Namespace, URIRef

class Graph:
    def __init__(self, createNew):
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
        dirname = os.path.dirname(__file__)
        with open('data/graph.pkl', 'wb') as file:
            pickle.dump(self.graph, file)
            
if __name__ == '__main__':
    graph1 = Graph(True)
    graph1.dump()
    graph2 = Graph(False)