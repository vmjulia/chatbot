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
            self.createSeparateGraph(graph.graph)
            self.dump()
        else:  
            self.compute_kappa()     

    def toUri(self, s, p ,o):
        s = URIRef(self.WD[re.sub("wd:", "", s)])
                    
        if re.search("ddis:", p):
                p = URIRef(self.DDIS[re.sub("ddis:", "", p)])
                print("ddis example", p)
        else:
                p = URIRef(self.WDT[re.sub("wdt:", "", p)])

        if re.search("wd:", o):
                o = URIRef(self.WD[re.sub("wd:", "", o)])
        elif re.search(r'(\d+-\d+-\d+)', o):
                print("date example before", o)
                o = Literal(o, datatype=XSD.date)
                print("date example after", o)
        else:
                o = Literal(o)
        return s, p, o
        
    def fromUri(self, s, p , o):
        #todo: finish all the cases
        if re.search("http://www.wikidata.org/entity/", s):
            s = "wd:"+ s[len("http://www.wikidata.org/entity/"):]
        if re.search("http://www.wikidata.org/entity/", o):
            o = "wd:"+ o[len("http://www.wikidata.org/entity/"):]
        if re.search("http://www.wikidata.org/prop/direct/", p):
            p = "wdt:"+p[len("http://www.wikidata.org/prop/direct/"):]         
        return s, p , o
    
    
    def createSeparateGraph(self, graph):
        self.crowd_graph  = rdflib.Graph()
        grouped = self.crowd_data.groupby('HITId')
        for hitId, group in grouped:
            hit = group.iloc[0]
            s, p, o = self.toUri( hit['Input1ID'],  hit['Input2ID'],  hit['Input3ID'])
            #if not (s, p, o) in graph:
            self.crowd_graph .add((s, p, o))

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
            #print("Fleiss Kappa:", task.multi_kappa())
            self.crowd_data.loc[self.crowd_data['HITTypeId'] == batchId, 'kappa'] = task.multi_kappa()

       
    def findAnswer(self, s, p, o):
        df = self.crowd_data
        crowd_answers = df.loc[(df['Input1ID'] == s) & (df["Input2ID"] == p) & (df["Input3ID"] == o)]
        #print(crowd_answers)
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
            #print(support_votes, reject_votes, round(kappa, 2))
            return support_votes, reject_votes, round(kappa, 2)
        
        
    def getAnswer(self, crowdAnswer, questionType, entities = None):
        agreementMax = 0
        chosentriple = [None, None, None]
        
        for ind, row in crowdAnswer.iterrows():
            print(row)
            s = row["Subject"]
            p = row["Predicate"]
            o = row["Object"]
            s_label = row["s_label"]
            p_label = row["p_label"]
            o_label = row["o_label"]
            s, p, o = self.fromUri(s, p ,o)
            
            res = self.findAnswer(str(o), str(p), str(s))
            if res == None:
                res = self.findAnswer(str(s), str(p), str(o))
                
            if res != None and res[0]>agreementMax:
                agreementMax = res[0]
                chosentriple = [s, p, o]
                chosentripleLabels = [s_label, p_label, o_label]
                            
        if res == None:
            return " Unfortunately (and unexpectidly), I do not have data about users opinion to compute kappa and so on for this quesiton."
        else:
            if questionType == "special":
                # return the answer, not entitiy in quesiton!
              print("how entity 0 is looking", entities[0])
              if chosentriple[0] == entities[0]:  
                return " According to the crowd, %s is the correct answer (I used maximum agreement as a metric). Inter-rater agreement is %s in this batch. According to the filtered crowdsource data %d out of %d think that the crowd statement is correct, while %d out of %d think that it is actually wrong. " %(chosentripleLabels[1], str(res[2]), res[0], res[0]+res[1], res[1], res[0]+res[1])
              else:
                  return " According to the crowd, %s  is the correct answer (I used maximum agreement as a metric). Inter-rater agreement is %s in this batch. According to the filtered crowdsource data %d out of %d think that the crowd statement is correct, while %d out of %d think that it is actually wrong. " %(chosentripleLabels[0], str(res[2]), res[0], res[0]+res[1], res[1], res[0]+res[1])
            else: # compare with the initial entities
                return " According to the crowd, it is True (I used maximum agreement as a metric). Inter-rater agreement is %s in this batch. According to the filtered crowdsource data %d out of %d think that the crowd statement is correct, while %d out of %d think that it is actually wrong. " %(str(res[2]), res[0], res[0]+res[1], res[1], res[0]+res[1])
        
if __name__ == '__main__':
    cs =  CrowdSource(False)
    s =  "wd:Q171300"
    p =  "wdt:P2142"
    o =  "267000000"
    res = cs.findAnswer(s, p, o)
    print(res)