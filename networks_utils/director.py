import torch
import pandas as pd
import random
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
model_name = 'tuner007/pegasus_paraphrase'
torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)
def get_response(input_text,num_return_sequences,num_beams):
  batch = tokenizer([input_text],truncation=True,padding='longest',max_length=60, return_tensors="pt").to(torch_device)
  translated = model.generate(**batch,max_length=60,num_beams=num_beams, num_return_sequences=num_return_sequences, temperature=1.5)
  tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
  return tgt_text
num_beams = 100
num_return_sequences = 50

movies = pd.read_csv("utildata/movie_entities.csv")
list_movies = []
for index, row in movies.iterrows():
    list_movies.append(row["EntityLabel"])


director_questions1 = []
random_movies = random.sample(list_movies, 10)
for movie in random_movies:
        context = "Who is the director of %s?" %movie
        director_questions1.append([context, movie])
        res = get_response(context,num_return_sequences,num_beams)
        for r in res:
            director_questions1.append([r, movie])
director_questions1 = random.sample(director_questions1, 50)

director_questions2 = []
random_movies = random.sample(list_movies, 10)
for movie in random_movies:
        context = "Who directed %s?" %movie
        director_questions2.append([context, movie])
        res = get_response(context,num_return_sequences,num_beams)
        for r in res:
            director_questions2.append([r, movie])
director_questions2 = random.sample(director_questions1, 50)

director_questions3 = []
random_movies = random.sample(list_movies, 10)
for movie in random_movies:
        context = "Do you know who the director of %s was?" %movie
        director_questions3.append([context, movie])
        res = get_response(context,num_return_sequences,num_beams)
        for r in res:
            director_questions3.append([r, movie])
director_questions3 = random.sample(director_questions1, 50)

director_questions1.extend(director_questions2)
director_questions1.extend(director_questions3)

df = pd.DataFrame(director_questions1, columns=["questions", "entity"])
df.drop_duplicates(inplace = True)
df.to_csv("utildata/director_questions.csv", index=False)
