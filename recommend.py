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
        directors = []
        genres = []
        times  = []
        time_min = None
        time_max = None
        inter = None
        producers = []
        if entities is not None and len(entities)>0:
            for entity in entities:
                res = self.queryDirector(entity)
                if res is not None and len(res)>0:
                    for r in res:
                        directors.append(r)
                        
                res = self.queryTime(entity)
                if res is not None and len(res)>0:
                    for r in res:
                        times.append(int(str(r)[0:4]))
                res = self.queryGenre(entity)
                if res is not None and len(res)>0:
                    for r in res:
                        genres.append(r)
                        
                res = self.queryProducer(entity)
                if res is not None and len(res)>0:
                    for r in res:
                        producers.append(r)
                        
                        
        if directors is not None and len(directors)>0:
            director  = max(set(directors), key=directors.count)
        else:
            director = None
        if genres is not None and len(genres)>0:
           genre  = max(set(genres), key=genres.count)
        else:
            genre = None
            
        if times is not None and len(times)>0:
            time_min  = min(set(times))
            time_max  = max(set(times))
      
        print(director, genre, time_min, time_max)
        director_predicate = self.graph.predicatToURI("director")
        genre_predicate = self.graph.predicatToURI("genre")
        director_query=[] 
        genre_query = []
        
        if director is not None:
            smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, self.graph.entityToURI(str(director)))
        if genre is not None:
            smth, genre_query = self.graph.querySpecial(self.graph.graph, genre_predicate, self.graph.entityToURI(str(genre)))
          
        inter = set(director_query).intersection(set(genre_query))
        if inter is None or len(inter)== 0:
            inter = set(genre_query)
        if inter is None or len(inter)== 0:
            inter = set(director_query)
            
        inter2 = []
        for movie in inter:
            inter2.append(str(movie))
            
        
        inter = set(inter2).intersection(set(self.graph.entities["EntityLabel"]))
        
        final = []
        # if there are too many, reduce by time
        if inter is not None and len(inter)>5: # TODO: change to 5
            print("reducing number of them")
            # if we have time information use it
            if time_min is not None and time_max is not None:
                for movie in inter:
                    res = self.queryTime(entity)
                    if res is not None and len(res)>0:
                        res = res[0]
                        res = int(str(res)[0:4])
                        if (res >=time_min -4) and (res<=time_max+4):
                            final.append(str(movie))
                            
            # if there was no time info  or smth didnt work, just take first 4-5
            count = 0          
            if len(final) == 0:
                for movie in inter:
                    count +=1
                    final.append(str(movie))
                    if count >=5:
                        break

        elif inter is not None:
            for movie in inter:
                final.append(str(movie))                    
        final = set(final) - set(entities)
        print("the final recommentations !!!!!!!!!", final)  
        if final is not None and len(final)>0:
            return self.formulateAnswer(list(final))
            
        else:
            return self.getRecommendationOld(entities)

            
    # accepts label as input
    def queryDirector(self, initial_entity):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("director")
       
        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        return director_query
    
    def queryProducer(self, initial_entity):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("executive producer")

        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        return director_query

    # accepts label as input
    def queryTime(self, initial_entity):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("publication date")

        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        return director_query
    
    def queryGenre(self, initial_entity):
        # form URI
        initial_entity =  self.graph.entityToURI(initial_entity)
        director_predicate = self.graph.predicatToURI("genre")

        smth, director_query = self.graph.querySpecial(self.graph.graph, director_predicate, initial_entity)
        return director_query
            
        
    def getRecommendationOld(self, entities):
        same_dir = None
        same_g = None
        rest = None
        empty = True
       
        if entities is not None and len(entities)>0:
            entity = entities[0]
            res2 = self.findSimilarEmbeddings(entity)
                        
            if res2 is not None and len(res2)>1:
                    res2 = list(set(res2).difference(set(entities)))
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                    rest = set(res2).difference(same_dir).difference(same_g)
            else:
                    res2 = random.sample(self.graph.movies, 100)
                    res2 = list(set(res2).difference(set(entities)))
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
            entity = entities[-1]
            res2 = self.findSimilarEmbeddings(entity)
                        
            if res2 is not None and len(res2)>1:
                    res2 = list(set(res2).difference(set(entities)))
                    same_dir = set(self.check_directors(entity, res2))
                    resres = list(set(res2).difference(set(same_dir)))
                    same_g = set(self.check_genres(entity, resres))
                    rest = set(res2).difference(same_dir).difference(same_g)
            else:
                    res2 = random.sample(self.graph.movies, 100)
                    res2 = list(set(res2).difference(set(entities)))
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
    print(r.getRecommendation(['Star Wars Episode IX: The Rise of Skywalker']))
    print(r.getRecommendation(['A Nightmare on Elm Street', "Friday the 13th"]))
    print(r.getRecommendation(['The Lion King', "Pocahontas", "Beauty and the Beast"]))
    
     #print(r.graph.queryPredicates('Star Wars Episode IX: The Rise of Skywalker'))
    #res2 = r.findSimilarEmbeddings('Star Wars Episode IX: The Rise of Skywalker')
    #r.check_genres('Star Wars Episode IX: The Rise of Skywalker', res2)
    
    
    # once the kind of question was determined, update the matched entities for media and recommender.
    # if type is media get longest overlap with human, if none than with movie
    # if  type is recommender get the longest overlap with movie, if non peak random
    # if those are equal to stored entities than all good, if not try both and choose smth 