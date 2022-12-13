import numpy as np
from sklearn.metrics import pairwise_distances
import random
from embedding import EmbeddingService 
from graph import Graph
import random
import constant

class Recommender():
    
    def __init__(self, graph, embeddingService):
        self.graph = graph
        self.embeddingService =  embeddingService
        
    def getRecommendation(self, entities):
        same_dir = None
        same_g = None
        rest = None
        empty = True
       
        if entities is not None and len(entities)>0:
            entity = entities[0]
            res2 = self.findSimilarEmbeddings(entity)
                        
            if res2 is not None and len(res2)>1:
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                    rest = set(res2).difference(same_dir).difference(same_g)
            else:
                    res2 = random.sample(self.graph.movies, 100)
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                
            
            answer = ""
            if same_dir is not None and len(same_dir)>0:
                empty = False
                answer += answer+self.formulateAnswer(list(random.sample(same_dir, min(2, len(same_dir))))) + " They have the same director. "
            if same_g is not None and len(same_g)>0:
                empty = False
                answer += self.formulateAnswer(list(random.sample(same_g, min(2, len(same_g))))) + " They have different director yet quite same genre/style. "
            if rest is not None and len(rest)>0:
                empty = False
                answer += self.formulateAnswer(list(random.sample(rest, min(2, len(rest))))) + " This is something which you might also like.  "

        
        if empty and entities is not None and len(entities)>1:
            entity = entities[1]
            res2 = self.findSimilarEmbeddings(entity)
                        
            if res2 is not None and len(res2)>1:
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                    rest = set(res2).difference(same_dir).difference(same_g)
            else:
                    res2 = random.sample(self.graph.movies, 100)
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                
            
            answer = ""
            if same_dir is not None and len(same_dir)>0:
                empty = False
                answer += answer+self.formulateAnswer(list(random.sample(same_dir, min(2, len(same_dir))))) + " They have the same director. "
            if same_g is not None and len(same_g)>0:
                empty = False
                answer += self.formulateAnswer(list(random.sample(same_g, min(2, len(same_g))))) + " They have different director yet quite same genre/style. "
            if rest is not None and len(rest)>0:
                empty = False
                answer += self.formulateAnswer(list(random.sample(rest, min(2, len(rest))))) + " This is something which you might also like.  "
            return

        return answer

            
       
    def formulateAnswer(self, entities):
        if(len(entities) == 1):
            r = np.random.choice(constant.SINGLE_RECOMMENDER_ANSWER) +entities[-1]+ '.'
            return r
        elif(len(entities) > 1):
            text = np.random.choice(constant.MULTIPLE_RECOMMENDER_ANSWER)
            for i, e in enumerate(entities):
                if(i < len(entities) - 2):
                    text += e + ", "
                elif(i < len(entities) - 1):
                    text += e + " and " + entities[-1]+"." 
        return text
      
   # accepts label as input
    def findSimilarEmbeddings(self, entity_label):
        # form URI
        try:
            labels = []
            entity =  self.graph.entityToURINamespace(entity_label)
            entity = self.embeddingService.entity_emb[self.embeddingService.ent2id[entity]]       
            dist = pairwise_distances(entity.reshape(1, -1), self.embeddingService.entity_emb).reshape(-1)
            sim = dist.argsort()[0:10]
            # save that as entities URIs and labels
            sim = [self.embeddingService.id2ent[s] for s in sim]  
            labels =[self.embeddingService.ent2lbl[self.graph.entityURINamespacetoCode(s)] for s in sim]
            # remove our entity from the resulting list
            labels = list(set(labels).difference(set([entity_label])))
        except:
            return []  
        return labels
    
    # accepts label as input
    def check_directors(self, initial_entity, list_similar):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("director")
        print(" the query to the graph", initial_entity, director_predicate)
        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        
        same_dir = []
        if director_query is not None and len(director_query)>0:
            b = self.graph.entityToURI(str(director_query[0]))
            for a_label in list_similar:
                a =  self.graph.entityToURI(a_label)
                res = self.graph.queryGeneral(self.graph.graph, a, b, director_predicate)
                if res is not None and len(res)>0:
                    same_dir.append(a_label)
        return same_dir
                
    # accepts label as input
    def check_genres(self, initial_entity, list_similar):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("genre")
        print(" the query to the graph", initial_entity, director_predicate)
        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        
        same_genre= []
        if director_query is not None and len(director_query)>0:
            b = self.graph.entityToURI(str(director_query[0]))
            for a_label in list_similar:
                a =  self.graph.entityToURI(a_label)
                res = self.graph.queryGeneral(self.graph.graph, a, b, director_predicate)
                if res is not None and len(res)>0:
                    same_genre.append(a_label)
        return same_genre
        
    
if __name__ == '__main__':
    graph =  Graph(False)
    embed = EmbeddingService(graph)
    r = Recommender(graph,  embed)
    r.getRecommendation(['Star Wars Episode IX: The Rise of Skywalker'])
    #res2 = r.findSimilarEmbeddings('Star Wars Episode IX: The Rise of Skywalker')
    #r.check_genres('Star Wars Episode IX: The Rise of Skywalker', res2)
    
    
    # once the kind of question was determined, update the matched entities for media and recommender.
    # if type is media get longest overlap with human, if none than with movie
    # if  type is recommender get the longest overlap with movie, if non peak random
    # if those are equal to stored entities than all good, if not try both and choose smth 