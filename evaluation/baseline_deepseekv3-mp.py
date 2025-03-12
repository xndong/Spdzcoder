import os
import re
import json
import jsonlines
import tqdm
import sys
sys.path.append('./')
from colorama import Fore, Style

from utility.utils import parse_args
from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response
from utility.model import load_model

from evaluation import MP_SPDZ_API_DOC

#**************** prompt ****************#
summarization_system_prompt = \
"""
You are an expert to write Python, and you are good at describing/explaining a Python program to other people.
"""
summarization_user_prompt = \
"""
Following is a piece of python code and some annotations about it. Your task is to describe the semantic of the code, i.e., you describe/explain the functionality of the code in natural languge within 5 sentences.
For functions defined in the code, you should summarize its inputs, outputs and functionalities.
For cirtical global variables in the code, you should summarize their names and usages.

Let us try with the following python code snippet.
```
{CODE}
```
"""



generation_system_prompt = \
"""
You are an expert to write MP-SPDZ program and you are familar with the differences between Python and MP-SPDZ. Thus, you think carefully before you write MP-SPDZ program. In addtion, you are very smart to refer the above/aforementioned external knowledge.
"""

generation_user_prompt = \
"""
This the MP-SPDZ API document:
{API_DOC}

The following is a python function and its semantic description. Your task is to implement/write a piece of code under MP-SPDZ framework according to the description. You should refer to the given MP-SPDZ API document above and write the code carefully.
The Python code is as follows:
```python
{CODE}
```
The semantic description of the code is here:
"
{DESCPRIPTION}
"
When you implement/write the MP-SPDZ code, you are supposed to follow the below requirements:
1. The code you write must have the same functionality as the original code. The critical parameters or variables must keep the same name.
2. You should use the types and methods of the MP-SPDZ framework correctly to rewrite the code. For example, you should change the `list` type into `Array` type.
3. All variables should be viewed as ciphertext variables, and you should turn them into secret types in MP-SPDZ and should not reveal them.
4. You only need to guarantee the functionality of the code you write matches the input code, and you don't have to align the implementation between the input and your answer.
"""
#**************** prompt end ****************#

def summarize_semantics(args, python_code):

    # load model
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)

    # encode prompts
    system_content = summarization_system_prompt
    user_content = summarization_user_prompt.format(CODE=python_code)

    # make request
    response = model(prompt=user_content, system=system_content)

    # post process the response
    text = model.resp_parse(response)
    semantic_description = text

    # Compute token consumption
    prompt_token_consumption = response.usage.prompt_tokens
    completion_token_consumption = response.usage.completion_tokens

    return semantic_description, prompt_token_consumption, completion_token_consumption


def generate_spdz_code(args, python_code, semantic_description):

    # load model
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    
    # encode prompts
    system_content = generation_system_prompt
    user_content = generation_user_prompt.format(API_DOC=MP_SPDZ_API_DOC, CODE=python_code, DESCPRIPTION=semantic_description)

    for i in range(3):
        # make request
        response = model(prompt=user_content, system=system_content)

        # check whether the post response includes code snippet.
        pattern = r"```(\w+)?\s*(.*?)```"
        text = model.resp_parse(response)
        # print(Fore.GREEN + text + Style.RESET_ALL)
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            break
        else:
            print(Fore.RED + f"The response from {args.model_name} does not include any code block. Let us try again..." + Style.RESET_ALL)
            continue

    if i == 2 and (not matches):
        raise Exception("Wrong generation after trying 3 times!")

    # post process the response
    spdz_code = model.code_parse(response)

    # Compute token consumption
    prompt_token_consumption = response.usage.prompt_tokens
    completion_token_consumption = response.usage.completion_tokens

    return spdz_code, prompt_token_consumption, completion_token_consumption


def process_line(i, line, args, repetitions):
    # Line item
    test_function_name = line["test_name"]
    init_code = line["input"]
    # Do inference
    result = {}
    for j in range(repetitions):

        semantic_description, ptc_summarize, ctc_summarize = summarize_semantics(args, init_code)
        spdz_code, ptc_generate, ctc_generate = generate_spdz_code(args, init_code, semantic_description)

        # Update token consumption
        prompt_token_consumption = ptc_summarize + ptc_generate
        completion_token_consumption = ctc_summarize + ctc_generate
        # Update result
        result_entry = {f"response_{j}": spdz_code, f"prompt_token_{j}": prompt_token_consumption, f"completion_token_{j}":completion_token_consumption}
        result.update(result_entry)

    # Format output
    result_item = {"test_name": test_function_name}
    result_item.update(result)
    result_item.update({"model_name": args.model_name})    # auxilary info: model_name
    # Provide feedback to the user
    print(f"{i} - {test_function_name} - {args.model_name} - Done!")

    return result_item


if __name__ == '__main__':


    args = parse_args()
    # args.model_name = 'deepseek-v3'
    print(args.model_name) 

    assert args.input_file.endswith(".jsonl") or args.input_file.endswith(".json")
    import time
    start_time = time.time()
    repetitions = 2
    filename = os.path.splitext(args.input_file)[0]
    with jsonlines.open(os.path.join(args.input_dir, args.input_file), "r") as reader:
        task_inputs = [(i, line, args, repetitions) for i, line in enumerate(reader)]
        
    import multiprocessing
    multiprocessing.set_start_method('spawn')
    with multiprocessing.Pool(processes=min(max(12, multiprocessing.cpu_count()//2),24))  as pool:
        SPDZ_items = pool.starmap(process_line, task_inputs)
        
    
    # Dump to files
    with open(os.path.join(args.baseline_output_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_out:
        for SPDZ_item in SPDZ_items:
            fw_out.write(json.dumps(SPDZ_item) + "\n")


    end_time = time.time()
    print(f'Total time consumption: {end_time - start_time} seconds')
    

    # Running Command:
    # python evaluation/baseline_deepseekv3-mp.py --input_file if_test.json
    # python evaluation/baseline_deepseekv3-mp.py --input_file if_test.json --experimental deepseek-v3-1-
    # python evaluation/baseline_deepseekv3-mp.py --input_file if_test.json --experimental deepseek-v3-2-