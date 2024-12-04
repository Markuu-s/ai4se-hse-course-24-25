from collections.abc import Iterable
from pprint import pprint

import torch
from functools import lru_cache


NEWFunc_name = "NEWFunc_name"
NEWFunc_body = "NEWFunc_body"
NEWFunc_body_without_comments = "NEWFunc_body_without_comments"

import datasets
import evaluate

from transformers import AutoTokenizer, T5ForConditionalGeneration

import re

extra_id = {
    'python': 'def <extra_id_0> ():',
    'go': 'func <extra_id_0> '
}


def prepare_predict(dataset, language_str: str):
    dataset[NEWFunc_body_without_comments] = '\n'.join([extra_id[language_str], dataset[NEWFunc_body_without_comments]])
    # dataset[NEWFunc_body_without_comments] = extra_id[language_str] + dataset[NEWFunc_body_without_comments]
    dataset[NEWFunc_body] = extra_id[language_str] + dataset[NEWFunc_body]
    return dataset


def _init_metrics():
    return evaluate.load('exact_match'), evaluate.load('rouge')


def predict(dataset: datasets.Dataset, which_field: str, model_str: str) -> None:
    torch.cuda.empty_cache()
    which_device = "cuda" if torch.cuda.is_available() else "cpu"
    print(which_device)
    device = torch.device(which_device)

    tokenizer = AutoTokenizer.from_pretrained(model_str)
    model = T5ForConditionalGeneration.from_pretrained(model_str).to(device)

    inputs = tokenizer(dataset[which_field],
                       return_tensors='pt',
                       padding=True,
                       truncation=True,
                       max_length=80,
                       ).to(device)
    outputs = model.generate(**inputs, max_length=80)
    predictions = tokenizer.batch_decode(outputs, skip_special_tokens=True)

    def make_str_better(x: str):
        if x:
            x = x.split(' ')
            if len(x) > 1:
                x = x[1]
            elif len(x) == 1:
                x = x[0]
            else:
                x = ''
        re.sub(r'\W', '', x)
        if x and x[0].isdigit():
            x = '_' + x
        for i in range(len(x)):
            if not x[i].isdigit() and not x[i].isalpha() and not x[i] == '_':
                x = x[:i]
                break
        return x

    print(predictions[3])
    for i in range(len(predictions)):
        predictions[i] = make_str_better(predictions[i])

    print(len(predictions))
    print(predictions)
    print(dataset[NEWFunc_name])

    eval_results = run_evaluate(predictions=predictions, references=dataset[NEWFunc_name])
    print()
    print('*' * 80)
    print('Evaluation results:')
    pprint(eval_results)
    print('*' * 80)
    print()


def run_evaluate(
        predictions: Iterable[str], references: Iterable[str]
) -> dict[str, float]:
    em, rouge = _init_metrics()
    em_score = em.compute(predictions=predictions, references=references)
    rouge_scores = rouge.compute(predictions=predictions, references=references)

    return {**rouge_scores, **em_score}
