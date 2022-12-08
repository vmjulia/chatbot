import constant
from inputParser import InputParser
from graph import Graph
from crowdsource import CrowdSource

class Chatbot:
    def __init__(self, room_id):
        self.room_id = room_id
        self.previous_token = [] 
        self.graph = Graph(False)
        self.inputParser = InputParser()
        #self.crowd_source = CrowdSource()
        #self.rdf_query_service = RDFQueryService(dataset.graph)
        #self.embedding_service = EmbeddingService(dataset.graph)
        #self.image_service = ImageService(dataset.graph)

    
    def getHelp(self):
        info = """
        
        """
        return info

    def getResponse(self, question):
        try:
            #question_type, entities, relation = self.inputParser.parse(question)

            question = self.inputParser.cleanUpInput(question)
            res = self.inputParser.is_embedding_questions(question)
            print("embeddings return", res)
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
            if len(predicate)>=2:
                matched_predicate = self.inputParser.getPredicate(predicate[1])   
                print("matched_predicate", matched_predicate) 
                
            if len(matched_predicate)==0 or len(entities) == 0:
                # TODO: try some second approach
                print(constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE
                    
            if len(entities) == 1 and types[0] == "movie":
                print("Great, %s is my favourite movie! Give me a second to check information about its %s." %(entities[0], matched_predicate[0])) 
            elif len(entities) == 1 and types[0] == "person":
                print("Great, %s is really talented! Give me a second to check information about this person." %entities[0]) #TODO: make her/him
            if len(entities) == 2 and types[0] == "movie":
                print( "Great, %s is my favourite movie! Give me a second to check information about it." %entities[0])
            
            answer = self.graph.getAnswer(predicate[0], matched_predicate, types, matches)
            print("final answer to the user:", answer)
            
            if answer is None:
                # TODO: try some second approach
                print(constant.DEFAULT_MESSAGE)
                return constant.DEFAULT_MESSAGE  
        except Exception as e:
            #response = constant.DEFAULT_MESSAGE
            print("Error:", e)
            
        #answer = self.graph.query_wh(predicate, entities, types, matches)
        #print(answer)
    
    
def main():
    chatbot = Chatbot(1)
    question =  'What is the MPAA film rating of Weathering with You?' #who directed batman movie
    response = chatbot.getResponse(question)
    print(response)
    
    
if __name__ == "__main__":
    main()