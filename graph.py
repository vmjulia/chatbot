import rdflib
import dill as pickle
from rdflib import Namespace
import pandas as pd
import constant
import numpy as np

class Graph:
    def __init__(self, createNew=False):
        
        self.properties = pd.read_csv("utildata/graph_properties_expanded.csv")
        self.entities = pd.read_csv("utildata/graph_entities.csv")
        self.movies = pd.read_csv("utildata/movie_entities.csv")["EntityLabel"].tolist()
        self.EmbeddingService = None
        
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
        #self.DDIS = Namespace('http://ddis.ch/atai/') # tags 

    def dump(self):
        with open('data/graph.pkl', 'wb') as file:
            pickle.dump(self.graph, file)            
    
    def querySpecial(self, graph,  predicate, entity):
       # graph = self.graph
        targets = []     
        entities = []       
        dir = []
        print("predicate", predicate)
        print("entity", entity)
        
        # in graph it is stored properly, we just store it wrongly actually
        if predicate == "ddis:indirectSubclassOf":
            predicate = "http://ddis.ch/atai/indirectSubclassOf"
        
        #find a matching predicate - todo, do it in the parser  
        # o is found, s is given          
        dir += [(s, p, o) for o, p, s in graph.triples((None, rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity))))]
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity)), rdflib.term.URIRef('%s'%predicate), None))]

        if predicate == self.WDT.P31 and False: #or re.search("type|class|parent|indirectSubclassOf|sub class", relation)s
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
                                        entities.append(o_label)                                                           
                                    
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
                    entities.append(o_label)                       

        print(dir)
        if len(dir)>0:
            df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
            df = df.drop_duplicates()
            print("resulting df",s, o, p, s_label, o_label, p_label)
            return df, entities
        return None, None
    
    #here important to query both graphs
    def queryPredicates(self, entity):
        graph = self.graph
        pred = []       
        dir = []
        
        #find a matching predicate - todo, do it in the parser  
        # o is found, s is given
        entity= self.entityToURI(entity)          
        dir += [(s, p, o) for o, p, s in graph.triples((None, None, ( rdflib.term.URIRef('%s' %entity))))]
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity)), None, None))]
                                
        if True:
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
                    pred.append(str(p_label))
        
        pred.append("indirect subclass of")    #add this to be sure
                
        graph = self.crowd_graph      
        dir = []          
        dir += [(s, p, o) for o, p, s in graph.triples((None, None, ( rdflib.term.URIRef('%s' %entity))))]
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity)), None, None))]
                                
        if True:
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
                    pred.append(str(p_label))
                    
        return set(pred)
    
    def queryEntities(self, predicate):
        graph = self.graph
        pred = []       
        dir = []
        if predicate == "ddis:indirectSubclassOf":
            predicate = "http://ddis.ch/atai/indirectSubclassOf"
        else:
            predicate= self.predicatToURI(predicate)   
        
        #find a matching predicate - todo, do it in the parser  
        # o is found, s is given          
        dir += [(s, p, o) for o, p, s in graph.triples((None, rdflib.term.URIRef('%s'%predicate),None))]
        dir += [(s, p, o) for s, p, o in graph.triples(( None, rdflib.term.URIRef('%s'%predicate), None))]
                                
        if True:
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
                    pred.append(str(s_label))
                    pred.append(str(o_label))
        
        pred.append("indirect subclass of")    #add this to be sure
                
        graph = self.crowd_graph      
        dir = []          
        dir += [(s, p, o) for o, p, s in graph.triples((None, rdflib.term.URIRef('%s'%predicate),None))]
        dir += [(s, p, o) for s, p, o in graph.triples(( None, rdflib.term.URIRef('%s'%predicate), None))]
                                
                                
        if True:
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
                    pred.append(str(s_label))
                    pred.append(str(o_label))
                    
        return set(pred)
    
    def queryGeneral(self, graph, entity1, entity2, predicate):
        # check if exactly this tuple is in the graph
       
        targets = []       
        dir = []      
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity1)), rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity2))))]
        dir += [(s, p, o) for o, p, s in graph.triples((( rdflib.term.URIRef('%s' %entity2)), rdflib.term.URIRef('%s'%predicate), ( rdflib.term.URIRef('%s' %entity1))))]

        for s, p, o in dir:
                    #print("difference between predicate and p", p, predicate)
                    if self.graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                        p_label = self.graph.value(p, self.RDFS.label)
                        o_label = self.graph.value(o, self.RDFS.label)
                        targets.append((s, o, p, s_label, o_label, p_label))

        df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
        #df = df.drop_duplicates().sort_values(by='Date', ascending=False, na_position='last').reset_index(drop=True)
        df = df.drop_duplicates()
        return df
    
    def queryGeneralCrowd(self, graph, entity1, entity2, predicate):
       # check if this tuple is partially there
        targets = []       
        dir = []      
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity1)), rdflib.term.URIRef('%s'%predicate), None))]
        dir += [(s, p, o) for s, p, o in graph.triples((( rdflib.term.URIRef('%s' %entity2)), rdflib.term.URIRef('%s'%predicate), None))]

        for s, p, o in dir:
                    #print("difference between predicate and p", p, predicate)
                    if self.graph.value(s, self.RDFS.label):
                        s_label = self.graph.value(s, self.RDFS.label)
                        p_label = self.graph.value(p, self.RDFS.label)
                        o_label = self.graph.value(o, self.RDFS.label)
                        targets.append((s, o, p, s_label, o_label, p_label))

        df = pd.DataFrame(targets, columns=['Subject', 'Object', 'Predicate', 'SubjectLabel', 'ObjectLabel', 'PredicateLabel'])
        df = df.drop_duplicates()
        return df
    
    def predicatToURI(self, p):
        uri = self.properties.loc[self.properties['PropertyLabel'] == p,'Property' ].values[0]
        return uri
    
    # returns string
    def entityToURI(self, e):
        uri = self.entities.loc[self.entities['EntityLabel'] == e,'Entity' ].values[0]
        return 'http://www.wikidata.org/entity/'+ uri
    
    # returns class instance
    def entityToURINamespace(self, e):
        entityCode = self.entities.loc[self.entities['EntityLabel'] == e,'Entity' ].values[0]
        return  self.WD[entityCode]
       
    # from class instance to Q bla bla
    def entityURINamespacetoCode(self, uri):
         uri = str(uri)
         res = uri[len('http://www.wikidata.org/entity/'):]
         return  res
     
    def fromUriStringToEntity(self, uri):
        if 'http://www.wikidata.org/entity/' in uri:
            res = uri[len('http://www.wikidata.org/entity/'):]
            res = "wd:"+res
            return  res
        return uri
     
    def fromUriStringToPredicate(self, uri):
        if  'http://www.wikidata.org/prop/direct/' in uri:
            res = uri[len('http://www.wikidata.org/prop/direct/'):]
            res = "wdt:"+res
            return  res
        return uri
    
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
        embed = None
        
        if len(matches)>=1:
             uri_entitiy_1 = self.entityToURI(matches[0])
        if len(matches)>=2:
             uri_entitiy_2 = self.entityToURI(matches[1])
             

        # todo: make it in a loop
        uri_predicate = self.predicatToURI(predicate[0])
            
        if questiontype == "general" and uri_predicate is not None and uri_entitiy_1 is not None and uri_entitiy_2 is not None:
            res_graph= self.queryGeneral(self.graph, uri_entitiy_1, uri_entitiy_2, uri_predicate )
            res_crowd = self.queryGeneralCrowd(self.crowd_graph, uri_entitiy_1, uri_entitiy_2, uri_predicate )
            
            if len(res_crowd) == 0:
                second = ""
            else:
                second = "This question was also asked to the crowd."
            
            if len(res_graph) == 0:
                return False, "The satement is wrong according to the initial knowledge graph. "+second, res_crowd
            else: 
                return True, "The satement is correct according to the initial knowledge graph. "+ second, res_crowd
            
        elif questiontype == "special":
            df, entities_graph = self.querySpecial(self.graph, uri_predicate, uri_entitiy_1)
            
            df_crowd, entities_crowd = self.querySpecial(self.crowd_graph, uri_predicate, uri_entitiy_1)
            answer = self.formulateAnswer(entities = entities_graph)
            if entities_crowd == None or len(entities_crowd) == 0:
                second = ""
            else:
                second = " This question was asked to the crowd. " 
                
                
            try:
                # find the predicate which is correct
                for p in reversed(predicate):
                    embed = self.EmbeddingService.getAnswer(uri_entitiy_1, self.predicatToURI(p))
                    if embed is not None and len(embed)>0:
                        embed = self.formulateAnswerEmbed(embed)
                        break
                    else: embed = None
            except:
                print("embed did not work")
                embed = None
            
            return entities_graph, answer + second, df_crowd, embed            
            
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
        
    def formulateAnswerEmbed(self, entities):

        if(entities == None or len(entities) == 0):
            return ""
        elif(len(entities) == 1):
            r = np.random.choice(constant.SINGLE_ANSWER_EMBED) +entities[-1]+ '.'
            return r
        elif(len(entities) > 1):
            text = np.random.choice(constant.MULTIPLE_ANSWER_EMBED)
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
    weird_entities = []
    weird_predicates = ["ddis:indirectSubclassOf"]
    for p in weird_predicates:
        w = graph.queryEntities(p)
        weird_entities.extend(w)
    weird_entities = list(set(weird_entities))
    print(weird_entities)
        
    
    
    exit()
    p = "director"
    e1 = "Star Wars"
    e2 = "Jan Dara"
    uri_predicate = graph.predicatToURI(p)
    uri_entitiy_1 = graph.entityToURI(e1)
    uri_entitiy_2 = graph.entityToURI(e2)
    df = graph.querySpecial(graph.graph, uri_entitiy_1, uri_predicate)
    print(df)
    #df = graph.queryGeneral(uri_entitiy_1, uri_entitiy_2, uri_predicate)
   # toUser = graph.formulateAnswer(entities = ["director", "director"])
