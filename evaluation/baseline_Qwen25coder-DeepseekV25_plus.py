
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

    response = model(prompt=user_content, system=system_content)
    text_response = model.resp_parse(response)
    # print(Fore.LIGHTBLUE_EX + text_response + Fore.RESET + '\n' + '*'*80)

    pattern = rf"```(\w+-*\w+)?\n(.*?)```"
    matches = re.findall(pattern, text_response, re.DOTALL)
    if not matches: print(Fore.RED + "The response from CodeLlama does not include any code." + Fore.RESET)
    
    # Post process the response
    spdz_code = model.code_parse(response) if matches else ''
    # print(spdz_code)

    return spdz_code



   
if __name__ == '__main__':

    args = parse_args()
    # args.model_name = 'deepseek-v2.5'
    print(args.model_name)
    
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)

    repetitions = 2
    filename = os.path.splitext(args.input_file)[0]
    import time
    start_time = time.time()
    with jsonlines.open(os.path.join(args.input_dir, args.input_file), "r") as reader:
        with open(os.path.join(args.baseline_output_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_out:

            for i, line in tqdm(enumerate(reader)):

                # Line item
                test_function_name = line["test_name"]
                init_code = line["input"]
                # Do inference
                SPDZ = {}
                for j in range(repetitions):

                    spdz_code = run_generate(args, init_code, model, prompt_template = codellama_prompt_api)
                    # Update SPDZ
                    SPDZ_entry = {f"response_{j}": spdz_code}
                    SPDZ.update(SPDZ_entry)

                # Format ouput
                SPDZ_item = {"test_name": test_function_name}
                SPDZ_item.update(SPDZ)
                SPDZ_item.update({"model_name": args.model_name})      # auxilary info: model_name

                # Dump to files
                fw_out.write(json.dumps(SPDZ_item) + "\n")
                # Hint for the user
                print(f"{i} - {test_function_name} - {args.model_name} - Done!")
                time.sleep(40)
                

    end_time = time.time()
    print(f'Total time consumption: {end_time - start_time} seconds')

    # Running Command:

    # python evaluation/baseline_Qwen25Coder-Deepseekv25_plus.py --input_file if_test.json
    # python evaluation/baseline_Qwen25Coder-Deepseekv25_plus.py --input_file if_test.json --experimental deepseek-v2.5-w-API-1-
    # python evaluation/baseline_Qwen25Coder-Deepseekv25_plus.py --input_file if_test.json --experimental deepseek-v2.5-w-API-2-


    # _plus.py : 给了API的版本