import os
import re
import tqdm
import json
import jsonlines
import subprocess
from pathlib import Path
from colorama import Fore, Style
from os.path import splitext

import sys
sys.path.append('./')
from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response


def read_lines(text):
    """
    Split the text into lines. Remember that character '\n' is preserved, so split() and join() are not used.
    """
    buffer = ""
    ret = []
    for i in range (0, len(text)):
        buffer = buffer+text[i]
        if text[i] == "\n":
            ret.append(buffer)
            buffer = ""
        elif i == len(text) - 1:
            ret.append(buffer)
    return ret

def _insert_function(func_block, text):
    """
    Insert the function block in the designated position.
    """
    func_block = func_block + "\n" if func_block[-1]!="\n" else func_block
    text_lines = read_lines(text)
    pattern = r"\#(\s)?insert(\s|\_)here(\s)\#"

    for i, text_line in enumerate(text_lines):
        if re.search(pattern, text_line):
            if text_line[-1] != '\n':
                text_line = text_line + '\n'
            position = i
            break
    else:
        raise Exception('No matches!')

    ret_text = ''.join(text_lines[:position+1]) + func_block + ''.join(text_lines[position+1:])

    return ret_text

def insert_compile_run(args, eval_partition, test_function_name, generated_code):

    home_dir = os.path.dirname(Path(__file__).parent)
    input_data_dir = f'{home_dir}/data/input_data/{eval_partition}'
    code_destination_dir = f'{home_dir}/evaluation/evaluation_storage'
    os.makedirs(code_destination_dir, exist_ok=True)

    # insert the generated mp-spdz code into the .mpc file
    with open(os.path.join(input_data_dir, f'{test_function_name}.mpc'), 'r') as fread:
        text = fread.read()
        eval_code = _insert_function(generated_code, text)

    with open(os.path.join(code_destination_dir, f'{test_function_name}.mpc'), 'w') as fwrite:
        fwrite.write(eval_code)

    # compile and run
    compilation_run_command = f"{args.spdz_path}/Scripts/compile-run.py -E mascot {os.path.join(code_destination_dir, f'{test_function_name}.mpc')}"
    time_out, retry_cnt, retries = (60, 0, 3) if ('math' not in eval_partition and 'ufunc' not in eval_partition) else (150, 0, 3) # (90, 0, 4)
    while retry_cnt < retries:
        try:
            running_result = subprocess.run(compilation_run_command, shell=True, text=True, capture_output=True, timeout=time_out)
            break
        except subprocess.TimeoutExpired:
            print(Fore.LIGHTBLUE_EX + f'The subprocess to evaluate {test_function_name}.mpc did not complete within the timeout period ({time_out}s).' + Fore.RESET)
            time_out += 30
            print(Fore.LIGHTBLUE_EX + f'Try again with the timeout period ({time_out}s)...' + Fore.RESET)
            retry_cnt += 1

        if retry_cnt >= retries:
            print(Fore.LIGHTGREEN_EX + f'Failed to evaluate {test_function_name}.mpc for {retry_cnt} times. We directly set success to False.' + Fore.RESET)
            success = False
            return success

    stdout, stderr = running_result.stdout, running_result.stderr

    # Pass v.s. compilation and run-time error exists.
    if 'pass' in stdout.lower():
        success = True
    cr_error_exist = True if 'Traceback' in stderr.strip() else False # 不对，可能是没有cr_error程序没问题，但是实现了错误的functionality
    if cr_error_exist:
        success = False
        print('\n' + stderr.strip()+'\n')
    if (not cr_error_exist) and ('pass' not in stdout.lower()):
        print("No compilation and run-time errors. Maybe the generated code performs wrong functionality.")
        success = False

    return success

    # success = True if 'pass' in stdout.lower() else False
    # return success


