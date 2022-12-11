import pandas as pd
import os
from rdflib import Namespace, URIRef, Literal, XSD
import rdflib
import re
from graph import Graph
import pickle
from nltk.metrics import agreement


class CrowdSource:
    def __init__(self, createNew = False):
        self.WD = Namespace('http://www.wikidata.org/entity/')
        self.WDT = Namespace('http://www.wikidata.org/prop/direct/')
        self.DDIS = Namespace('http://ddis.ch/atai/')
        self.crowd_graph = None
        self.crowd_data = pd.read_csv('data/crowd_data.tsv', sep='\t', header=0)
        if createNew:
            self.compute_kappa()
            graph =  Graph(False)          
            self.create_difference_graph(graph.graph)
            self.dump()
        else:  
            self.compute_kappa()     
            #with open('data/crowd_graph.pkl', 'rb') as file:
            #    self.crowd_graph = pickle.load(file)

    def toUri(self, s, p ,o):
        s = URIRef(self.WD[re.sub("wd:", "", s)])
            
            
        if re.search("ddis:", p):
                p = URIRef(self.DDIS[re.sub("ddis:", "", p)])
        else:
                p = URIRef(self.WDT[re.sub("wdt:", "", p)])

        if re.search("wd:", o):
                o = URIRef(self.WD[re.sub("wd:", "", o)])
        elif re.search(r'(\d+-\d+-\d+)', o):
                o = Literal(o, datatype=XSD.date)
        else:
                o = Literal(o)
        return s, p, o
        
    def fromUri(self, s, p , o):
        #todo: finish all the cases
        if re.search("http://www.wikidata.org/entity/", s):
            s = s[len("http://www.wikidata.org/entity/"):]
        if re.search("http://www.wikidata.org/entity/", o):
            o = o[len("http://www.wikidata.org/entity/"):]
        if re.search("http://www.wikidata.org/prop/direct/", p):
            p = p[len("http://www.wikidata.org/prop/direct/"):]         
        return s, p , o
    
    
    def create_difference_graph(self, graph):
        self.crowd_graph  = rdflib.Graph()
        WD = Namespace('http://www.wikidata.org/entity/')
        WDT = Namespace('http://www.wikidata.org/prop/direct/')
        DDIS = Namespace('http://ddis.ch/atai/')
        grouped = self.crowd_data.groupby('HITId')
        for hitId, group in grouped:
            hit = group.iloc[0]
            s, p, o = self.toUri( hit['Input1ID'],  hit['Input2ID'],  hit['Input3ID'])
            #if not (s, p, o) in graph:
            self.crowd_graph .add((s, p, o))
            print("added", s, p , o)

    def dump(self, ):
        with open('data/crowd_graph.pkl', 'wb') as file:
            pickle.dump( self.crowd_graph , file)            
    
    def compute_kappa(self):
        batches = self.crowd_data.groupby('HITTypeId')
        for batchId, batch in batches:
            data = []
            grouped = batch.groupby('HITId')
            for hitId, group in grouped:
                index = 0
                for idx, row in group.iterrows():
                    index += 1
                    data.append((f"Worker_{index}", str(hitId), row['AnswerID']))
            task = agreement.AnnotationTask(data=data)
            print("Fleiss Kappa:", task.multi_kappa())
            self.crowd_data.loc[self.crowd_data['HITTypeId'] == batchId, 'kappa'] = task.multi_kappa()

       
    def findAnswer(self, s, p, o):
        df = self.crowd_data
        crowd_answers = df.loc[(df['Input1ID'] == s) & (df["Input2ID"] == p) & (df["Input3ID"] == o)]
        print(crowd_answers)
        if crowd_answers.empty:
            return None
        else:
            kappa = crowd_answers['kappa'].iloc[0]
            votes = crowd_answers['AnswerLabel'].value_counts().to_frame('count').reset_index()
            if votes.loc[votes['index'] == 'CORRECT', 'count'].values:
                support_votes = votes.loc[votes['index'] == 'CORRECT', 'count'].values[0]
            else:
                support_votes = 0

            if votes.loc[votes['index'] == 'INCORRECT', 'count'].values:
                reject_votes = votes.loc[votes['index'] == 'INCORRECT', 'count'].values[0]
            else:
                reject_votes = 0
            return support_votes, reject_votes, round(kappa, 2)
        
        
    def getAnswer(self, crowdAnswer):
        print("start crowd")
        s = crowdAnswer.loc[0,"Subject"]
        o = crowdAnswer.loc[0,"Object"]
        p = crowdAnswer.loc[0, "Predicate"]
        s, p,  o = self.fromUri(s, p ,o)
        print("start crowd2", s, p , o)
        return self.findAnswer(o, p, s)
        
if __name__ == '__main__':
    cs =  CrowdSource(True)
    s =  "wd:Q1288004"
    p =  "wdt:P520"
    o =  "wd:Q52382294"
    res = cs.findAnswer(s, p, o)
    print(res)