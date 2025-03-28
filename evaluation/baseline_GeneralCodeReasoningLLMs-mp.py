
import os
import re
import sys
sys.path.append('./')
import json
import jsonlines
from colorama import Fore, Style

from utility.utils import parse_args
from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response
from utility.model import load_model

from evaluation import codellama_prompt, codellama_prompt_api
from evaluation import CodeLlama_Prompt, CodeLlama_Prompt_API
from evaluation import MP_SPDZ_API_DOC
from evaluation import post_process_codellama_response

from tqdm import tqdm

def run_generate(args, init_code, model, prompt_template = None):

    # Encode prompts
    if prompt_template is None:
        # system_content = "Translate the give Python code into MP-SPDZ code."
        system_content = "You are a helpful and honest code assistant expert in writing MP-SPDZ promgram. When you translate a Python Program into MP-SPDZ, you will consider their differences in expressing semantics and try to solve the code translation task step by step.\nYou must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!"
        user_content = f"{init_code}"
    elif isinstance(prompt_template, CodeLlama_Prompt_API):
        system_content = prompt_template.system_prompt
        user_content = prompt_template.rule_prompt.format(API_DOC=MP_SPDZ_API_DOC, CODE=init_code)
    else:
        raise ValueError("Invalid prompt type")

    for i in range(3):
        response = model(prompt=user_content, system=system_content)
        text_response = model.resp_parse(response)
        # print(Fore.LIGHTBLUE_EX + text_response + Fore.RESET + '\n' + '*'*80)

        pattern = rf"```(\w+-*\w+)?\n(.*?)```"
        matches = re.findall(pattern, text_response, re.DOTALL)
        if matches: 
            break
        else:
            print(Fore.RED +f"The response from run_generate does not include pattern-match response. Try again..." + Fore.RESET)
    
    # Post process the response
    spdz_code = model.code_parse(response) if matches else ''
    # print(spdz_code)

    return spdz_code



def process_line(i, line, args, repetitions):
    # Load the model
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    # Line item
    test_function_name = line["test_name"]
    init_code = line["input"]
    # Do inference
    SPDZ = {}
    for j in range(repetitions):
        spdz_code = run_generate(args, init_code, model, prompt_template=None)
        SPDZ_entry = {f"response_{j}": spdz_code}
        SPDZ.update(SPDZ_entry)

    # Format output
    SPDZ_item = {"test_name": test_function_name}
    SPDZ_item.update(SPDZ)
    SPDZ_item.update({"model_name": args.model_name})  # auxiliary info: model_name

    # Provide feedback to the user
    print(f"{i} - {test_function_name} - {args.model_name} - Done!")

    return SPDZ_item

if __name__ == '__main__':
    
    args = parse_args()
    # args.model_name = 'deepseek-v2.5'
    print(args.model_name)    
    
    repetitions = 2
    filename = os.path.splitext(args.input_file)[0]
    import time
    start_time = time.time()
    # Read input file and create a pool of processes
    with jsonlines.open(os.path.join(args.input_dir, args.input_file), "r") as reader:
        # Prepare the arguments for each line
        task_inputs = [(i, line, args, repetitions) for i, line in enumerate(reader)]
        
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    with multiprocessing.Pool(processes=min(max(12, multiprocessing.cpu_count()//2),24))  as pool:
        SPDZ_items = pool.starmap(process_line, task_inputs)


    # Dump to files
    args.baseline_output_dir = os.path.join(args.baseline_output_dir, 'naive-baseline')
    with open(os.path.join(args.baseline_output_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_out:
        for SPDZ_item in SPDZ_items:
            fw_out.write(json.dumps(SPDZ_item) + "\n")


    end_time = time.time()
    print(f'Total time consumption: {end_time - start_time} seconds')




    # Running Command:

    # python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py --input_file if_test.json
    # python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py --input_file if_test.json --experimental deepseek-v2.5-wo-API-1-
    # python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py --input_file if_test.json --experimental deepseek-v2.5-wo-API-2-


    # _plus.py : 给了API的版本