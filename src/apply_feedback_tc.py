import os
import re
import subprocess
import sys
sys.path.append('./')
from colorama import Fore, Style
from pathlib import Path

from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response

from feedback_rule import use_cr_error
from feedback_rule import use_functionality_message
from utility.model_msg import load_model
import inspect


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
    time_out, retry_cnt, retries = (60, 0, 4)  if ('math' not in eval_partition and 'ufunc' not in eval_partition) else (150, 0, 3) # (90, 0, 4)
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
            message = "Warning:: No compilation and run-time errors. This indicates the generated code performs wrong functionality. You must translate the code from Python to MP-SPDZ again!"
            return success, message

    stdout, stderr = running_result.stdout, running_result.stderr

    # Pass v.s. compilation and run-time error exists.
    if 'pass' in stdout.lower():
        success = True
        message = None
    cr_error_exist = True if 'Traceback' in stderr.strip() else False 
    if cr_error_exist:
        # print('\n' + stderr.strip() + '\n')
        success = False
        message = stderr
    if (not cr_error_exist) and ('pass' not in stdout.lower()):
        success = False
        message = "Warning:: No compilation and run-time errors. This indicates the generated code performs wrong functionality. You must translate the code from Python to MP-SPDZ again!"

    return success, message


def run_feedback(args, test_function_name, python_code, spdz_code, cot_chat_message=None):

    current_spdz_code = spdz_code
    eval_partition = os.path.splitext(args.input_file)[0]
    success, message = insert_compile_run(args, eval_partition, test_function_name, spdz_code)

    if (message is not None) and 'Traceback' in message.strip():
        print('\nCompilation and Runtime - type error\n')
    elif (message is not None) and'Warning::' in message:
        print('\nFunctionality - type error\n')
    print('*'*80 + '\n')

    prompt_token_consumption, completion_token_consumption = 0, 0
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    for k in range(args.max_feedback):

        if success:
            return current_spdz_code, prompt_token_consumption, completion_token_consumption

        print(Fore.GREEN + f'The {k+1} time to try to fix bugs/wrong functionality...' + Fore.RESET)
        current_spdz_code = spdz_code

        # Encode prompts
        if 'Traceback' in message.strip():
            system_content = use_cr_error.fix_cr_error.system_prompt
            user_content = use_cr_error.fix_cr_error.rule_prompt.format(PYTHON_CODE=python_code, SPDZ_CODE=current_spdz_code, COMPILATION_RUNTIME_ERROR=message)
        elif 'Warning::' in message:
            system_content = use_functionality_message.fix_functionality_error.system_prompt
            user_content = use_functionality_message.fix_functionality_error.rule_prompt.format(PYTHON_CODE=python_code, SPDZ_CODE=current_spdz_code)
        else:
            raise NotImplementedError

        messages=[
            {"role": "system", "content": f"{system_content}"},
            {"role": "user", "content": f"{user_content}"}
        ]

        # Insert CoT chat history
        if cot_chat_message:
            messages[1:1] = cot_chat_message[1:-1]

        for i in range(3):
            # Make request
            response = model(messages)

            # Check whether the post response includes code snippet.
            pattern = r"```(\w+-*\w+)?\s*(.*?)```"
            text = response.choices[0].message.content
            matches = re.findall(pattern, text, re.DOTALL)
            if matches:
                break
            else:
                print(Fore.GREEN + f"The response from {inspect.currentframe().f_code.co_name} does not include any code block. Try again..." + Fore.RESET)
                continue

        if matches:
            # Post process the response
            current_spdz_code = post_process_response(response)
        else:
            continue

        # # Print the modified code
        # print('='*80)
        # print(current_spdz_code)
        # print('='*80 + '\n')

        # Compute token consumption
        prompt_token_consumption += response.usage.prompt_tokens
        completion_token_consumption += response.usage.completion_tokens

        # Self-reflection
        from low_semantic_rules import lo_self_reflection_rule

        system_content = lo_self_reflection_rule.self_reflection.system_prompt
        user_content = lo_self_reflection_rule.self_reflection.rule_prompt.format(CODE=current_spdz_code)
        messages=[
            {"role": "system", "content": f"{system_content}"},
            {"role": "user", "content": f"{user_content}"}
        ]

        for i in range(3):
            response = model(messages)

            text = response.choices[0].message.content
            matches = re.findall(pattern, text, re.DOTALL)
            if matches: 
                current_spdz_code = post_process_response(response)
                break

        # Compile and run with current_spdz_code
        success, _message = insert_compile_run(args, eval_partition, test_function_name, current_spdz_code)

        # Compute token consumption
        prompt_token_consumption += response.usage.prompt_tokens
        completion_token_consumption += response.usage.completion_tokens


    if success:
        return current_spdz_code, prompt_token_consumption, completion_token_consumption
    else:
        return spdz_code, prompt_token_consumption, completion_token_consumption