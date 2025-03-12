
import os
import re
import sys
sys.path.append('./')
import json
import jsonlines
from colorama import Fore, Style
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM

from utility.utils import parse_args
from utility.count_tokens import num_tokens_from_messages

from evaluation import codellama_prompt, codellama_prompt_api
from evaluation import CodeLlama_Prompt, CodeLlama_Prompt_API
from evaluation import MP_SPDZ_API_DOC
from evaluation import post_process_codellama_response


def run_generate(args, init_code, model, tokenizer, prompt_template = None):

    # Encode prompts
    if prompt_template is None:
        system_content = "Translate the give Python code into MP-SPDZ code."
        user_content = f"{init_code}"
    elif isinstance(prompt_template, CodeLlama_Prompt_API):
        system_content = prompt_template.system_prompt
        user_content = prompt_template.rule_prompt.format(API_DOC=MP_SPDZ_API_DOC, CODE=init_code)
    else:
        raise ValueError("Invalid prompt type")

    # Construct message and tokenize message
    chat=[
            {"role": "system", "content": f"{system_content}"},
            {"role": "user", "content": f"{user_content}"}
        ]
    inputs = tokenizer.apply_chat_template(chat, return_tensors="pt").to("cuda")
    # Generate
    output = model.generate(input_ids=inputs,
                            do_sample=True,
                            do_sample=False,
                            top_k=50,
                            top_p=0.95,
                            num_return_sequences=1,
                            eos_token_id=tokenizer.eos_token_id,
                            max_new_tokens=1024)
    output = output[0].to("cpu")

    text_response = tokenizer.decode(output, skip_special_tokens=True)
    print(Fore.LIGHTBLUE_EX + text_response + Fore.RESET + '\n' + '*'*80)

    pattern = rf"```(\w+-*\w+)?\n(.*?)```"
    matches = re.findall(pattern, text_response, re.DOTALL)
    if not matches: print(Fore.RED + "The response from CodeLlama does not include any code." + Fore.RESET)

    # Post process the response
    spdz_code = post_process_codellama_response(text_response) if matches else ''
    print(spdz_code)

    return spdz_code



if __name__ == '__main__':

    args = parse_args()
    args.model_name = 'deepseek-ai/deepseek-coder-33b-instruct'
    print(args.model_name)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForCausalLM.from_pretrained(args.model_name,
                                                torch_dtype=torch.float16,
                                                device_map="auto")

    repetitions = 2
    filename = os.path.splitext(args.input_file)[0]
    with jsonlines.open(os.path.join(args.input_dir, args.input_file), "r") as reader:
        with open(os.path.join(args.baseline_output_dir, f'{args.experimental}{filename}.jsonl'), "w") as fw_out:

            for i, line in enumerate(reader):

                # Line item
                test_function_name = line["test_name"]
                init_code = line["input"]
                # Do inference
                SPDZ = {}
                for j in range(repetitions):

                    spdz_code = run_generate(args, init_code, model, tokenizer, prompt_template = codellama_prompt_api)
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


    # Running Command:

    # python evaluation/baseline_deepseekcoder_33b_plus.py --input_file if_test.json
    # python evaluation/baseline_deepseekcoder_33b_plus.py --input_file if_test.json --experimental deepseek-33b-w-API-1-