import argparse
from pathlib import Path

import datasets

from funccraft.data import load_dataset, prepare, save_dataset
from funccraft.models import predict, prepare_predict

from funccraft.myField import *


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='cmd')

    default_data_path_output = Path('./output-dataset/outputPYTHON')

    prepare_data_parser = subparsers.add_parser('prepare-data')
    prepare_data_parser.set_defaults(func=prepare_data)
    prepare_data_parser.add_argument(
        '-o',
        '--output',
        help='Path to save prepared dataset to',
        type=Path,
        default=default_data_path_output,
    )
    prepare_data_parser.add_argument(
        '-s',
        '--select',
        help='How many entries use in dataset',
        type=int,
        default=1000
    )
    prepare_data_parser.add_argument(
        '-l',
        '--language',
        help='Language (python|go)',
        default='python',
    )

    predict_parser = subparsers.add_parser('predict-names')
    predict_parser.set_defaults(func=predict_names)
    predict_parser.add_argument(
        '-d',
        '--dataset',
        help='Path to prepared dataset',
        type=Path,
        default=default_data_path_output,
    )
    predict_parser.add_argument(
        '-m',
        '--model',
        default='Salesforce/codet5p-220m',
    )
    predict_parser.add_argument(
        '-l',
        '--language',
        help='Language (python|go)',
        default='python',
    )
    predict_parser.add_argument(
        '-c',
        '--comments',
        help='With comments or not',
        type=bool,
        default=False
    )

    return parser.parse_args()


def prepare_data(args):
    dataset = datasets.load_dataset(
        'code_search_net',
        args.language,
        split='test',
        trust_remote_code=True
    )
    dataset = dataset.select(range(args.select))
    print("Original func: \n", dataset[4][original_function])

    dataset = dataset.map(lambda x: prepare(x, args.language))
    print('Func_name: \n', dataset[4][NEWFunc_name])
    print('Func_body: \n', dataset[4][NEWFunc_body])
    print('Func_body_without_comment: \n', dataset[4][NEWFunc_body_without_comments])

    save_dataset(dataset, args.output)


def predict_names(args):
    dataset = load_dataset(args.dataset)
    dataset = dataset.select(range(100))

    which_field = NEWFunc_body_without_comments
    if args.comments:
        which_field = NEWFunc_body

    dataset = dataset.map(lambda x: prepare_predict(x, args.language))

    print('Func_body:')
    print(dataset[6][which_field])

    predict(dataset, which_field, args.model)


if __name__ == '__main__':
    main()
