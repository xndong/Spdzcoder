import json
import jsonlines
import tqdm
import os
import time
from datetime import datetime
from colorama import Fore, Style
# import random

import sys
sys.path.append('./')
from utility.utils import parse_args
from apply_high_rules import apply_stage_1_rules
from apply_low_rules import apply_stage_2_rules
from apply_feedback_tc import run_feedback

import multiprocessing

date_and_time = datetime.now()
mdHM = date_and_time.strftime("%m_%d-%H_%M")

def process_line(args, repetitions, line):

    # line item
    test_function_name = line["test_name"]
    init_code = line["input"]

    # do inference
    IR = {}
    SPDZ = {}
    result = {}
    for j in range(repetitions):

        print(Fore.GREEN + '\n' + '###'*10 + f'  Test function: {test_function_name} - Repetition j={j} starts  ' + '###'*10 + '\n' + Style.RESET_ALL)

        # Stage 1: 
        print(Fore.GREEN + 'Start Stage 1'+'>>>>>'*10 + '\n' + Style.RESET_ALL)
        python_IR, prompt_token_consumption_1, completion_token_consumption_1 = apply_stage_1_rules(args, init_code)

        # Stage2: 
        print(Fore.GREEN + 'Start Stage 2'+'>>>>>'*10 + '\n' + Style.RESET_ALL)
        model_in_stage2 = args.model_name 
        spdz_code, prompt_token_consumption_2, completion_token_consumption_2, cot_chat_message = apply_stage_2_rules(args, python_IR)

        # Stage 3: whether to use feedback, default is False unless use --feedback_flag in command.
        output, prompt_token_consumption_3, completion_token_consumption_3 = run_feedback(args, test_function_name, python_IR, spdz_code, cot_chat_message=cot_chat_message) if args.feedback_flag else (' ', 0 , 0)

        # Update IR
        IR_entry = {f"response_{j}": python_IR, f"prompt_token_{j}": prompt_token_consumption_1, f"completion_token_{j}":completion_token_consumption_1}
        IR.update(IR_entry)
        # Update SPDZ
        SPDZ_entry = {f"response_{j}": spdz_code, f"prompt_token_{j}": prompt_token_consumption_2, f"completion_token_{j}":completion_token_consumption_2}
        SPDZ.update(SPDZ_entry)
        # Update result
        result_entry = {f"response_{j}": output, f"prompt_token_{j}": prompt_token_consumption_3, f"completion_token_{j}":completion_token_consumption_3}
        result.update(result_entry)

    # Format ouput
    IR_item = {"test_name": test_function_name}
    IR_item.update(IR)
    SPDZ_item = {"test_name": test_function_name}
    SPDZ_item.update(SPDZ)
    SPDZ_item.update({"model_in_stage2": model_in_stage2, "current_stage": "stage_2"})      # auxilary info: model_name, current stage
    result_item = {"test_name": test_function_name}
    result_item.update(result)
    result_item.update({"model_in_stage3": args.model_name, "current_stage": "stage_3"})    # auxilary info: model_name, current stage

    return IR_item, SPDZ_item, result_item



if __name__ == "__main__":

    args = parse_args()

    os.makedirs(args.stage_1_IR_dir, exist_ok=True)
    os.makedirs(args.stage_2_SPDZ_dir, exist_ok=True)
    os.makedirs(args.stage_3_output_dir, exist_ok=True)
    assert args.input_file.endswith(".jsonl") or args.input_file.endswith(".json")

    start_time = time.time()
    repetitions = 2
    filename = os.path.splitext(args.input_file)[0]
    
    with jsonlines.open(os.path.join(args.input_dir, args.input_file), "r") as reader:
        task_inputs = [(args, repetitions, line) for i, line in enumerate(reader)]  
    with multiprocessing.Pool(processes=16) as pool:
        RESULTS = pool.starmap(process_line, task_inputs)
            
            
    with open(os.path.join(args.stage_1_IR_dir, f'{args.experimental}{filename}_{args.IR_file}'), "w") as fw_IR:
        with open(os.path.join(args.stage_2_SPDZ_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_SPDZ:
            with open(os.path.join(args.stage_3_output_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_out:
                for IR_item, SPDZ_item, result_item in RESULTS:
                    # Dump to files
                    fw_IR.write(json.dumps(IR_item) + "\n")
                    fw_SPDZ.write(json.dumps(SPDZ_item) + "\n")
                    fw_out.write(json.dumps(result_item) + "\n")

    end_time = time.time()
    print(f'Total time consumption: {end_time - start_time} seconds')