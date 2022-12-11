# intentions
UNKNOWN = -1
GREETING = 0
GOODBYE = 1
LOCATION = 2
TIME = 3
PERSON = 4
RECOMMENDATION = 5
IMAGE = 6

DEFAULT_MESSAGE = 'Sorry, I did not understand that. Could you please rephrase the question and make sure that the spelling is correct!'
DID_NOT_FIND_ANSWER = ['There was no answer to your question in the initial graph, but I also checked crowdsourcing data! ', 'The initially given knowledge graph does not contain this info, but I also checked crowdsourcing data! ', 'I could not find anyhting stored in the knowledge graph given to us, but I also checked crowdsourcing data! ' ]
SINGLE_ANSWER = ['Great, I have found an answer to your question. It is ', 'The answer is ', 'It is ' ]
MULTIPLE_ANSWER = ['The answers that I found are ', 'The results of my search are ']
CANDIDATE_LABELS_MOVIE = ["character", "genre", "director", "screenwriter", "cast", "producer", "personal information", "occupation", "award", "birth", "residence", "gender", "movie"]

#CANDIDATE_LABELS_HUMAN = ["personal information", "occupation", "award", "birth", "residence", "gender", "movie"]