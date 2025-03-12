# Goal:
# Detect while loops and convert while-loop into for-loop if applicable.
# If can not convert to for-loop, then return the original code.abs
from dataclasses import dataclass
import ast

@dataclass
class RewriteWhileLoop:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#

RewriteWhileLoop_rule_prompt = \
"""
The following given Python code snippet among the triple backticks includes while-loop. However, we don't like while-loop in code and we prefer use for-loop.
To this end, your task is to rewrite/refactor the loop body of the given Python code in order that while-loop is replaced with for-loop.
Note that there are some reasons that the while-loop can/should not convert into for-loop in Python, e.g. the number of loops/iterations is unknown/unpredicable. In such case, keep the whole code snippet unchanged and just return the original code in your response.
```
{CODE}
```
"""

System_prompt = 'You are an expert to refactor/re-write python. You would like to use the `for-loop` instead of the `while-loop` if applicable.'

#******************** Instantiate rules with the above prompt **********************#

#* Instantiate实例化
rewrite_while_loop = RewriteWhileLoop(System_prompt, RewriteWhileLoop_rule_prompt)

#* Simplely choose all instances
rule_instances = [rewrite_while_loop]

#* Alternatively, use pattern match to smartly select necessary instances.
class WhileLoopFinder(ast.NodeVisitor):
    def __init__(self):
        self.found_while_loop = False

    def visit_While(self, node):
        self.found_while_loop = True
        # 使用generic_visit确保继续遍历当前While节点的子节点
        self.generic_visit(node)

def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在while loop
    # 将代码解析成AST
    try:
        parsed_code = ast.parse(code_snippet)
        # 使用自定义的访问器遍历AST
        finder = WhileLoopFinder()
        finder.visit(parsed_code)
    except (SyntaxError, Exception):
        print(f"WRONG CODE SNIPPET! Exception occurs in {__file__}'s pattern_match.")
        finder = WhileLoopFinder()
        finder.found_while_loop = False

    # 输出检查结果是否存在while_loop
    if finder.found_while_loop:
        rule_instances.append(rewrite_while_loop)

    return rule_instances

