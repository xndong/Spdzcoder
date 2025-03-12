


from dataclasses import dataclass

@dataclass
class FixFunctionalityError:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#


FixFunctionalityError_rule_prompt = \
"""
You are provided a Python code snippet as follows:
```python
{PYTHON_CODE}
```
Then we provide you a MP-SPDZ code snippet in the following and we hope the given MP-SPDZ code performs the same functionality as the Python code, i.e. semantically equivalent to the given Python Code:
```MP-SPDZ
{SPDZ_CODE}
```
However, the provided MP-SPDZ code performs wrong functionality. The reason is that the code translation task from Python to MP-SPDZ failed.

To this end, your task is: First, read the Python code, and learn/summarize its functionality. Then, you fix the given MP-SPDZ code or totally re-translate the Python code into MP-SPDZ again. Finally, return your rectified MP-SPDZ code with correct functionality.
"""


System_prompt = \
"""
You are an expert to translate Python code into MP-SPDZ code and refine MP-SPDZ code.\nYou must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!
"""


#******************** Instantiate rules with the above prompt **********************#

#* Instantiate
fix_functionality_error = FixFunctionalityError(System_prompt, FixFunctionalityError_rule_prompt)


#* Simplely choose all instances
rule_instances = [fix_functionality_error]