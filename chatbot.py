import constant
from inputParser import InputParser
from graph import Graph
from crowdsource import CrowdSource

class Chatbot:
    def __init__(self, room_id):
        self.room_id = room_id
        self.previous_token = [] 
        #self.graph = Graph(False)
        self.inputParser = InputParser()
        #self.crowd_source = CrowdSource()
        #self.rdf_query_service = RDFQueryService(dataset.graph)
        #self.embedding_service = EmbeddingService(dataset.graph)
        #self.image_service = ImageService(dataset.graph)

    
    def getHelp(self):
        info = """
        You can ask me variety of questions such as: \n
        1) About movies: characters, genre, director, screenwriter, cast members, producer \n
        2) About people: movies, personal information, occupation, awards, birth, residence, gender \n
        3) Webpages about movies and people: wikidata pages, imdb pages \n
        4) Images: behind the scenes, events, publicity, poster, etc. \n
        5) Recommendation based on a movie, or an actor. \n
        Do not forget to evaluate my performance in the end :)
        """
        return info

    def getResponse(self, question):
        try:
            #question_type, entities, relation = self.inputParser.parse(question)

            question = self.inputParser.cleanUpInput(question)
            entities = self.inputParser.getEntities(question)
            print(entities)

            if (len(entities) >=1):
                entity1 =  entities[0]
            else:
                entity1 = None
            if (len(entities) >=2):
                entity2 =  entities[1]
            else:
                entity2 = None
            res = self.inputParser.getQuestionType(question, entity1= entity1,  entity2= entity2)
        
            if len(entities) == 0:
                return constant.DEFAULT_MESSAGE
            
            if len(entities) == 1:
                print(res)
                return "Great, %s is my favourite movie! Give me a second to check information about it. " %entities[0]
            if len(entities) == 2:
                return "Great, %s is my favourite movie! Give me a second to check information about it. hm... where is %s stored...." %(entities[0], res)
        except Exception as e:
            response = constant.DEFAULT_MESSAGE
            print("Error:", e)
    
    
def main():
    chatbot = Chatbot(1)
    question =  'What is the genre of Good Neighbours?'
    response = chatbot.getResponse(question)
    print(response)
    
    
if __name__ == "__main__":
    main()