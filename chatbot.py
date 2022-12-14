import constant
from inputParser import InputParser
from graph import Graph
from crowdsource import CrowdSource
from embedding import EmbeddingService
from multimedia import MultimediaService
from recommend import Recommender
import random

class Chatbot:
    
    def __init__(self, room_id, classifier = None, ner_pipeline = None ):
        self.room_id = room_id
        self.graph = Graph(False)
        self.inputParser = InputParser(classifier, ner_pipeline)
        self.crowd_source = CrowdSource()
        self.embedding_service = EmbeddingService(self.graph)
        self.graph.EmbeddingService = self.embedding_service
        self.multimedia_service = MultimediaService(self.graph)
        self.recommender = Recommender(self.graph, self.embedding_service)
        
        
    def check_some_stuff(self, question):
        question_lower = question.lower()
        
        greetings = ["hi", "hello", "good morning", "morning", "good afternoon", "afternoon", "good day", "greeting"]
        for greeting in greetings:
            if greeting in question_lower:
                return random.choice(constant.GREETINGS)
        bye = ["bye", "goodbye", "see you", "later", "have a nice day"]
        for b in bye:
            if b in question_lower:
                return random.choice(constant.BYE_RESPONSE)
        
        thanks = ["thanks", "thank", "helpful", "well done"]
        for b in thanks:
            if b in question_lower:
                return random.choice(constant.THANKS_RESPONSE)
        return None
    
    def check_indirect_subclass_of(self, question):
        question_lower = question.lower()
        predicate = ["indirect subclass of", "indirect subclass", "subclass of", "type", "class", "parent", "indirectSubclassOf", "sub class"]
        for p in predicate:
            if p in question_lower:
                pp = ["special", p]
                e = self.inputParser.matchweirdEntitiesApproximately(question)
                if e is not None:
                    ee = [e]
                    type = ["unknown"]
                    return  pp, ee, type, ee, ee[0]
        return None, None, None, None
                
  
    
    def getResponse(self, question):
        try:              
            # Step 1: parse the input
            question = self.inputParser.cleanUpInput(question)
            entities, types, matches = self.inputParser.getEntities(question)
            print("entities", entities)
            print("types", types)
            print("matches", matches)

            if (len(entities) >=1 and len(matches) >=1 ):
                entity1 =  entities[0]
                match1 =  matches[0]
            else:
                entity1 = None
                
            if (len(entities) >=2):
                entity2 =  entities[1]
            else:
                entity2 = None
                
                
            predicate = self.inputParser.getQuestionType(question, entity1= entity1,  entity2= entity2)
            if predicate is None:
                possible_answer = self.check_some_stuff(question)
                if possible_answer is not None:
                    return False, possible_answer, None, None, None,None 
                else:
                    predicate, entities, types, matches, match1 = self.check_indirect_subclass_of(question)
                    if entities is None:
                        return False, constant.DEFAULT_MESSAGE, None, None, None,None 
           
            print("predicate", predicate)
            
            
            # Step 2: break early when smth was not found, match predicate
            if predicate is None or len(predicate) == 0:
                print("no predicate!! type of question was not determined")
                return False, constant.DEFAULT_MESSAGE, None, None, None,None 
            
            # fix matches for media and recommender questions
            if predicate[0] == "media":

                if  matches is not None and len(matches) == 2: 
                    if types[0] == "person":
                        matches = [matches[0]]
                        types = ["person"]
                           
                    elif types[1] == "person":
                         matches = [matches[1]]
                         types = ["person"]
                         
                # stupid cases, update this
                elif matches is None or len(matches)>2 or len(matches) ==0:
                    matches_new= self.inputParser.getEntitiesPerson(question) 
                    if len(matches_new)>0:
                        matches = [matches_new[0]]
                        types = ["person"]
                    else: 
                        matches_new= self.inputParser.getEntitiesMovies(question) 
                        if len(matches_new)>0:
                            matches = [matches_new[0]]
                            types = ["movie"]
                    print("updated matches", matches)
                   
            if predicate[0] == "recommendation":
                matches_new= self.inputParser.getEntitiesMovies(question) 
                if len(matches_new)>0:
                    matches = matches_new
                    matches.append(match1) # just if it was actually good and we lost it
                    matches = list(set(matches))
                    print("updated matches", matches)
                 
            # if no matches, break
            if  matches is None or len(matches) == 0:
                print("no entities were found")
                return False, constant.DEFAULT_MESSAGE, None, None, None,None 
            
            
            #matching the predicate 
            matched_predicate = None
            if predicate[0]!= "media" and predicate[0]!= "recommendation" and len(predicate)>=2: # if we have type of question and our predicate
                predicate_candidates = self.graph.queryPredicates(match1)
                if len(predicate_candidates)>0:
                    matched_predicate = self.inputParser.getPredicate(predicate[1], predicate_candidates)   
                print("matched_predicate", matched_predicate) 
                
            if (predicate[0]!= "media" and predicate[0]!= "recommendation") and  (matched_predicate is None or len(matched_predicate) == 0):
                # TODO: maybe do smth here, maybe not
                print("no predicate was matched",constant.DEFAULT_MESSAGE)
                return False, constant.DEFAULT_MESSAGE, None, None, None,None 
 
            
            # step 3: once entitiy and predicate is known - > through intermediry answer
            # INTERMIDIARY ANSWER
            if predicate[0]!= "media" and predicate[0]!= "recommendation" and len(matches) > 0 and types[0] == "movie":
                return True, ("Great, %s is my favourite movie! Give me a second to check information about its %s." %(match1, matched_predicate[0])), predicate, matches, matched_predicate,types
            elif len(matches) > 0 and predicate[0]== "recommendation":
                return True, ( "Great, %s is my favourite movie! I will search for recommendations." %match1),  predicate, matches, matched_predicate,types
            
            elif len(matches) > 0 and types[0] == "movie":
                return True, ( "Great, %s is my favourite movie! Give me a second to check information about it." %match1),  predicate, matches, matched_predicate,types
            elif len(matches) == 1 and types[0] == "person":
                return True, ("Great, %s is really talented! Give me a second to check information about this person." %match1),  predicate, matches, matched_predicate,types
            
            return True, "Just one second..  I am searching",  predicate, matches, matched_predicate,types 
                                   
        except Exception as e:
            print("exception was thown:", e)
            return False, constant.DEFAULT_MESSAGE, None, None, None,None 
        
        
    def getResponseFinal(self,  predicate, matches, matched_predicate,types, question):
        try:
            # step 4 get the actual answer depending on the case
            # CASE 1: media question
            if predicate[0]== "media":
                answer = self.multimedia_service.getAnswer(matches, types, question)
            
            elif predicate[0]== "recommendation":
                answer = self.recommender.getRecommendation(matches)
                print("recommender returned", answer)             
       
            # CASE 3: normal graph question + crowdsourcing and embedding
            else:
                graphAnswer, userGraphString, crowdGraphAnswer, embed_answer = self.graph.getAnswer(predicate[0], matched_predicate, types, matches)
                print("final answer to the user from the graph:", graphAnswer, userGraphString)
                
                if crowdGraphAnswer is None or len(crowdGraphAnswer) == 0:
                    print("this question was not answered by the crowd")
                    crowdsourceAnswer = ""
                else:
                    crowdsourceAnswer = self.crowd_source.getAnswer(crowdGraphAnswer, predicate[0], matches)
                    print("final answer to the user from the crowd:", crowdsourceAnswer)
                answer =  userGraphString+crowdsourceAnswer
                
                
                if embed_answer is not None:
                    answer =  answer + embed_answer        
                    
            if answer is None or len(answer)==0:
                return False, constant.DEFAULT_MESSAGE, None, None, None,None 
            else:
                return answer
            
        except Exception as e:
            response = constant.DEFAULT_MESSAGE
            print("Error:", e)
            return("the pipeline broke")
        
    
    
