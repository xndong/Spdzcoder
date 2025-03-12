# Goal:
# Access a single element of an array by a secrete index
# Mutually exclusive to vanilla array indexing
# Apply this rule if and only if we explicitly denote the index is secrete in code annotations/docstring.
import ast
from dataclasses import dataclass

@dataclass
class ObliviousIndexing:
    system_prompt: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

ObliviousIndexing_rule_prompt = \
"""
The following given Python code snippet among the triple backticks includes array indexing. However, the code docstring/anotation denotes that the index is secrete. To this end, we would simulate array indexing in an oblivious form.
Your task is to refactor the array indexing into oblivious array indexing. Concretely, you should traverse the whole array and index the array in order to simulate an ORAM-style access.
Below is a one-shot example or demonstration:
```
'''
The index is a secrete varible.
'''
result = array[idx]                     # indexing the array and obtain the indexing result
```
After refactoring/rewriting, it becomes
```
result = 0
for i in range(len(array)):             # traverse the whole array
    flag = (i == idx)                   # only one i can match the target indexing `idx`
    result = result + flag * array[i]   # obtain the indexing result
    # The array indexing is now in an oblivious form since the access pattern remain unchanged for any index `idx`.
```
Now, Let us refactor array indexing in the following code among the triple backticks.
```
{CODE}
```
"""

ObliviousIndexingSystem_prompt = 'You are an expert to refacotr/rewrite python code.'

#******************** Instantiate rules with the above prompts **********************#

#* Instantiate实例化
oblivious_indexing = ObliviousIndexing(ObliviousIndexingSystem_prompt, ObliviousIndexing_rule_prompt)

#* Simplely choose all instances
rule_instances = [oblivious_indexing]

#* Alternatively, use pattern match to smartly select necessary instances.
class IndexingFinder(ast.NodeVisitor):
    def __init__(self):
        self.found_indexing = False
        self.found_slicing = False

    def visit_Subscript(self, node):
        # 检查是否是切片操作
        if isinstance(node.slice, (ast.Slice, ast.ExtSlice)):
            self.found_slicing = True
        # 否则是索引操作
        else:
            self.found_indexing = True
        # 继续遍历AST以找到更多可能的索引操作和切片操作
        self.generic_visit(node)

def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在indexing
    # 将代码解析成AST
    try:
        parsed_code = ast.parse(code_snippet)

        # 使用自定义的访问器遍历AST
        finder = IndexingFinder()
        finder.visit(parsed_code)
    except (SyntaxError, Exception):
        print(f"WRONG CODE SNIPPET! Exception occurs in {__file__}'s pattern_match.")
        finder = IndexingFinder()
        finder.found_indexing = False

    # Code anotation里是否显式指定索引为secrete varible
    flag = 'secrete' in code_snippet.lower() and 'index' in code_snippet.lower()

    # 输出检查结果是否存在indexing
    if finder.found_indexing and flag:
        rule_instances.append(oblivious_indexing)

    return rule_instances