# Goals:
# nested branch implies multiple branch, while the vice verse is not true.
# eliminate simple and nested branch --> MPSPDZ
# eliminate multiple return (implies multiple branch) --> MPSPDZ
# (eliminate chained comparision --> MPSPDZ)
from dataclasses import dataclass
import ast

@dataclass
class NestedIf_MultipleReturn:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

@dataclass
class ChainedComparision:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

@dataclass
class ObliviousForm:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#

NIMR_rule_prompt = \
"""
There maybe a nested if-condition block in a given code snippet, i.e. there is an inner if-condition block in the outer if-condition block.
Besides, there maybe one more return in a code snippet.
We can refactor the code to simplify the control flow and makes the code easier to understand.
Therefore, your task is to refactor the given code without the nested `if` condition and with only one `return` statement at the end, i.e. you must eliminate the nested if-condition block and keep one `return` statement at the end of the code.
Below is a one-shot example or demonstration:
```
def foo(x):                 # nested `if` and multiple `return` statments
    if x<=0:
        if x <= -3:
            return 10       # The condition for `return 10` is `x<=0 and x<=-3`
        else:
            return 100      # The condition for `return 100` is `x>-3 and x<= 0`
    elif x>=6:
        return 1000         # The condition for `return 1000` is `x>=6`
    else:
        return x            # For cases where 0 < x < 6, x remains unchanged and is returned
```
After rewriting, it becomes
```
def foo(x):
    # Initialize result with x for cases where none of the conditions apply directly.
    result = x

    # Check the conditions and update the result accordingly
    if x <=0 and x <= -3:
        result = 10
    elif x > -3 and x <= 0:
        result = 100
    elif x >= 6:
        result = 1000

    # For cases where 0 < x < 6, x remains unchanged.
    return result
    # Additionally, there is only one single `return` statement at the end of the code.
```
Now, Let us refactor the following code among the triple backticks.
```
{CODE}
```
"""

# 先写成了refactor，结果gpt3.5给的代码全使用了chained comparison; 接着改成了eliminate, gpt3.5就把chained comparisong改成了 if x >= -5 and x <= 0 这种形式
ChainedComparision_rule_prompt = \
"""
Chained comparison the syntax sugar of Python. Your task is to refactor the chained comparison through logic operator in a given code snippet but keep everything else unchanged. For example, the statement `if -3 < x < 6:` will be changed into `if x > -3 and x < 6`.
Now, Let us refactor the chained comparison in the following code among the triple backticks.
```
{CODE}
```
"""

ObliviousForm_rule_prompt = \
"""
Your task is to refactor the if-condition block into an oblivious form. In other words, you should eliminate the `if` statement in your code.
Below is a one-shot example or demonstration:
```
def foo(x):
    # Initialize the result with x
    result = x

    if x <= -3:
        result = 10             # The condition for `return 10` is `x<=-3`
    elif x > -3 and x <= 0:
        result = 100            # The condition for `return 100` is `x>-3 and x<= 0`
    elif x >= 6:
        result = 1000           # The condition for `return 1000` is `x>=6`

    # For cases where 0 < x < 6, x remains unchanged and is returned.
    return result
```
After refactoring/rewriting, it becomes
```
def foo(x):
    # Initialize the result with x
    result = x

    condition_1 = (x<3)                 # The condition for `return 10` is `x<=-3`
    condition_2 = (x>-3 and x<= 0)      # The condition for `return 100` is `x>-3 and x<= 0`
    condition_3 = (x>=6)                # The condition for `return 1000` is `x>=6`
    condition_4 = (x>0 and x<6)         # The condition for `return x` is `x>0 and x<6`

    # Apply transformations based on conditions
    # Note: Multiplication by a condition acts as an if statement
    result = condition_1 * 10 + condition_2 * 100 + condition_3 * 1000 + condition_4 * result    # The result is an combination

    return result
    # The code is in an oblivious form since there is no `if` statement (no branch) in the code.
```
Now, Let us refactor the following code among the triple backticks.
```
{CODE}
```
"""


