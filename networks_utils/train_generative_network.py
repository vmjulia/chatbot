from transformers import pipeline
import pandas as pd



generation_pipeline = pipeline("text-generation", model='eugenesiow/bart-paraphrase')
res = generation_pipeline("Who is the director of Good Will Hunting?")
print(res)