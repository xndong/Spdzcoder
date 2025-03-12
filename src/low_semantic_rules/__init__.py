import ast
from dataclasses import dataclass
from utility.gpt_chat_api import make_requests
from utility.model_msg import load_model
@dataclass
class SelectChatMessage:
    system_prompt: str
    # user_logicOP_prompt: str
    user_math_prompt: str
    user_array_prompt: str
    # user_clearBranchJump_prompt: str
    # user_datatype_prompt: str

system_prompt = \
"""
Answer the question with `Ture` or `False`.
"""

user_math_prompt = \
"""
Read the given Python code. Does the Python code snippet include math function or does the Python code call a math function or does the Python code include math operation except basic `+` `-` `*` `\`? Answer with `True` or `False`.
```python
{CODE}
```
"""

user_array_prompt = \
"""
Read the given Python code. Does the Python code snippet include ndarray creation, indexing and slicing? In other words, does the Python code need ndarray creation, indexing and slicing? Answer with `True` or `False`.
```python
{CODE}
```
"""

# 实例化instance
selectchatmessage = SelectChatMessage(system_prompt,
                                      user_math_prompt,
                                      user_array_prompt)



def pattern_match(args, system_prompt, user_prompt, code_snippet):

    # args.model_name = 'gpt-3.5-turbo-1106'
    # args.model_name = 'gpt-4-turbo-2024-04-09'

    system_content = system_prompt
    user_content = user_prompt.format(CODE=code_snippet)
    messages=[
            {"role": "system", "content": f"{system_content}"},
            {"role": "user", "content": f"{user_content}"}
        ]
    model = load_model(args.model_name, temperature=0.7) if args.provider_name is None else load_model(args.model_name, provider_name=args.provider_name, temperature=0.7)
    response = model(messages)
    text = response.choices[0].message.content
    print(f'pattern_match text is: {text}') #? remember to remove
    match = True if 'True' in text else False

    return match


# 定义一个访问者类来检查逻辑操作
class LogicOperationVisitor(ast.NodeVisitor):
    def __init__(self):
        self.found_logic_operations = False

    def visit_BoolOp(self, node):
        # BoolOp代表逻辑运算符（and, or）
        self.found_logic_operations = True
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        # UnaryOp可以代表逻辑非（not）
        if isinstance(node.op, ast.Not):
            self.found_logic_operations = True
        self.generic_visit(node)

# 实例化
logic_operation_visitor = LogicOperationVisitor()