System_prompt = 'You are an expert to write python but you always write python through a basic and explicit approach in order that junior student can understand it. Never modify the function name and never add example usage of the function, otherwise I will punish you!'

ObliviousFormSystem_prompt = 'You are an expert to translate python code into MP-SPDZ. To this end, when you refactor/rewrite python code, you always refactor/rewrite a python code snippet into an oblivious form just as what you do in MP-SPDZ framework. Never modify the function name and never add example usage of the function, otherwise I will punish you!'

#******************** Instantiate rules with the above prompts **********************#

#* Instantiate实例化
nested_if_and_mult_return = NestedIf_MultipleReturn(System_prompt, NIMR_rule_prompt)
chained_comparision = ChainedComparision(System_prompt, ChainedComparision_rule_prompt)
oblivious_form = ObliviousForm(ObliviousFormSystem_prompt, ObliviousForm_rule_prompt)

#* Simplely choose all instances
rule_instances = [nested_if_and_mult_return, chained_comparision, oblivious_form]

#* Alternatively, use pattern match to smartly select necessary instances.
class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.has_chained_comparison = False
        self.return_statements_count = 0
        self.functions_with_multiple_returns = []
        self.exist_if = False
        self.found_nested_if = False

    def visit_FunctionDef(self, node):
        # 重置return语句计数器
        self.return_statements_count = 0
        self.generic_visit(node)  # 访问函数定义内的所有节点
        if self.return_statements_count > 1:
            self.functions_with_multiple_returns.append(node.name)

    def visit_Return(self, node):
        self.return_statements_count += 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        if len(node.ops) > 1:
            self.has_chained_comparison = True
        self.generic_visit(node)

    def visit_If(self, node):
        self.exist_if = True
        # 检查当前If节点的body部分是否包含更多的If节点
        for body_item in node.body:
            if isinstance(body_item, ast.If):
                self.found_nested_if = True
                break  # 找到嵌套的if后退出循环
        # 继续遍历AST以查找更多的If节点
        self.generic_visit(node)


def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在continue或者break
    try:
        # 解析代码为AST
        tree = ast.parse(code_snippet)

        # 创建一个分析器对象并使用它来遍历AST
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
    except (SyntaxError, Exception):
        print(f"WRONG CODE SNIPPET! Exception occurs in {__file__}'s pattern_match.")
        analyzer = CodeAnalyzer()
        analyzer.found_nested_if = False
        analyzer.functions_with_multiple_returns = False
        analyzer.has_chained_comparison = False
        analyzer.exist_if = False

    # 检查是否有函数包含嵌套的if语句或多个return语句
    if analyzer.found_nested_if or analyzer.functions_with_multiple_returns:
        rule_instances.append(nested_if_and_mult_return)
    # 检查是否有链式比较
    if analyzer.has_chained_comparison:
        rule_instances.append(chained_comparision)

    if analyzer.found_nested_if or analyzer.functions_with_multiple_returns or analyzer.exist_if:
        rule_instances.append(oblivious_form)

    return rule_instances

    # # Code anotation里是否显式指定condition为clear varible
    # if 'condition is clear' in code_snippet.lower():
    #     rule_instances.pop()


#****************************  Demo  ***************************#

'''
{CODE}
def relu6(x):
    if x<=0:
        if x <= -3:
            x += 10
        else:
            x += 100
    elif x>=6:
        x += 1000
    else:
        return x

{RESPONSE}
def relu6(x):
    # Initialize result with x for cases where none of the conditions apply directly
    result = x

    # Check the conditions and update result accordingly
    if x <= -3:
        result = x + 10
    elif -3 < x <= 0:
        result = x + 100
    elif x >= 6:
        result = x + 1000

    # For cases where 0 < x < 6, x remains unchanged and is returned
    return result

#* Demo中的例子和上面prompt中的不同分别是`return x+ 10`和`return 10`
#* Demo中的例子接续lo_branch_rule.py中的Demo
#* Demo接Demo, Prompt接Prompt
'''
