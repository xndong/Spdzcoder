import os
import re
from pathlib import Path
from dataclasses import dataclass

#**************** api_doc ****************#

file_path = Path(__file__)
current_dir = os.path.dirname(file_path)

with open(f'{current_dir}/spdz_api_docs/spdz_api_mpc_math.txt', 'r') as f:
    MP_SPDZ_API_DOC_math = f.read()
with open(f'{current_dir}/spdz_api_docs/spdz_api_types.txt', 'r') as f:
    MP_SPDZ_API_DOC_types = f.read()
with open(f'{current_dir}/spdz_api_docs/spdz_api_utils.txt', 'r') as f:
    MP_SPDZ_API_DOC_utils = f.read()

MP_SPDZ_API_DOC = MP_SPDZ_API_DOC_math + '\n\n' + MP_SPDZ_API_DOC_types + '\n\n' + MP_SPDZ_API_DOC_utils
MP_SPDZ_API_DOC = MP_SPDZ_API_DOC_types + '\n\n' + MP_SPDZ_API_DOC_utils

#**************** Code LLM prompt ****************#

@dataclass
class CodeLlama_Prompt:
    system_prompt: str
    rule_prompt: str

system_prompt = \
"""
You are a helpful and honest code assistant expert in writing MP-SPDZ promgram. When you translate a Python Program into MP-SPDZ, you will consider their differences in expressing semantics and try to solve the code translation task step by step.
You must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!
"""

system_prompt = \
"""
You are a helpful and honest code assistant expert in writing MP-SPDZ promgram. When you re-write a Python code snippet into MP-SPDZ, you will consider their differences in expressing semantics and refer to the official MP-SPDZ API documents.
You must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!
"""

rule_prompt = \
"""
Your task is to re-write it into semantically equivalent MP-SPDZ code in order to save intensive human labor.
Generally, you should consider the following aspects.
1. The data type. You should carefully choose the appropriate data type.
2. The built-in math functions have different names. For example, MP-SPDZ provides `mpc_math.pow_fx(x,y)`, `mpc_math.log_fx(x,y)`, `mpc_math.sqrt(x)`, `mpc_math.InvertSqrt(x)` as basic non-linear logarithmic functions, and it provodes `mpc_math.sin(x)`, `mpc_math.cos(x)`, `mpc_math.tan(x)`, `mpc_math.tanh(x)`, `mpc_math.asin(x)`, `mpc_math.acos(x)`, `mpc_math.atan(x)` as basic trigonometric functions.
3. The logic operation. For example, in python , we use `x or y` while in MP-SPDZ we use `x.bit_and(y)`
4. The bitwise operation. For example, in numpy, we use `bitwise_and(x,y)` while in MP-SPDZ we simply use `x & y` like in Python.
5. Remember to import your needed module in MP-SPDZ.
Note that you must use triple backticks for code blocks in your response and never include any usage example in the code blocks.
Now, re-write the following Python code into MP-SPDZ code!
{CODE}

"""

@dataclass
class CodeLlama_Prompt_API:
    system_prompt: str
    rule_prompt: str

rule_prompt_api = \
"""
Your task is to re-write it into semantically equivalent MP-SPDZ code in order to save intensive human labor.
Generally, you should consider the following aspects.
1. The data type. You should carefully choose the appropriate data type.
2. The built-in math functions have different names. For example, MP-SPDZ provides `mpc_math.pow_fx(x,y)`, `mpc_math.log_fx(x,y)`, `mpc_math.sqrt(x)`, `mpc_math.InvertSqrt(x)` as basic non-linear logarithmic functions, and it provodes `mpc_math.sin(x)`, `mpc_math.cos(x)`, `mpc_math.tan(x)`, `mpc_math.tanh(x)`, `mpc_math.asin(x)`, `mpc_math.acos(x)`, `mpc_math.atan(x)` as basic trigonometric functions.
3. The logic operation. For example, in python , we use `x or y` while in MP-SPDZ we use `x.bit_and(y)`
4. The bitwise operation. For example, in numpy, we use `bitwise_and(x,y)` while in MP-SPDZ we simply use `x & y` like in Python.
5. Remember to import your needed module in MP-SPDZ.

Importantly, you must refer to the MP-SPDZ API documentation to write the MP-SPDZ code. The API documentation is as follows:

{API_DOC}

Note that you must use triple backticks for code blocks in your response and never include any usage example in the code blocks.
Now, re-write the following Python code into MP-SPDZ code with the help of the API documentation!
{CODE}

"""


#**************** Prompt Template Instances ****************#

codellama_prompt = CodeLlama_Prompt(system_prompt, rule_prompt)
codellama_prompt_api = CodeLlama_Prompt_API(system_prompt, rule_prompt_api)



#**************** Defined Functions for Evaluation ****************#

def post_process_codellama_response(response):

    pattern = r"```(\w+-*\w+)?\s*(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        code_response =  matches[-1][1]
    else:
        raise Exception('No substring in text that matches the pattern.')

    return code_response