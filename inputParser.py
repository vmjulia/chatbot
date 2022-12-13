from transformers import pipeline
import constant
import pandas as pd
import re
from fuzzywuzzy import process

# https://huggingface.co/docs/transformers/main_classes/pipelines

class InputParser:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification")
        self.ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
        
        self.graph_entities = pd.read_csv("utildata/graph_entities.csv")["EntityLabel"].tolist()
        self.movies = pd.read_csv("utildata/movie_entities.csv")["EntityLabel"].tolist()
        self.directors = pd.read_csv("utildata/director_entities.csv")["EntityLabel"].tolist()
        self.actors = pd.read_csv("utildata/actor_entities.csv")["EntityLabel"].tolist()
        self.characters = pd.read_csv("utildata/character_entities.csv")["EntityLabel"].tolist()
        self.genres = pd.read_csv("utildata/genre_entities.csv")["EntityLabel"].tolist()
        self.predicates = pd.read_csv("utildata/graph_properties_expanded.csv")["PropertyLabel"].tolist()
        self.people =  self.directors+self.actors+ self.characters # TODO: add some more
         
        #special questions
        self.wh_1 = r"(?:.*)?(?:Who |What |Whom |How)"   
        self.wh_2 = r"(?:.*)?(?:What |Which )"
        self.wh_3 = r"(?:.*)?(?:Who )"
        
        self.wh_A = self.wh_1 + r"(?:is |are |was |were |does |do |did )?(.*?)(?: in | of | from | for )(?: the| a)?(?: movie| film|character)?"
        self.wh_B = self.wh_2 + r"(?:movie |movies |film |films )?(?:is |are |was |were |does |do |did |has|have|had)?(.*)"
        self.wh_C = r"(?:.*)?(?:tell |give information |provide information |inform )(?:me )?(?:please )?(?:about )?(.*)(?: of | in | from | for | by )"
        self.wh_D = self.wh_3 + r"(.*)" # who directed e.g.
      
        #general questions
        self.general_pattern = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did )(.*)?(.*)"
        
        #recommender questions
        self.recommender = r"(?: I like| I prefer| I love| am into|my favourite |liked|)(?: the)?(.*)(?: movie| movies| film| films| series)?(?:, |. |; )"
        self.recommender_A = self.recommender + r"(?:could you |can you |would you |will you )(?:provide |find |recommend |suggest|show)(?:me)?(.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_B = self.recommender + r"(?:could you |can you |Could you |Can you )(?:provide |find |recommend |suggest|show )(?:me)?(.*)(?: movies| movie| films| film)(.*)"
        self.recommender_C = self.recommender + r"(?:could you |can you |Could you |Can you )(?:provide |find |recommend |suggest|show )(?:me)?(.*)"
        self.recommender_D = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_E = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)(?: movies| movie| films| film)(.*)"
        self.recommender_F = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)"
        self.recommender_G = r"(?:.*)(?:provide |find |recommend |suggest|show)(?: me)?(?: some| any| a few)? (.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_H= r"(?:.*)(?:provide |find |recommend |suggest|show)(?: me)?(.*)"
        
        #media
        self.image_pattern_A = r"poster|posters|picture|pictures|image|images|photo|photos|scene|frame"
        self.image_pattern_B = r"(?:What |How | What's |How's |what's |how's )(?:do |does |is |are )?(.*)(?: look like| looks like)"

    def who_pattern (self, entity):
            entity = " "+entity
            toreturn1 = self.wh_D + "(?: the| a)" +"(?:.*)?"+ f"(.*){entity}" if entity else  self.wh_D
            toreturn2 = self.wh_D + f"(.*){entity}" if entity else  self.wh_D
            return [toreturn1, toreturn2]
        
    def where_when_pattern (self, entity):
            pattern = r"(?:.*)?(Where|When)"+"(?:.*)?"+f"(?:.*){entity}"+"(.*)"
            return pattern
    
    def movie_person_pattern (self, entity, question):
            pattern = r"(.*)?"+f"(?:.*){entity}"+"(.*)?"
            
            res = re.match(pattern, question, re.IGNORECASE)
            if res != None:
                res = True
            return res, entity
        
    def parseInput(self, question):
        return
    
    def cleanUpInput(self, input):
        input = re.sub('[-,/:!@#$?]', '', input)
        return " ".join(input.split())
    
    def getEntitiesEasy(self, question):
        matches = []
        entities = []
        types = []
        for movie in self.movies:
            res, match = self.movie_person_pattern(movie,question)
            if res:
                matches.append(match)
        if len (matches)>0:
            print("chosen movie", max(matches, key=len))
            entities.append(max(matches, key=len))
            entities.append("movie")
            
        for person in self.people:
            res, match = self.movie_person_pattern(person,question)
            if res:
                matches.append(match)
        if len (matches)>0:
            print("chosen person", max(matches, key=len))
            entities.append(max(matches, key=len))
            entities.append("person")
            
        return entities, types, entities
            
    def getEntities(self, question):
        # TODO: add box staff numbers as entitiy and dates as date as entity
        entities = self.ner_pipeline(question, aggregation_strategy="simple")
        input_entities = []
        types = []
        for item in entities:
            # first determine the type of this item
            if(item['entity_group'] == 'PER'):
                type = 'person'
            elif(item['entity_group'] == 'MISC'):
                type = 'movie'
            elif(item['entity_group'] == 'LOC'):
                type = 'location'
            elif(item['entity_group'] == 'ORG'):
                type = 'organization'
            else: type = 'smth'
                      
            # if aggregation did not work properly aggregate manually
            if(len(item['word']) > 2 and item['word'][:2] == '##' and len(input_entities) != 0):
                input_entities[-1] = input_entities[-1] + item['word'][2:]
                if types[-1] != type:
                    types[-1] = type 
                    
            # in normal case just append
            elif(len(item['word']) > 0 ):
                input_entities.append(item['word'])
                types.append(type)
        
        movie_score = 0
        person_score = 0
        person = None
        movie = None
        person_match = None
        movie_match = None
        
        
        for i in range(len(input_entities)):
            if types[i] == "movie" and movie != None: # probably movie got split into two
                        new1 = input_entities[i] + " "+  movie
                        new2 = movie + " "+  input_entities[i]
                        match, score = self.matchEntity(new1, "movie")
                        
                        if score >=0.9*movie_score:
                            movie_score = score
                            movie_match = match
                            movie = new1
                        
                        match, score = self.matchEntity(new2, "movie")
                        if score >=0.9*movie_score:
                            movie_score = score
                            movie_match = match
                            movie = new2   
                              
            elif types[i] == "movie":
                match, score = self.matchEntity(input_entities[i], types[i])
                if score >movie_score:
                    movie = input_entities[i]
                    movie_score = score
                    movie_match = match
                    
            elif types[i] == "person":
                match, score = self.matchEntity(input_entities[i], types[i])
                if score >person_score:
                    person = input_entities[i]
                    person_score = score
                    person_match = match
                    
        for i in range(len(input_entities)):
              if types[i] != "movie"  and   types[i] != "person" : # if there is smth else like location, check that it is not actually part of the movie
                match, score = self.matchEntity(input_entities[i], "movie")
                if (movie_score is not None and score >movie_score) or movie_score is None:
                    movie = input_entities[i]
                    movie_score = score
                    movie_match = match
                if movie != None:
                        new1 = input_entities[i]+ " "+ movie
                        new2 =movie+ " "+  input_entities[i]
                        match, score = self.matchEntity(new1, "movie")
                        if score > movie_score:
    
                            movie_score = score
                            movie_match = match
                            movie = new1
                        match, score = self.matchEntity(new2, "movie")
                        if score > movie_score:
 
                            movie_score = score
                            movie_match = match
                            movie = new2             
        
        if (movie_score!= 0 and person_score!= 0):
            return ([movie, person], ["movie", "person"], [movie_match, person_match])
        elif (movie_score!= 0 and person_score== 0):

            return ([movie], ["movie"], [movie_match])
        elif (movie_score== 0 and person_score!= 0):

            return ([person], ["person"], [person_match])
        return [], [], []
    
    def matchEntity(self,entity, type):

        if(type == "movie"):
            labels = self.movies
            match, score = process.extractOne(entity, labels, score_cutoff = 0)

        elif(type == "person"):
            labels = self.directors.copy()
            labels.extend(self.actors)
            match, score = process.extractOne(entity,labels, score_cutoff = 0) 
        else:
            return [], []
    
        return match, score
    
    
    def getLabel(self, question):
        res =  self.classifier(question, constant.CANDIDATE_LABELS_MOVIE)
        res = res["labels"][0]
        return res

    
    def getPredicate(self, predicate):
        labels = self.predicates
        # TODO: must be several top
        res = []
        predicates = None
        predicates = process.extract(predicate, labels, limit = 3)
        if predicates is not None:
            for index in range(len(predicates)):
                if (predicates[index][1]>50):
                    res.append(predicates[index][0])
        return res
    
    # check why I did it 
    def getGraphEntity(self, entity_string):
        # get some additional classification as this is not enough
        if self.genres['EntityLabel'].str.lower().str.contains(entity_string.lower(), regex=False).any():
            return "GENRE"
        elif self.movies['EntityLabel'].str.lower().str.contains(entity_string.lower(), regex=False).any():
            return "TITLE"
        elif self.characters['EntityLabel'].str.lower().str.contains(entity_string.lower(), regex=False).any():
            return "CHARACTER"
        elif self.actors['EntityLabel'].str.lower().str.contains(entity_string.lower(), regex=False).any():
            return "ACTOR"
        elif self.directors['EntityLabel'].str.lower().str.contains(entity_string.lower(), regex=False).any():
            return "DIRECTOR"
        else:
            return entity_string
    
    def getQuestionType(self, question,  entity1=None, entity2 = None):

        special = self.checkSpecialQuestion(question,  entity= entity1 )
        general = self.checkGeneralQuestion(question, entity1,  entity2)
        recommendation = self.checkRecommenderQuestion(question,  entity1)
        media = self.checkMediaQuestion(question)
        
        if recommendation and not media:
            return "recommendation", recommendation.group()
        if media and not recommendation:
           return "media", media.group()
        if special and not recommendation and not media :
            try:
                return "special", special.group(1) + special.group(2)
            except:
                return "special", special.group(1)
        if general and not recommendation and not media:
            return "general", general.group(1)
        else:
            print("use classification method")
            return
    
    def checkSpecialQuestion(self, question, entity=None):        
            return  re.match(self.wh_A, question, re.IGNORECASE)  or re.match(self.wh_B, question, re.IGNORECASE)  or re.match(self.wh_C, question, re.IGNORECASE) or re.match(self.who_pattern(entity)[0], question, re.IGNORECASE) or re.match(self.who_pattern(entity)[1], question, re.IGNORECASE) or re.match(self.where_when_pattern(entity), question, re.IGNORECASE)
        
    
    def checkGeneralQuestion(self, question, entity1, entity2):
        if entity1 and entity2:
            entity1_first = entity1+" "
            entity2_first = entity2+" "
            entity1_last = " "+entity1
            entity2_last = " "+ entity2
            res1 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity1_first}" + "(.*)" + "(?: of | by | in | on | for )"+ "(?:the |a )?" +"(?:.*)?"+ f"(?:.*){entity2}" 
            res2 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity2_first}" + "(.*)" + "(?: of | by | in | on | for )"+ "(?:the |a )?"+  "(?:.*)?"+ f"(?:.*){entity1}" 
            res3 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity1_first}" + "(.*)" + "(?: the| a)" +"(?:.*)?"+ f"(?:.*){entity2_last}"  
            res4 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity2_first}" + "(.*)" + "(?: the| a)" +"(?:.*)?"+ f"(?:.*){entity1_last}" 
            res5 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity1_first}" + "(.*)" +  f"(?:.*){entity2_last}"  
            res6 = r"(?:.*)?(?:Is |Was |Are |Were |Does |Do |Did |Has |Have |Had )" + f"(?:.*){entity2_first}" + "(.*)" +  f"(?:.*){entity1_last}" 
            return re.match(res1, question, re.IGNORECASE) or re.match(res2, question, re.IGNORECASE) or re.match(res3, question, re.IGNORECASE) or re.match(res4, question, re.IGNORECASE) or re.match(res5, question, re.IGNORECASE) or re.match(res6, question, re.IGNORECASE)
        return False  
      
    def checkRecommenderQuestion(self, question, is_ner=True, entity=None):
        return False     
                   
    def checkMediaQuestion(self, question):
        res1 = re.search(self.image_pattern_A, question) 
        res2 = re.match(self.image_pattern_B, question)
        return re.search(self.image_pattern_A, question, re.IGNORECASE) or re.match(self.image_pattern_B, question, re.IGNORECASE)
        
                