def evaluate(args, spdzcode_dir='stage_2_SPDZ_output', model_name="", evaluation_file=None):
    """
    Args:
        spdzcode_dir: directory that stores the generated mp-spdz code. Defaults to 'stage_2_SPDZ_output'.
        model_name: the chat-gpt model name used in generating mp-spdz code. Defaults is "" which means that evaluation_file has no model_name as prefix.
        evaluation_file: evaluate a specific jsonl file in spdzcode_dir. Defaults to None. None, str, List evaluate all, single, part respectively.
    """
    print(Fore.RED + f'Evaluate {evaluation_file}...' + Fore.RESET)
    home_dir = os.path.dirname(Path(__file__).parent)
    evaluation_file_dir = f'{home_dir}/data/{spdzcode_dir}'
    eval_file = evaluation_file

    # eval_partition: all_rewrite_test, array_access_test, if_test, math_test...
    pattern = rf"{args.experimental}{model_name}_(.*?)\.jsonl"
    eval_partition = re.search(pattern, eval_file).group(1) if model_name else os.path.splitext(eval_file)[0][len(args.experimental):]

    # init and compute the run-time results
    results = []
    with jsonlines.open(os.path.join(evaluation_file_dir, eval_file), 'r') as reader:
        for line in reader:
            test_name = line['test_name']
            response_0 = line['response_0']
            response_1 = line['response_1']

            # insert back, compile and run
            compile_and_run_0 = insert_compile_run(args, eval_partition, test_name, response_0) if response_0 else False
            compile_and_run_1 = insert_compile_run(args, eval_partition, test_name, response_1) if response_1 else False
            print(f'{eval_partition} - {test_name} - compile_and_run_0: {compile_and_run_0}')
            print(f'{eval_partition} - {test_name} - compile_and_run_1: {compile_and_run_1}')
            result = {'test_name': f'{test_name}', 'cr_0': compile_and_run_0, 'cr_1': compile_and_run_1}

            # update run-time results
            results.append(result)

    # compute evaluation metric
    p1_counter, p2_counter = 0, 0
    average_p1_counter = 0
    total_cases = len(results)
    for result in results:
        if result['cr_0']: p1_counter += 1
        if result['cr_0'] or result['cr_1']: p2_counter += 1
        if result['cr_0']: average_p1_counter += 1
        if result['cr_1']: average_p1_counter += 1
    p1_acc = p1_counter / total_cases
    p2_acc = p2_counter / total_cases
    ave_p1_acc = average_p1_counter / (total_cases * 2)

    directory = os.path.join(Path(__file__).parent, 'baseline-evaluation') if args.eval_baseline else Path(__file__).parent
    directory = os.path.join(directory, 'naive-baseline') if 'naive-baseline' in spdzcode_dir else directory
    directory = os.path.join(directory, 'intertrans-baseline') if 'intertrans-baseline' in spdzcode_dir else directory
    directory = os.path.join(directory, 'unitrans-baseline') if 'unitrans-baseline' in spdzcode_dir else directory
    spdzcode_dir_ = spdzcode_dir.split('/')[0] if '/' in spdzcode_dir else spdzcode_dir

    # dump the run-time results
    with open(os.path.join(directory, f'{args.experimental}{spdzcode_dir_}_{splitext(eval_file)[0].removeprefix(f"{args.experimental}")}.txt'), 'w') as fw:
        for result in results:
            s = f"{result['test_name']}, {result['cr_0']}, {result['cr_1']}"
            fw.write(s + '\n')
    with open(os.path.join(directory, f'{args.experimental}{spdzcode_dir_}_{splitext(eval_file)[0].removeprefix(f"{args.experimental}")}.txt'), 'a') as fw:
        fw.write('\n' + '********'*5 + '\n\n')
        for result in results:
            print("%-30s %-10s %-10s" % (result['test_name'], result['cr_0'], result['cr_1']), file=fw)

    # dump/append the evaluation results
    with open(os.path.join(directory, f'{args.experimental}{spdzcode_dir_}_{splitext(eval_file)[0].removeprefix(f"{args.experimental}")}.txt'), 'a') as fw:
        fw.write('\n' + '********'*5 + '\n\n')
        fw.write('# of test cases : {}'.format(total_cases) + '\n')
        fw.write('# of first generation correct : {}'.format(p1_counter) + '\n')
        fw.write('# of second generation correct : {}'.format(average_p1_counter - p1_counter) + '\n\n')
        fw.write('p1_counter : {}'.format(p1_counter) + '\n')
        fw.write('p2_counter : {}'.format(p2_counter) + '\n')
        fw.write('average_p1_counter : {}'.format(average_p1_counter) + '\n\n')
        fw.write('p1_acc : {:.2%}'.format(p1_acc) + '\n')
        fw.write('p2_acc : {:.2%}'.format(p2_acc) + '\n')
        fw.write('ave_p1_acc : {:.2%}'.format(ave_p1_acc) + '\n')


if __name__ == '__main__':

    from utility.utils import parse_args
    args = parse_args()

    import time
    start_time = time.time()
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    
    
    evaluation_file = None                  # choices: str, list, or None
    # evaluation_file = ['if']


    home_dir = os.path.dirname(Path(__file__).parent)
    evaluation_file_dir = f'{home_dir}/data/{args.spdzcode_dir}'

    if evaluation_file is None:
        evaluation_file = ['if', 'for', 'array_access_traverse', 'numpy_ufunc', 'numpy_operation', 'all_rewrite', 'math']
        evaluation_file_list = [f'{args.experimental}{args.model_name}_{file}_test.jsonl' for file in evaluation_file] if args.model_name else [f'{args.experimental}{file}_test.jsonl' for file in evaluation_file]
    elif isinstance(evaluation_file, list):
        evaluation_file_list = [f'{args.experimental}{args.model_name}_{file}_test.jsonl' for file in evaluation_file] if args.model_name else [f'{args.experimental}{file}_test.jsonl' for file in evaluation_file]
    elif isinstance(evaluation_file, str):
        evaluation_file_list = [f'{args.experimental}{args.model_name}_{evaluation_file}_test.jsonl'] if args.model_name else [f'{args.experimental}{evaluation_file}_test.jsonl']
    else:
        raise NotImplementedError
    
    # evaluate: spdzcode_dir/{experimental}{model_name}_{evaluation_file}_test.
    pool_size = 7 if evaluation_file is None else len(evaluation_file_list) if isinstance(evaluation_file, list) else 1
    task_inputs = [(args, args.spdzcode_dir, args.model_name, eval_file) for eval_file in evaluation_file_list]
    
    print(Fore.GREEN + f"pool_size: {pool_size}" + Fore.RESET)

    with multiprocessing.Pool(processes=pool_size) as pool:
        pool.starmap(evaluate, task_inputs)


    end_time = time.time()
    print(f'Total time consumption: {(end_time - start_time)/60} minutes')