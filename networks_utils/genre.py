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
num_beams = 200
num_return_sequences = 50

movies = pd.read_csv("utildata/movie_entities.csv")
list_movies = []
for index, row in movies.iterrows():
    list_movies.append(row["EntityLabel"])


director_questions1 = []
random_movies = random.sample(list_movies, 10)
for movie in random_movies:
        context = "What is the genre of %s?" %movie
        res = get_response(context,num_return_sequences,num_beams)
        for r in res:
            director_questions1.append(r)
director_questions1 = random.sample(director_questions1, 100)

director_questions3 = []
random_movies = random.sample(list_movies, 10)
for movie in random_movies:
        context = "Do you know what the genre of %s is?" %movie
        res = get_response(context,num_return_sequences,num_beams)
        for r in res:
            director_questions3.append(r)
director_questions3 = random.sample(director_questions1, 100)

director_questions = list(set(director_questions1).union(set(director_questions3)))

df = pd.DataFrame(director_questions, columns=["questions"])
print(df)
df.to_csv("utildata/director_questions.csv", index=False)
