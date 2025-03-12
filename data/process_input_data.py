#!/usr/bin/python
# -*- encoding: utf-8 -*-

import os, sys
import json, jsonlines
import tqdm
import argparse
from pathlib import Path

file_dir = Path(__file__)
data_dir = file_dir.parent


def pipeline(split_name:str='all_rewrite_test'):

    split_dir = os.path.join(f'{data_dir}/input_data/', split_name)

    processed_split_name = f'{split_name}.json'
    processed_split_dir = f'{data_dir}/input_processed_data/'
    os.makedirs(processed_split_dir, exist_ok=True)

    # extract pair data from 'data-template' and convert them to one json file.
    entries = []
    for file_name in tqdm.tqdm(os.listdir(split_dir)):
        if '.DS_Store' in file_name:
            continue
        with open(os.path.join(split_dir, file_name), 'r') as fd:

            input, annotation, output, flag = [], [], [], 'invalid'

            for line in fd.readlines():
                if 'input:' in line:
                    flag = 'input'
                    continue
                if flag == 'input' and (not 'output:' in line) and (not 'annotation:' in line):
                    input.append(line)

                if 'annotation:' in line:
                    flag = 'annotation'
                    continue
                if flag == 'annotation' and (not 'output:' in line):
                    annotation.append(line)

                if 'output:' in line:
                    flag = 'output'
                    continue
                if flag == 'output' and (not "*'''" in line):
                    output.append(line)

                if "*'''" in line:
                    flag = 'invalid'

            instruction = 'Translate the following code snippet from Python/Numpy to MP-SPDZ.'
            input_str = ''.join(input)
            if len(annotation)==0:
                annotation_str = 'No annotation.'
            else:
                annotation_str = ''.join(annotation)
            output_str = ''.join(output)

            entry = {"test_name":file_name.split(".")[0], 'instruction':instruction, 'input': input_str, 'annotation': annotation_str, 'output': output_str}
            entries.append(entry)

    with jsonlines.open(os.path.join(processed_split_dir, processed_split_name), 'w') as writer:
        for e in entries: writer.write(e)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--split_name', type=str)
    parser.add_argument('--process_all', default=False, action='store_true')
    args = parser.parse_args()

    if args.process_all:
        for split_name in os.listdir(f'{data_dir}/input_data/'):
            if split_name == '.DS_Store':
                continue
            pipeline(split_name=split_name)
    else:
        if args.split_name:
            pipeline(split_name=args.split_name)
        else:
            pipeline()

    # Running command:
    # python data/process_input_data.py --process_all
    # python data/process_input_data.py --split_name FULL_SPLIT_NAME