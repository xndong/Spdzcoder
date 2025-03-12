import os
import re
import sys
sys.path.append('./')
from colorama import Fore, Style

from utility.count_tokens import num_tokens_from_messages
from utility.gpt_chat_api import make_requests, post_process_response


from high_semantic_rules import hi_DS_method_Syntax_sugar_rule
from high_semantic_rules import hi_array_creation_indexing_manipulation_rule
from high_semantic_rules import hi_math_ufunc_rule
from high_semantic_rules import hi_while_loop_rule
from high_semantic_rules import hi_ocf_break_continue_rule
from high_semantic_rules import hi_ocf_branch_rule
from high_semantic_rules import hi_ocf_ORAM_rule

from high_semantic_rules.hi_array_creation_indexing_manipulation_rule import ElimininateAdvancedArrayOperations
from utility.model_msg import load_model
import inspect

def apply_stage_1_rules(args, init_code):

    # initialization
    code_snippet = init_code
    prompt_token_consumption, completion_token_consumption = 0, 0
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    # high-level semantic rules 
    H_semantic_rules_list = [hi_math_ufunc_rule,
                             hi_DS_method_Syntax_sugar_rule,
                             hi_while_loop_rule,
                             hi_ocf_break_continue_rule,
                             hi_ocf_branch_rule,
                             hi_array_creation_indexing_manipulation_rule,
                            #  hi_ocf_ORAM_rule,
                             ]
    # main procedure
    for semantic_rule in H_semantic_rules_list:

        # Dynamically choose instances
        rule_instances = semantic_rule.pattern_match(code_snippet)
        if not rule_instances: # empty list
            print(Fore.GREEN + f'High: there are 0 instances in rule_instances from {semantic_rule.__name__}, indicating that we skip a rule.\n' + Fore.RESET)
            continue
        else:
            print(Fore.GREEN + f'High: there are {len(rule_instances)} instances in rule_instances from {semantic_rule.__name__}' + Fore.RESET)
            for rule_instance in rule_instances:

                # Encode prompts
                system_content = rule_instance.system_prompt
                user_content = rule_instance.rule_prompt.format(CODE=code_snippet)
                messages=[
                        {"role": "system", "content": f"{system_content}"},
                        {"role": "user", "content": f"{user_content}"}
                    ]
                # Encode prompts for Numpy array
                if isinstance(rule_instance, ElimininateAdvancedArrayOperations):
                    system_content = rule_instance.system_prompt
                    user_content = rule_instance.rule_prompt.format(CODE=code_snippet)
                    messages=[
                            {"role": "system", "content": f"{system_content}"},
                            {"role": "user", "content": f"{rule_instance.user_prompt_1}"},
                            {"role": "assistant", "content": f"{rule_instance.assistant_response_1}"},
                            {"role": "user", "content": f"{rule_instance.user_prompt_2}"},
                            {"role": "assistant", "content": f"{rule_instance.assistant_response_2}"},
                            {"role": "user", "content": f"{rule_instance.user_prompt_3}"},
                            {"role": "assistant", "content": f"{rule_instance.assistant_response_3}"},
                            {"role": "user", "content": f"{user_content}"}
                        ]

                for i in range(3):
                    # Make request
                    response = model(messages)

                    # Check whether the post response includes python code snippet
                    pattern = rf"```(\w+-*\w+)?\n(.*?)```"
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

    python_IR = code_snippet
    # return python_IR
    return python_IR, prompt_token_consumption, completion_token_consumption



if __name__ == '__main__':

    from utility.utils import parse_args
    args = parse_args()
    args.model_name = 'gpt-4-1106-preview'
    args.model_name = 'gpt-4-turbo-2024-04-09'
    args.model_name = 'azure-gpt4'
    print(args.model_name)
    
    init_code = \
'''
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.stack((a, b))
'''
    apply_stage_1_rules(args, init_code)