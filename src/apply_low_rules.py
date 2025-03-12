import os
import re
import sys
sys.path.append('./')
from colorama import Fore, Style

from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response
# general purpose rule: translation
from low_semantic_rules import lo_chain_of_thought_rule
from low_semantic_rules import lo_self_reflection_rule

from low_semantic_rules.lo_chain_of_thought_rule import ChainOfThoughtTranslation
from low_semantic_rules import selectchatmessage, pattern_match, logic_operation_visitor, ast
from utility.model_msg import load_model
import inspect

def apply_stage_2_rules(args, init_code):                               #* init_code is python_IR from last stage.

    # initialization
    code_snippet = init_code
    prompt_token_consumption, completion_token_consumption = 0, 0
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    # low-level semantic rules
    L_semantic_rules_list = [lo_chain_of_thought_rule, lo_self_reflection_rule]
    # main procedure
    for semantic_rule in L_semantic_rules_list:

        # Simplely choose all instances
        rule_instances = semantic_rule.rule_instances
        print(Fore.GREEN + f'Low: there are {len(rule_instances)} instances in rule_instances from {semantic_rule.__name__}' + Fore.RESET)

        for rule_instance in rule_instances:

            # Encode prompts
            system_content = rule_instance.system_prompt
            user_content = rule_instance.rule_prompt.format(CODE=code_snippet)
            messages=[
                    {"role": "system", "content": f"{system_content}"},
                    {"role": "user", "content": f"{user_content}"}
                ]

            if isinstance(rule_instance, ChainOfThoughtTranslation):
                system_content = rule_instance.system_prompt
                user_content = rule_instance.rule_prompt.format(CODE=code_snippet)
                # Dynamically choose chat messages
                messages=[
                        {"role": "system", "content": f"{system_content}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_1}"},
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_1}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_2}"},
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_2}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_3}"},
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_3}"},
                    ]   # warmup messages

                candidate_messages = [
                        {"role": "user", "content": f"{rule_instance.user_prompt_4}"},              # logic OP
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_4}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_5}"},              # math
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_5}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_6}"},              # array
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_6}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_7}"},              # clear Branch and Jump
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_7}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_8}"},              # data type
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_8}"},
                        {"role": "user", "content": f"{rule_instance.user_prompt_9}"},              # MemValue
                        {"role": "assistant", "content": f"{rule_instance.assistant_response_9}"}
                    ]

                # Select matched chat messages
                def chat_message_match(args, candidate_messages, selectchatmessage, code_snippet):

                    chosen_messages = []
                    try:
                        parsed_code = ast.parse(code_snippet)
                        logic_operation_visitor.visit(parsed_code)
                        if logic_operation_visitor.found_logic_operations:
                            chosen_messages.append(candidate_messages[0])
                            chosen_messages.append(candidate_messages[1])
                    except SyntaxError:
                        print(Fore.RED + "There exists identifier that violates the Python abstract grammer in code_snippet." + Fore.RESET)
                        pass
                    if pattern_match(args, selectchatmessage.system_prompt, selectchatmessage.user_math_prompt, code_snippet):
                        chosen_messages.append(candidate_messages[2])
                        chosen_messages.append(candidate_messages[3])
                    if pattern_match(args, selectchatmessage.system_prompt, selectchatmessage.user_array_prompt, code_snippet):
                        chosen_messages.append(candidate_messages[4])
                        chosen_messages.append(candidate_messages[5])
                    if 'clear' in code_snippet.lower():
                        chosen_messages.append(candidate_messages[6])
                        chosen_messages.append(candidate_messages[7])
                    # Always pop data type message (4th) and remain the MemValue message (5th)
                    chosen_messages.append(candidate_messages[8])
                    chosen_messages.append(candidate_messages[9])

                    return chosen_messages

                chosen_messages = chat_message_match(args, candidate_messages, selectchatmessage, code_snippet)
                messages.extend(chosen_messages)
                # Append user content
                user_message = [{"role": "user", "content": f"{user_content}"}]
                messages.extend(user_message)

                # Deep copy CoT messages
                import copy
                cot_chat_message = copy.deepcopy(messages)

            for i in range(3):
                # Make request
                response = model(messages)

                # Check whether the post response includes code snippet.
                pattern = r"```(\w+-*\w+)?\n(.*?)```"
                text = response.choices[0].message.content
                matches = re.findall(pattern, text, re.DOTALL)
                if matches:
                    break
                else:
                    print(Fore.RED + f"The response from {inspect.currentframe().f_code.co_name} does not include code. Try again..." + Fore.RESET)
                    

            # Post process the response
            post_response = post_process_response(response) if matches else code_snippet

            # Update current code snippet
            code_snippet = post_response

            # # Print the modified code
            # print('='*80)
            # print(code_snippet)
            # print('='*80 + '\n')

            # Compute token consumption
            prompt_token_consumption += response.usage.prompt_tokens
            completion_token_consumption += response.usage.completion_tokens

    spdz_code = code_snippet
    # return spdz_code
    return spdz_code, prompt_token_consumption, completion_token_consumption, cot_chat_message



if __name__ == '__main__':

    from utility.utils import parse_args
    args = parse_args()
    args.model_name = 'gpt-4-1106-preview'
    args.model_name = 'gpt-4-turbo-2024-04-09'
    args.model_name = 'azure-gpt4'
    print(args.model_name)
    
    init_code = \
"""
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Manually adjust the arrays to 2D if necessary and concatenate along the new axis
a_2d = a[np.newaxis, :]  # Adds a new axis, effectively reshaping a to 2D without using reshape
b_2d = b[np.newaxis, :]  # Does the same for b

# Use concatenate to achieve the stack effect along axis 0
array = np.concatenate((a_2d, b_2d), axis=0)
"""
    apply_stage_2_rules(args, init_code)