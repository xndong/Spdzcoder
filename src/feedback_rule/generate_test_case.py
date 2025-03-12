# Goal:
#

from dataclasses import dataclass

@dataclass
class GenerateTestCase:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

@dataclass
class GenerateTestCase_Python:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#

GenerateTestCase_rule_prompt = \
"""
The following code defines a function written in MP-SPDZ which performs secure multi-party computation.
```MP-SPDZ
{SPDZ_CODE}
```
Your task is to create/generate one simple input that can be fed into the defined MP-SPDZ function above and generate a statement to invoke the function with your input. Generate them with comment that explains the rationale behind choosing the specific input.

Depending on whether the MP-SPDZ function accept scalar as input or 1-D vector as input, your generated input and statment respectively should be like
```MP-SPDZ
# generated scalar-like input
x = ...
y = ...
# generated statement to invoke the function
foo(x,y)
```
or
```MP-SPDZ
# generated 1-D vector-like input
array_1 = ...
array_2 = ...
# generated statement to invoke the function
func(array_1, array_2)
```
"""

GenerateTestCase_Python_rule_prompt = \
"""
The following code defines a function written in Python.
```python
{PYTHON_CODE}
```
But the only/sole purpose of the above Python code is to help you understand the semantic of the following MP-SPDZ code. (Note that the following MP-SPDZ code snippet which performs secure multi-party computation is semantically equivalent to the given Python code.)
Your task is to create/generate one input that can be fed into the defined MP-SPDZ function below and generate a statement to invoke the function with your input. Provide detailed descriptions for your test case, including the inputs and the rationale behind choosing the specific input.
```MP-SPDZ
{SPDZ_CODE}
```
For example, your generated input and statment should be like
```MP-SPDZ
# generated input
x = ...
y = ...
array_1 = ...
array_2 = ...
# generated statement to invoke the function
foo(x,y)
func(array_1, array_2)
```
"""

System_prompt = \
"""
You are a senior software test engineer and you can write an input for a defined function.
"""


#******************** Instantiate rules with the above prompt **********************#

#* Instantiate
from_spdz = GenerateTestCase(System_prompt, GenerateTestCase_rule_prompt)
from_spdz_python = GenerateTestCase_Python(System_prompt, GenerateTestCase_Python_rule_prompt)


#* Simplely choose all instances
rule_instances = [from_spdz, from_spdz_python]
