import constant
from inputParser import InputParser
from graph import Graph
from crowdsource import CrowdSource
from embedding import EmbeddingService

class Chatbot:
    def __init__(self, room_id):
        self.room_id = room_id
        self.previous_token = [] 
        self.graph = Graph(False)
        self.inputParser = InputParser()
        self.crowd_source = CrowdSource()
        self.embedding_service = EmbeddingService()
      
        #self.image_service = ImageService(dataset.graph)

    
    def getHelp(self):
        info = """
        
        """
        return info

    def getResponse(self, question):
        try:
            #question_type, entities, relation = self.inputParser.parse(question)

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
            
            
            if predicate is None or entities is None or len(predicate)<2 or len(entities) == 0:
                # TODO: try some second approach
                print("nothing was matched",constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE
            
            if len(predicate)>=2:
                matched_predicate = self.inputParser.getPredicate(predicate[1])   
                print("matched_predicate", matched_predicate) 
                
            if matched_predicate is None:
                # TODO: try some second approach
                print("nothing was matched",constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE
                            
            if len(entities) == 1 and types[0] == "movie":
                print("Great, %s is my favourite movie! Give me a second to check information about its %s." %(entities[0], matched_predicate[0])) 
            elif len(entities) == 1 and types[0] == "person":
                print("Great, %s is really talented! Give me a second to check information about this person." %entities[0]) #TODO: make her/him
            if len(entities) == 2 and types[0] == "movie":
                print( "Great, %s is my favourite movie! Give me a second to check information about it." %entities[0])
            
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
            
        #answer = self.graph.query_wh(predicate, entities, types, matches)
        #print(answer)
    
    
def main():
    chatbot = Chatbot(1)
    question =  'Who directed The Bridge on the River Kwai?' #who directed batman movie
    response = chatbot.getResponse(question)
    print("a very final answer", response)
    
    
if __name__ == "__main__":
    main()