# Goal: try best to achieve translate Python code to MP-SPDZ code in single one step.
#* 和lo_chain_of_thought_rule.py打擂台

from dataclasses import dataclass

@dataclass
class SingleStepTranslation:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

SystemPrompt = \
"""
You are an expert to write MP-SPDZ promgram and you are familar with the differences between Python and MP-SPDZ. You will translate the Python code to MP-SPDZ code step by step.
"""


SingleStepTranslation_rule_prompt = \
"""
When you translate a Python/Numpy Program into MP-SPDZ, you will carefully consider the following aspects one by one.
1. The data type. You should carefully choose the appropriate data type.
2. The built-in math functions have different names. MP-SPDZ provides `mpc_math.pow_fx(x,y)`, `mpc_math.log_fx(x,y)`, `mpc_math.sqrt(x)`, `mpc_math.InvertSqrt(x)` as basic non-linear logarithmic functions, and it provodes `mpc_math.sin(x)`, `mpc_math.cos(x)`, `mpc_math.tan(x)`, `mpc_math.tanh(x)`, `mpc_math.asin(x)`, `mpc_math.acos(x)`, `mpc_math.atan(x)` as basic trigonometric functions.
3. The logic operation. For example, in python , we use `x or y` while in MP-SPDZ we use `x.bit_and(y)`
4. The bitwise operation. For example, in numpy, we use `bitwise_and(x,y)` while in MP-SPDZ we simply use `x & y` like in Python.
5. Remember to import your needed module in MP-SPDZ.
Let us translate the following Python code in MP-SPDZ code.
{CODE}
"""
# the appropriate data type from `sfix`, `cfix`, `sint`, `cint`,

#********* Instantiate rules with the above prompts ***********#

#* Instantiate实例化
single_step_translation = SingleStepTranslation(SystemPrompt, SingleStepTranslation_rule_prompt)

#* Directly choose the instance
rule_instances = [single_step_translation]

#****************************  End  ***************************#