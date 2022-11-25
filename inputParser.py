from transformers import pipeline
import constant
import pandas as pd
import re

# https://huggingface.co/docs/transformers/main_classes/pipelines

class InputParser:
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification")
        self.ner_pipeline = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
        
        self.graph_entities = pd.read_csv("utildata/graph_entities.csv")
        self.movies = pd.read_csv("utildata/movie_entities.csv")
        self.directors = pd.read_csv("utildata/director_entities.csv")
        self.actors = pd.read_csv("utildata/actor_entities.csv")
        self.characters = pd.read_csv("utildata/character_entities.csv")
        self.genres = pd.read_csv("utildata/genre_entities.csv")
        
        self.wh_1 = r"(?:Who |What |Where |When| Whom | How)" \
            
        
        self.wh_2 = r"(?:What |Which)" \
        

        self.wh_ner_A = self.wh_1 + r"(?:is |are |was |were |does |do |did |have |has )?(.*)(?: in| of| from| for)(?: the| a)?(?: movie| film |character)?"
        self.wh_ner_B = self.wh_2 + r"(?:movie |movies |film |films )?(?:is |are |was |were |does |do |did )?(.*) (.*)"
        self.wh_ner_C = r"(?:.*)(?:tell)(?: me)?(?: about)?(.*)(?:of|in|from|for)"


        self.wh_A = self.wh_1 + r"(?:is |are |was |were )?(.*)(?: in| of| from| for)(?: the| a)?(.*)(?: movie| film |character)([\w\s]*)"
        self.wh_B = self.wh_1 + r"(?:is |are |was |were )?(.*)(?: in| of| from| for)(?: the| a)?(.*)"
        self.wh_C = self.wh_1 + r"(?:movie |movies |film |films )?(?:is |are |was |were |did )?(.*)(?:by)(.*)"
        self.wh_D = self.wh_1 + r"(?:movie |movies |film |films )?(?:is |are |was |were |did )?(.*) (.*)"
        self.wh_E = r"(?:.*)(?:Tell|tell)(?: me)?(?: about)?(.*)(?:of|in|from|for)(.*)"

        self.wh_type = r"(?:What |what |What's |what's )(?:is |are |was |were )?" \
                          r"(?:a |an |the |the type of |the parent type of |the parent of |the class of |the parent class of )?(.*)"

        # yes/no-questions
        self.yesno_pattern = "(Is|Was|Are|Were|Does|Do|Did|) "

        # recommender-questions #TODO - combine all action questions to recommender questions
        self.recommender = r"(?: I like| I prefer| I love| am into|my favourite |liked|)(?: the)?(.*)(?: movie| movies| film| films| series)?(?:, |. |; )"
        self.recommender_A = self.recommender + r"(?:could you |can you |would you |will you )(?:provide |find |recommend |suggest|show)(?:me)?(.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_B = self.recommender + r"(?:could you |can you |Could you |Can you )(?:provide |find |recommend |suggest|show )(?:me)?(.*)(?: movies| movie| films| film)(.*)"
        self.recommender_C = self.recommender + r"(?:could you |can you |Could you |Can you )(?:provide |find |recommend |suggest|show )(?:me)?(.*)"
        self.recommender_D = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_E = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)(?: movies| movie| films| film)(.*)"
        self.recommender_F = r".*?(?:provide |find |recommend |suggest|show)(?: me)?(.*)"
        self.recommender_ner_A = r"(?:.*)(?:provide |find |recommend |suggest|show)(?: me)?(?: some| any| a few)? (.*)(?: of| by| directed by| featuring| starring)(?: his| hers| theirs| the movie| the film| the series| the)?(.*)"
        self.recommender_ner_B = r"(?:.*)(?:provide |find |recommend |suggest|show)(?: me)?(.*)"

        self.main_actor_character_pattern = 'main actor|lead actor|main character|lead character'

        self.image_pattern_A = r"poster|posters|picture|pictures|image|images|photo|photos|scene|frame"
        self.image_pattern_B = r"(?:What |How |what |how |What's |How's |what's |how's )(?:do |does |is |are )?(.*)(?: look like| like)"

        #self.embedding_pattern = r"similar"
        
    def parseInput(self, question):
        return
    
    def getEntities(self, question):
        entities = self.ner_pipeline(question, aggregation_strategy="simple")
        if len(entities) == 0:
            print("no entities")
            res = []
        else:
            res = [' '.join([str(item['word']) for item in entities])]
            res = [item['word'] for item in entities]
        return res
    
    def getLabel(self, question):
        res =  self.classifier(question, constant.CANDIDATE_LABELS_MOVIE)
        res = res["labels"][0]
        print(res)
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
    
    def getQuestionType(self, question, is_ner=True, entity=None):
        res = self.checkSpecialQuestion(question, is_ner, entity)
        if res:
            return "special", res.groups()
        elif self.is_yesno_question(question):
        #    return "yesno", []
        #elif self.is_recommender_question(question, is_ner):
        #    return "recommender", self.is_recommender_question(question, is_ner).groups()
        else:
            return "unknown", []
    
    def checkSpecialQuestion(self, question, is_ner=True, entity=None):
        if is_ner:
            return re.match(self.wh_ner_A, question, re.IGNORECASE) or re.match(self.wh_ner_B(entity), question, re.IGNORECASE) \
                   or re.match(self.wh_type, question, re.IGNORECASE) or re.match(self.wh_ner_C, question, re.IGNORECASE)
        else:
            return re.match(self.wh_A, question) or re.match(self.wh_B, question) \
                   or re.match(self.wh_C, question) or re.match(self.wh_type, question) \
                   or re.match(self.wh_E, question)   
    
    def checkGeneralQuestion(self, question, is_ner=True, entity=None):
        if is_ner:
            return re.match(self.wh_ner_A, question, re.IGNORECASE) or re.match(self.wh_ner_B(entity), question, re.IGNORECASE) \
                   or re.match(self.wh_type, question, re.IGNORECASE) or re.match(self.wh_ner_C, question, re.IGNORECASE)
        else:
            return re.match(self.wh_A, question) or re.match(self.wh_B, question) \
                   or re.match(self.wh_C, question) or re.match(self.wh_type, question) \
                   or re.match(self.wh_E, question)     
    
    def checkRecommenderQuestion(self, question, is_ner=True, entity=None):
        if is_ner:
            return re.match(self.wh_ner_A, question, re.IGNORECASE) or re.match(self.wh_ner_B(entity), question, re.IGNORECASE) \
                   or re.match(self.wh_type, question, re.IGNORECASE) or re.match(self.wh_ner_C, question, re.IGNORECASE)
        else:
            return re.match(self.wh_A, question) or re.match(self.wh_B, question) \
                   or re.match(self.wh_C, question) or re.match(self.wh_type, question) \
                   or re.match(self.wh_E, question)     
                   
    def checkMediaQuestion(self, question, is_ner=True, entity=None):
        if is_ner:
            return re.match(self.wh_ner_A, question, re.IGNORECASE) or re.match(self.wh_ner_B(entity), question, re.IGNORECASE) \
                   or re.match(self.wh_type, question, re.IGNORECASE) or re.match(self.wh_ner_C, question, re.IGNORECASE)
        else:
            return re.match(self.wh_A, question) or re.match(self.wh_B, question) \
                   or re.match(self.wh_C, question) or re.match(self.wh_type, question) \
                   or re.match(self.wh_E, question)    
                   
    def checkMediaQuestion(self, question, is_ner=True, entity=None):
        if is_ner:
            return re.match(self.wh_ner_A, question, re.IGNORECASE) or re.match(self.wh_ner_B(entity), question, re.IGNORECASE) \
                   or re.match(self.wh_type, question, re.IGNORECASE) or re.match(self.wh_ner_C, question, re.IGNORECASE)
        else:
            return re.match(self.wh_A, question) or re.match(self.wh_B, question) \
                   or re.match(self.wh_C, question) or re.match(self.wh_type, question) \
                   or re.match(self.wh_E, question)     
    
    