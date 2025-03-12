# Goal:
# Insert-Compile-Run the generated spdz code with user prepared test case (Note that this requires the user to generate test cases instead of generating test case by GPT). If compilation-runtime error occurs, apply this rule to fix. Otherwise, skip this rule.

from dataclasses import dataclass

@dataclass
class FixCompilationRuntimeError:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#

FixCompilationRuntimeError_rule_prompt = \
"""
There exists bugs in the following MP-SPDZ code. And the compilation and runtime error is provided to you.
The MP-SPDZ code is as follows:
```
{CODE}
```
The compilation and runtime error is in the below:
"
{COMPILATION_RUNTIME_ERROR}
"
Your task is to check the error messages, fix the existing bugs and return the rectified code.
"""
# user_content = use_cr_error.fix_cr_error.rule_prompt.format(CODE=current_spdz_code, COMPILATION_RUNTIME_ERROR=message)





FixCompilationRuntimeError_rule_prompt = \
"""
You are provided a Python code snippet as follows:
```python
{PYTHON_CODE}
```
Then we provide its corresponding semantic-equivalent MP-SPDZ code in the following:
```MP-SPDZ
{SPDZ_CODE}
```
However, there exists bugs/errors in the provided MP-SPDZ code and the traceback inforamtion is provided to you in the below:
"
{COMPILATION_RUNTIME_ERROR}
"
Here is your task: First, read the Python code and the MP-SPDZ code. Then, combining traceback inforamtion, you fix the existing bugs in the given MP-SPDZ code or re-translate the Python code into MP-SPDZ again. Finally, return your rectified/correct MP-SPDZ code.
"""



System_prompt = \
"""
You are an expert to debug/re-write MP-SPDZ code when you are given the traceback information/compilation errors/ runtime errors.\nYou must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!
"""


#******************** Instantiate rules with the above prompt **********************#

#* Instantiate实例化
fix_cr_error = FixCompilationRuntimeError(System_prompt, FixCompilationRuntimeError_rule_prompt)


#* Simplely choose all instances
rule_instances = [fix_cr_error]
