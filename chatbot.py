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

            entities = self.inputParser.getEntities(question)
            res = self.inputParser.getQuestionType(question)
            print(res)
            
            response = entities

            if len(entities) == 0:
                return "Sorry, I didn't understand your question. Could you please spell check and proper case movie titles and person names?"

        except Exception as e:
            response = constant.DEFAULT_MESSAGE
            print("Error:", e)
        return response
    
def main():
    chatbot = Chatbot(1)
    question =  'Who is the director of Good Will Hunting?'
    chatbot.getResponse(question)
    
    
if __name__ == "__main__":
    main()