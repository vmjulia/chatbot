from transformers import pipeline
import difflib
import constant
import pandas as pd
import re
from fuzzywuzzy import process

# https://huggingface.co/docs/transformers/main_classes/pipelines

class InputParser:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification")
        self.ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
        
        self.graph_entities = pd.read_csv("utildata/graph_entities.csv")["EntityLabel"]
        self.movies = pd.read_csv("utildata/movie_entities.csv")["EntityLabel"]
        self.directors = pd.read_csv("utildata/director_entities.csv")["EntityLabel"]
        self.actors = pd.read_csv("utildata/actor_entities.csv")["EntityLabel"]
        self.characters = pd.read_csv("utildata/character_entities.csv")["EntityLabel"]
        self.genres = pd.read_csv("utildata/genre_entities.csv")["EntityLabel"]
        
        #special questions
        self.wh_1 = r"(?:.*)?(?:Who |What |Whom |How)"   
        self.wh_2 = r"(?:.*)?(?:What |Which )"
        self.wh_3 = r"(?:.*)?(?:Who )"
        
        self.wh_A = self.wh_1 + r"(?:is |are |was |were |does |do |did )?(.*)(?: in | of | from | for )(?: the| a)?(?: movie| film|character)?"
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
        self.image_pattern_B = r"(?:What |How | What's |How's |what's |how's )(?:do |does |is |are )?(.*)(?: look like| like)"
        
    def who_pattern (self, entity):
            entity = " "+entity
            toreturn1 = self.wh_D + "(?: the| a)" +"(?:.*)?"+ f"(.*){entity}" if entity else  self.wh_D
            toreturn2 = self.wh_D + f"(.*){entity}" if entity else  self.wh_D
            return [toreturn1, toreturn2]
        
    def where_when_pattern (self, entity):
            pattern = r"(?:.*)?(Where|When)"+"(?:.*)?"+f"(?:.*){entity}"+"(.*)"
            return pattern
        
    def parseInput(self, question):
        return
    
    def cleanUpInput(self, input):
        input = re.sub('[-,/:!@#$]', '', input)
        return " ".join(input.split())
    
    def getEntities(self, question):
        entities = self.ner_pipeline(question, aggregation_strategy="simple")
        input_entities = []
        types = []
        print(entities)
        for item in entities:
            # first determine the type of this item
            if("entity" in item and item['entity'] == 'I-PER'):
                type = 'human'
            else: type = 'movie'
                      
            # if aggregation did not work properly aggregate manually
            if(len(item['word']) > 2 and item['word'][:2] == '##' and len(input_entities) != 0):
                input_entities[-1] = input_entities[-1] + item['word'][2:]
                if types[-1] != type:
                    types[-1] = 'movie'  
            # if there is 
            elif(len(item['word']) > 0 ):
                input_entities.append(item['word'])
                types.append(type)
        for i in range(len(input_entities)):
            if types[i] == "movie":
                matched_entities = self.matchEntity(input_entities[i], types[i])
            elif types[i] == "person":
                matched_entities = self.matchEntity(input_entities[i], types[i])
        
        #if len(entities) == 0:
        #    print("no entities")
        #    res = []
        #else:
        #    res = [' '.join([str(item['word']) for item in entities])]
        #    res = [item['word'] for item in entities]
        return input_entities, types, matched_entities
    
    def matchEntity(self,entity, type):

        if(type == "movie"):
            labels =self.movies.tolist()
            match, score = process.extractOne(labels, entity, score_cutoff = 60)
            close_matches = difflib.get_close_matches(entity, labels)
        elif(type == "human"):
            labels = [i[1] for i in self.directors.tolist()]
            close_matches = difflib.get_close_matches(entity, labels)
    
        
        print("closest matches", match, score)
        return []
    
    
    def getLabel(self, question):
        res =  self.classifier(question, constant.CANDIDATE_LABELS_MOVIE)
        res = res["labels"][0]
        return res

    
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
        media = self.checkMediaQuestion(question, entity1)
        
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
                   
    def checkMediaQuestion(self, question, is_ner=True, entity=None):
        return False 
                

