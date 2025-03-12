# Goal:
# eliminate `break` with nested branch at the same time --> MPSPDZ
# eliminate `continue` with nested branch at the same time --> MPSPDZ
from dataclasses import dataclass
import ast

@dataclass
class EliminateBreak:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

@dataclass
class EliminateContinue:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#

Break_rule_prompt = \
"""
Refactor the following code in order that the `break` keyword is eliminated. You are not allowed to use any `break` or `continue` keyword.
```
{CODE}
```
You can refer the given example:
```
for i in range(len(array)):
    if a[i]>10:
        if a[i+1]>2:
            break       # The condition for `break` is `a[i]>10 and a[i+1]>2`
        else:
            a[i] += 1   # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    else
        a[i] += 2       # The condition for `a[i] += 2` is `a[i]<=10`
```
will be refactored into
```
flag = False            # Employ a flag to manage the loop execution in order to avoid using both `break` and `continue` keyword
for i in range(len(array)):
    flag = flag or (a[i]>10 and a[i+1]>2)
    a[i] = flag*a[i] + (1-flag)*((a[i]>10 and a[i+1]<=2)*(a[i]+1) + (a[i]<=10)*(a[i]+2)) # The result is an combination
    # The code is in an oblivious form since there is no `break` and `continue` statement (no jump) in the code.
```
"""

Continue_rule_prompt = \
"""
Refactor the following code in order that the `continue` keyword is eliminated. You are not allowed to use any `break` or `continue` keyword.
```
{CODE}
```
You can refer the given example:
```
for i in range(len(array)):
    if a[i]>10:
        if a[i+1]>2:
            continue    # The condition for `continue` is `a[i]>10 and a[i+1]>2`
        else:
            a[i] += 1   # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    else
        a[i] += 2       # The condition for `a[i] += 2` is `a[i]<=10`
```
will be refactored into
```
flag = False            # Employ a 'flag' to manage the loop execution in order to avoid using both `break` and `continue` keyword
for i in range(len(array)):
    flag = flag or (a[i]>10 and a[i+1]>2)
    a[i] = flag*a[i] + (1-flag)*((a[i]>10 and a[i+1]<=2)*(a[i]+1) + (a[i]<=10)*(a[i]+2)) # The result is an combination
    flag = False    # To simulate the `continue` statement in loop, it is necessary to additionally add a statement to reset the 'flag' here. (Otherwise, do not modify flag!)
    # The code is in an oblivious form since there is no `break` and `continue` statement (no jump) in the code.
```
"""

System_prompt = 'You are an expert to write python but you always write python through a basic and explicit approach and do not use `break` and `continue` keyword in order that junior student can understand it.'

#******************** Instantiate rules with the above prompt **********************#

#* Instantiate实例化
eliminate_break = EliminateBreak(System_prompt, Break_rule_prompt)
eliminate_continue = EliminateContinue(System_prompt, Continue_rule_prompt)

#* Simplely choose all instances
rule_instances = [eliminate_break, eliminate_continue]

#* Alternatively, use pattern match to smartly select necessary instances.
def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在continue或者break

    def find_break_continue(node, found):
        # 检查是否是break或continue
        if isinstance(node, ast.Break):
            found['break'] = True
        elif isinstance(node, ast.Continue):
            found['continue'] = True

        # 遍历当前节点的所有子节点
        for child in ast.iter_child_nodes(node):
            find_break_continue(child, found)

    # 解析代码为AST
    try:
        parsed_code = ast.parse(code_snippet)
        found = {'break': False, 'continue': False}
        # 从顶层节点开始检查
        find_break_continue(parsed_code, found)
    except (SyntaxError, Exception):
        print(f"WRONG CODE SNIPPET! Exception occurs in {__file__}'s pattern_match.")
        found = {'break': False, 'continue': False}

    if found['break']:
        rule_instances.append(eliminate_break)
    if found['continue']:
        rule_instances.append(eliminate_continue)

    return rule_instances

    # # Code anotation里是否显式指定condition为clear varible
    # if 'condition is clear' in code_snippet.lower():
    #     rule_instances.pop()
    #     rule_instances.pop()

#****************************  Demo  ***************************#

'''
{CODE}
for i in range(len(array)):
    if a[i]>1:
        break
    a[i] += 1

{RESPONSE}
flag = False
for i in range(len(array)):
    flag = flag or (a[i] > 1)
    if not flag:
        a[i] += 1
'''

#********************** alternative prompts **********************#

Break_rule_prompt_alternative = \
"""
Refactor the following code in order that the `break` keyword is eliminated. You are not allowed to use any `break` or `continue` keyword.
```
{CODE}
```
You can refer the given example:
```
for i in range(len(array)):
    if a[i]>10:
        if a[i+1]>2:
            break       # The condition for `break` is `a[i]>10 and a[i+1]>2`
        else:
            a[i] += 1   # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    else
        a[i] += 2       # The condition for `a[i] += 2` is `a[i]<=10`
```
will be refactored into
```
flag = False            # Employ a flag to manage the loop execution in order to avoid using both `break` and `continue` keyword
for i in range(len(array)):

    condition_1 = a[i]>10 and a[i+1]>2      # The condition for `break` is `a[i]>10 and a[i+1]>2`
    condition_2 = a[i]>10 and a[i+1]<=2     # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    condtion_3 = a[i]<=10                   # The condition for `a[i] += 2` is `a[i]<=10`

    flag = flag or condition_1              # flag OR the condition for `break`
    a[i] = flag*a[i] + (1-flag)*(condition_2*(a[i]+1) + condition_3*(a[i]+2)) # The result is an combination
    # The code is in an oblivious form since there is no `break` and `continue` statement (no jump) in the code.
```
"""

Continue_rule_prompt_alternative = \
"""
Refactor the following code in order that the `continue` keyword is eliminated. You are not allowed to use any `break` or `continue` keyword.
```
{CODE}
```
You can refer the given example:
```
for i in range(len(array)):
    if a[i]>10:
        if a[i+1]>2:
            continue    # The condition for `continue` is `a[i]>10 and a[i+1]>2`
        else:
            a[i] += 1   # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    else
        a[i] += 2       # The condition for `a[i] += 2` is `a[i]<=10`
```
will be refactored into
```
flag = False            # Employ a 'flag' to manage the loop execution in order to avoid using both `break` and `continue` keyword
for i in range(len(array)):

    condition_1 = a[i]>10 and a[i+1]>2      # The condition for `continue` is `a[i]>10 and a[i+1]>2`
    condition_2 = a[i]>10 and a[i+1]<=2     # The condition for `a[i] += 1` is `a[i]>10 and a[i+1]<=2`
    condtion_3 = a[i]<=10                   # The condition for `a[i] += 2` is `a[i]<=10`

    flag = flag or condition_1              # flag OR the condition for `continue`
    a[i] = flag*a[i] + (1-flag)*(condition_2*(a[i]+1) + condition_3*(a[i]+2)) # The result is an combination
    flag = False    # To simulate the `continue` statement in loop, it is necessary to additionally add a statement to reset the 'flag' here. (Otherwise, do not modify flag!)
    # The code is in an oblivious form since there is no `break` and `continue` statement (no jump) in the code.
```
"""