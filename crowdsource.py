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

    def create_difference_graph(self, graph):
        self.crowd_graph  = rdflib.Graph()
        WD = Namespace('http://www.wikidata.org/entity/')
        WDT = Namespace('http://www.wikidata.org/prop/direct/')
        DDIS = Namespace('http://ddis.ch/atai/')
        grouped = self.crowd_data.groupby('HITId')
        for hitId, group in grouped:
            hit = group.iloc[0]
            s = URIRef(WD[re.sub("wd:", "", hit['Input1ID'])])
            
            p_value = hit['Input2ID']
            if re.search("ddis:", p_value):
                p = URIRef(DDIS[re.sub("ddis:", "", p_value)])
            else:
                p = URIRef(WDT[re.sub("wdt:", "", p_value)])

            o_value = hit['Input3ID']
            if re.search("wd:", o_value):
                o = URIRef(WD[re.sub("wd:", "", o_value)])
            elif re.search(r'(\d+-\d+-\d+)', o_value):
                o = Literal(o_value, datatype=XSD.date)
            else:
                o = Literal(o_value)
            if not (s, p, o) in graph:
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

       
    def find_answer(self, s, p, o):
        df = self.crowd_data
        crowd_answers = df.loc[(df['Input1ID'] == s) & (df["Input2ID"] == p) & (df["Input3ID"] == o)]
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
        
if __name__ == '__main__':
    cs =  CrowdSource(False)
    s =  "wd:Q4335275"
    p =  "wdt:P520"
    o =  "wd:Q52382294"
    res = cs.find_answer(s, p, o)
    print(res)