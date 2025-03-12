# rewrite math and universal functions
# functions:
#   1. arithmetic
#      linear: ADD and MUL
#      non-linear: trigonometric functions, basic non-linear functions, and their combinations.
#           trigonometric:
#           basic: exp, ln, sqrt, invertsqrt(invert)
#   2. binary/boolean/bit_wise

from dataclasses import dataclass

@dataclass
class Linear_NonLinear:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'


#********************** prompts **********************#

Linear_NonLinear_rule_prompt = \
"""
You will be offered a python/numpy code snippet which describes a function.
If the function does not include any advanced math operation, python math operation, numpy universal function, your task is just return the original given code snippet and do nothing.
Otherwise, your task is to refacotr/rewrite the math part in the python/numpy function.
For any linear arithmetic function, you should re-implement the linear function in an explict/basic approach;
For any nonlinear arithmetic function, you should re-implement by only using `exp`, `ln`, `sqrt`, `invertsqrt` (invert), and their combinations;
For any trigonometric function, you should re-implement by only using `sin`, `cos`, `tan`, `arcsin`, `arccos`, `arctan`, `tanh`.
For any numpy universal function, the argument should be considered as an array.
Again, if  the given code just include elementary math: `add`, `subtraction`, `multiplication` and `divide`, you should just return the original code snippet and do nothing!
Now, Let us refactor math part in the following code among the triple backticks if applicable.
```
{CODE}
```
"""

System_prompt = 'You are an expert to refactor/rewrite python code but you only need to care about the advanced math function or numpy universal function in a given python code snippet. Never modify the function name and never add example usage of the function, otherwise I will punish you!'

#******************** Instantiate rules with the above prompts **********************#

#* Instantiate实例化
linear_nonlinear_mathfunc = Linear_NonLinear(System_prompt, Linear_NonLinear_rule_prompt)

#* Simplely choose all instances
rule_instances = [linear_nonlinear_mathfunc]

#* Alternatively, use pattern match to smartly select necessary instances.
def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在特殊的Python方法和Syntax Sugar
    # 直接在规则的prompt里判断是否需要apply规则了，如果不需要直接返回original code and do nothing，所以就不再这里调用LLM判断是否需要apply规则了
    rule_instances = [linear_nonlinear_mathfunc]

    return rule_instances




""" Below is a one-shot example or demonstration:
```

```
After refactoring/rewriting, it becomes
```

``` """