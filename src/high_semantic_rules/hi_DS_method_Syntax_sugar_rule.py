# Goal:
# eliminate special/exclusive data structure functions/methods in Python and Numpy
# eliminate Python syntax sugars: list comprehension, set comprehension, Lambda Functions.
from dataclasses import dataclass

@dataclass
class DataStructureMethod:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

@dataclass
class SyntaxSugar:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#
#REVIEW: Alternative, 把List全都变成Numpy ndarray
# For example, unlike typical Python programming, MP-SPDZ does not support dynamic list operations like `.append()` in the same way.
DS_method_rule_prompt = \
"""
It's important to note that MP-SPDZ doesn't directly support all Python data structure methods, e.g. list `append()`, `extend()`.

Your task is to simplify rewrite/refactor the following given Python code snippet among the triple backticks in order that the re-written python code only consists of simple, commonly-used, rigid methods in Numpy ndarray and Python List data structure. For example, you should eliminate and never use List `append`, `extend`, `insert`, `reverser`, `count` methods in a given python code snippet and rewrite/refactor them from scratch.
In other words, your task is to refactor the following python code through a more basic and explicit approach by Numpy or Python.
If you think the code is simple enought and doesn't include advanced List methods, you can just response with the original code.
```
{CODE}
```
"""

SyntaxSugar_rule_prompt = \
"""
Refactor the following code among the triple backticks in order to remove or elminate the Python syntax sugars.
If there is no Python syntax sugars, you can just response with the original code.
```
{CODE}
```
"""

System_prompt = 'You always write python without advanced List methods and Python syntax sugars.'
# step by step

#******************** Instantiate rules with the above prompts **********************#

#* Instantiate实例化
exclusive_data_structure_methods = DataStructureMethod(System_prompt, DS_method_rule_prompt)
syntax_sugar = SyntaxSugar(System_prompt, SyntaxSugar_rule_prompt)

#* Simplely choose all instances
rule_instances = [exclusive_data_structure_methods, syntax_sugar]

#* Alternatively, use pattern match to smartly select necessary instances.
def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在特殊的Python方法和Syntax Sugar
    # 直接在规则的prompt里判断是否需要apply规则了，如果不需要直接返回original code，所以就不再这里调用LLM判断是否需要apply规则了
    rule_instances = [exclusive_data_structure_methods, syntax_sugar]

    return rule_instances


#****************************  Demo  ***************************#

'''
{CODE}

{RESPONSE}
'''