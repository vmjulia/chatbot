import json
import time
import atexit
import getpass
import requests  # install the package via "pip install requests"
from collections import defaultdict
from chatbot import Chatbot
import constant
import time
from transformers import pipeline

# url of the speakeasy server
url = 'https://server5.speakeasy-ai.org'
listen_freq = 3


class Agent:
    def __init__(self, login):
        with open("./credentials.json", "r") as f:
         credentials = json.load(f)
        username = credentials["agent"]["username"]
        password = credentials["agent"]["password"]
        self.agent_details = self.login(username, password)
        self.session_token = self.agent_details['sessionToken']
        self.chat_state = defaultdict(lambda: {'messages': defaultdict(dict), 'initiated': False, 'my_alias': None})
        self.chatbots = {}
        self.login = login
        atexit.register(self.logout)
        
        self.cloassifier = pipeline("zero-shot-classification")
        self.ner = pipeline('ner', model='dbmdz/bert-large-cased-finetuned-conll03-english')
        

    def listen(self):
        while True:
            # check for all chatrooms
            current_rooms = self.check_rooms(session_token=self.session_token)['rooms']
            for room in current_rooms:
                # ignore finished conversations
                if room['remainingTime'] > 0:
                    room_id = room['uid']
                    if not self.chat_state[room_id]['initiated']:
                        # send a welcome message and get the alias of the agent in the chatroom
                        self.post_message(room_id=room_id, session_token=self.session_token, message='Hi, I am a movie specialist. I can help you with any questions you have about movies, recommend you some based on your preferences and show pictures. Since I am very smart and know so much give me a few seconds to prepare and we can start:) You can send your question already')
                        self.chat_state[room_id]['initiated'] = True
                        self.chat_state[room_id]['my_alias'] = room['alias']
                        self.chatbots[room_id] = Chatbot(room_id, classifier=self.cloassifier, ner_pipeline=self.ner) # create an instance of chatbot for that room

                    # check for all messages
                    all_messages = self.check_room_state(room_id=room_id, since=0, session_token=self.session_token)['messages']

                    # you can also use ["reactions"] to get the reactions of the messages: STAR, THUMBS_UP, THUMBS_DOWN

                    for message in all_messages:
                        if message['authorAlias'] != self.chat_state[room_id]['my_alias']:

                            # check if the message is new
                            if message['ordinal'] not in self.chat_state[room_id]['messages']:
                                # if logout happened, dont answer on all the questions all over again
                              if (self.login is None) or (self.login is not None and message["timeStamp"]>self.login):
                                self.chat_state[room_id]['messages'][message['ordinal']] = message
                                
                                print('\t- Chatroom {} - new message #{}: \'{}\' - {}'.format(room_id, message['ordinal'], message['message'], self.get_time()))

                                ##### You should call your agent here and get the response message #####
                                try:
                                    flag, response,  predicate, matches, matched_predicate,types  = self.chatbots[room_id].getResponse(message["message"])
                                    if flag:
                                        self.post_message(room_id=room_id, session_token=self.session_token, message=response)
                                        response = self.chatbots[room_id].getResponseFinal(predicate, matches, matched_predicate,types, message["message"])              
                                except:
                                    response = "Sorry, I did not understand that. Please rephrase the question for me!"    
                                self.post_message(room_id=room_id, session_token=self.session_token, message=response)
                                
            time.sleep(listen_freq)

    def login(self, username: str, password: str):
        agent_details = requests.post(url=url + "/api/login", json={"username": username, "password": password}).json()
        print('- User {} successfully logged in with session \'{}\'!'.format(agent_details['userDetails']['username'], agent_details['sessionToken']))
        return agent_details

    def check_rooms(self, session_token: str):
        return requests.get(url=url + "/api/rooms", params={"session": session_token}).json()

    def check_room_state(self, room_id: str, since: int, session_token: str):
        return requests.get(url=url + "/api/room/{}/{}".format(room_id, since), params={"roomId": room_id, "since": since, "session": session_token}).json()

    def post_message(self, room_id: str, session_token: str, message: str):
        
        message = message.encode(encoding='utf-8')
        tmp_des = requests.post(url=url + "/api/room/{}".format(room_id),
                                params={"roomId": room_id, "session": session_token}, data=message).json()
        if tmp_des['description'] != 'Message received':
            print('\t\t Error: failed to post message: {}'.format(message))

    def get_time(self):
        return time.strftime("%H:%M:%S, %d-%m-%Y", time.localtime())

    def logout(self):
        if requests.get(url=url + "/api/logout", params={"session": self.session_token}).json()['description'] == 'Logged out':
            print('- Session \'{}\' successfully logged out!'.format(self.session_token))


if __name__ == '__main__':
    login = None
    for k in range(5):       
        try:
                agent = Agent(login)
                agent.listen()
        except Exception as e:
            if e is KeyboardInterrupt:
                exit()     
            print("it is logging in again!!!")
            login = time.time()
            
