import constant
from inputParser import InputParser
from graph import Graph
from crowdsource import CrowdSource
from embedding import EmbeddingService
from multimedia import MultimediaService

class Chatbot:
    def __init__(self, room_id):
        self.room_id = room_id
        self.graph = Graph(False)
        self.inputParser = InputParser()
        self.crowd_source = CrowdSource()
        self.embedding_service = EmbeddingService()
        self.multimedia_service = MultimediaService(self.graph)
    
    
    def getHelp(self):
        info = """
        
        """
        return info

    def getResponse(self, question):
        try:
            #question_type, entities, relation = self.inputParser.parse(question)
           
           
            # Step 1: parse the input
            question = self.inputParser.cleanUpInput(question)
            entities, types, matches = self.inputParser.getEntities(question)
            print("entities", entities)
            print("types", types)
            print("matches", matches)

            if (len(entities) >=1):
                entity1 =  entities[0]
            else:
                entity1 = None
            if (len(entities) >=2):
                entity2 =  entities[1]
            else:
                entity2 = None
            predicate = self.inputParser.getQuestionType(question, entity1= entity1,  entity2= entity2)
            print("predicate", predicate)
            
            
            # Step 2: break early when smth was not found, match predicate
            if predicate is None or entities is None or len(predicate) == 0 or len(entities) == 0:
                # TODO: try some second approach
                print("nothing was matched",constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE
            
            matched_predicate = None
            if predicate[0]!= "media" and len(predicate)>=2:
                matched_predicate = self.inputParser.getPredicate(predicate[1])   
                print("matched_predicate", matched_predicate) 
                
            if predicate[0]!= "media" and  matched_predicate is None:
                # TODO: try some second approach
                print("nothing was matched",constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE
                            
            # step 3: once entitiy and predicate is known - > through intermediry answer
            # INTERMIDIARY ANSWER
            if len(entities) == 1 and types[0] == "movie":
                print("Great, %s is my favourite movie! Give me a second to check information about its %s." %(entities[0], matched_predicate[0])) 
            elif len(entities) == 1 and types[0] == "person":
                print("Great, %s is really talented! Give me a second to check information about this person." %entities[0]) #TODO: make her/him
            if len(entities) == 2 and types[0] == "movie":
                print( "Great, %s is my favourite movie! Give me a second to check information about it." %entities[0])
            
             
            # step 4 get the actual answer depending on the case
            # CASE 1: media question
            if predicate[0]== "media":
                answer = self.multimedia_service.getAnswer(matches)
                return answer
            
            # CASE 2: recommendation question
            if predicate[0]== "recommend":
                #answer = self.multimedia_service.getAnswer(matches)
                return "Not implemented"
       
            # CASE 3: normal graph question + crowdsourcing and embedding
            else:
                graphAnswer, userGraphString, crowdGraphAnswer = self.graph.getAnswer(predicate[0], matched_predicate, types, matches)
                print("final answer to the user from the graph:", graphAnswer, userGraphString)
                
                if crowdGraphAnswer is None or len(crowdGraphAnswer) == 0:
                    print("this question was not answered by the crowd")
                    crowdsourceAnswer = ""
                else:
                    crowdsourceAnswer = self.crowd_source.getAnswer(crowdGraphAnswer, predicate[0], matches)
                    print("final answer to the user from the crowd:", crowdsourceAnswer)
            
            #if graphAnswer is None:
            #    # TODO: try some second approach
            #    print("final answer to the user from the graph approach 2:", constant.DEFAULT_MESSAGE)
                
                return userGraphString+crowdsourceAnswer
                       
        except Exception as e:
            #response = constant.DEFAULT_MESSAGE
            print("Error:", e)
            return("the pipeline broke")
    
    
def main():
    chatbot = Chatbot(1)
    question =  'Let me know what Sandra Bullock looks like.' #who directed batman movie
    response = chatbot.getResponse(question)
    print("a very final answer", response)
    
    
if __name__ == "__main__":
    main()