def main():
    chatbot = Chatbot(1)
    text_file = open("test.txt", "w")
    text_file.write("NEW RUN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    #TODO: add pattern can i see for images maybe
    
    
    
    text_file.write("EMBEDDINNG QUESTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    question =  'What is the genre of Good Neighbors?' #who directed batman movie
    #question =  'Hi' #who directed batman movie
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    exit()
    question =  'Who directed Star Wars: Episode VI - Return of the Jedi?' #who directed batman movie
    #question =  'Hi' #who directed batman movie
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    exit()
    
    question =  'What is the MPAA film rating of Weathering with You?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'What is the genre of Good Neighbors?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answr", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    
    text_file.write("NORMAL QUESTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    
    
    question =  'Who is the director of Good Will Hunting?' #who directed batman movie
    #question =  'Hi' #who directed batman movie
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Who directed The Bridge on the River Kwai?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Who is the director of Star Wars: Episode VI - Return of the Jedi?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answr", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    
    text_file.write("CROWDSOURCE QUESTIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    
    question =  'What is fictional princess indirect subclass of?' #who directed batman movie
    #question =  'Hi' #who directed batman movie
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
        
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    
    
    question =  'What is the box office of The Princess and the Frog?' #who directed batman movie
    #question =  'Hi' #who directed batman movie
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Can you tell me the publication date of Tom Meets Zizou?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answer", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Who is the executive producer of X-Men: First Class?'
    flag, response,  predicate, matches, matched_predicate,types = chatbot.getResponse(question)
    print("first answr", response)
    if flag:
        response = chatbot.getResponseFinal(predicate, matches, matched_predicate,types, question)
    
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    exit()
    
    
    text_file.write("PICTURES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    question =  'Show me a picture of Halle Berry.' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'What does Julia Roberts look like?' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response + "\n")
    
    question =  'Let me know what Sandra Bullock looks like.' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    text_file.write("RECOMMENDATIONS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    question =  'Recommend movies similar to Hamlet and Othello' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Given that I like The Lion King, Pocahontas, and The Beauty and the Beast, can you recommend some movies?' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    
    question =  'Recommend movies like Nightmare on Elm Street, Friday the 13th, and Halloween.' #who directed batman movie
    response = chatbot.getResponse(question)
    text_file.write(question+ "\n")
    text_file.write(response+ "\n")
    text_file.close()
    
if __name__ == "__main__":
    main()