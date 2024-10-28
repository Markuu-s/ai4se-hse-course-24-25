from pathlib import Path

import datasets
import pandas as pd

import re, string
import contractions

from nltk import word_tokenize, sent_tokenize, download
from nltk.corpus import stopwords
import random

download('stopwords')
download('punkt')
download('punkt_tab')


def prepare(raw_data: Path) -> datasets.Dataset:
    dataset = pd.read_excel(raw_data)
    dataset = dataset.dropna()
    
    dataset["message"] = datset["message"].apply(lambda sample: process(sample))
    dataset["message"] = dataset["message"].apply(lambda x: ' '.join(x))
    dataset["message"] = dataset["message"][dataset["message"].apply(len) > 0]
    dataset = dataset.drop_duplicates(subset=["message"])
    
    return datasets.Dataset.from_pandas(dataset)


def load_dataset(path: Path) -> datasets.Dataset:
    return datasets.load_from_disk(str(path))


def save_dataset(dataset: datasets.Dataset, path: Path) -> None:
    dataset.save_to_disk(str(path))
    
    
url_regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
def process(data):
    data = url_regex.sub(" ", data) # urls    
    data = data.lower()

    
    data = re.compile(r"(.)\1{2,}", re.DOTALL).sub(r"\1", data) # remove repeated
    
    for target, patterns in RE_PATTERNS.items():
        for pat in patterns:
            data = re.sub(pat, target, data)
            
    data = re.sub(r"[^a-z' ]", ' ', data)
    
    data = contractions.fix(data)
    data = re.compile('([^\s\w]|_)+').sub(' ', data)

    
    data = word_tokenize(data)
    return [word for word in data if word not in stopwords.words('english')]


        
     
    
