# Goal:
# eliminate advanced array creation, indexing, slicing and manipulation in Numpy --> MPSPDZ
from dataclasses import dataclass

@dataclass
class ElimininateAdvancedArrayOperations:
    system_prompt: str
    user_prompt_1: str
    assistant_response_1: str
    user_prompt_2: str
    assistant_response_2: str
    user_prompt_3: str
    assistant_response_3: str
    rule_prompt: str
    # implementation: str='LLM' # 'AST'

#********************** prompts **********************#


ElimininateAdvancedArrayOperations_rule_prompt = \
"""
The following given Python code snippet among the triple backticks maybe includes one or more Numpy array creation, indexing, slicing or manipulation statement. However, we don't like advanced Numpy array operations in code.
To this end, your task is to rewrite/refactor the given Python code, if there exists advanced Numpy array operations, in order that the re-written python code only consists of simple/rigid, easy, commonly-used, rigid methods to create, use or manipulate a Numpy array.

If there is no Numpy array operations like creation, indexing, slicing, manipulation in the original code, you can just response with the original code with the triple backticks. Never modify the function name and never add example usage of the function, otherwise I will punish you!
```
{CODE}
```
"""
# array creation
user_prompt_1 = \
"""
The following given Python code snippet among the triple backticks maybe includes a Numpy array creation statement. However, we don't like advanced Numpy array creation in code.
To this end, your task is to rewrite/refactor the given Python code in order that the re-written python code only consists of simple/rigid methods to create a Numpy array. For example, you should eliminate `eye`, `identity`, `empty`, `diag`, `linspace`, `logspace`, `geomspace` methods in a given python code snippet and rewrite/refactor them from scratch.
In other words, your task is to refactor the following python code, if there exists advanced Numpy array creation, through a more basic, explicit and rigid approach using `zeros`, `zeros_like`, `full`, `full_like`, `array`, `as_array`, `mat`, `matrix`, `as_matrix` methods in Numpy.
```
import numpy as np
alist = [1, 3, 5]           #
array = np.diag(alist)      # create a diagnal array from List by using advanced numpy array creation
```
"""

assistant_response_1 = \
"""
To refactor the given code snippet to avoid using the `np.diag` method for creating a diagonal array, you can achieve the same result by initializing a square array of zeros and then filling the diagonal with the desired values manually. This is a straightforward approach and relies solely on basic Numpy array creation methods like `zeros` and direct assignment to elements. Here's how you can do it:

```python
import numpy as np

# Original list to be used for the diagonal
alist = [1, 3, 5]

# Create a square matrix of zeros with dimensions based on the length of alist
array = np.zeros((len(alist), len(alist)))

# Fill the diagonal with values from alist
for i in range(len(alist)):
    array[i, i] = alist[i]
```

This code does exactly what the original snippet does but avoids using the `np.diag` method for creating a diagonal matrix. Instead, it creates a square matrix filled with zeros and manually assigns the values from `alist` to the diagonal elements of the matrix.
"""
# array indexing and slicing
user_prompt_2 = \
"""
The following given Python code snippet among the triple backticks includes one or more Numpy array indexing statements. However, we don't like advanced Numpy array indexing and slicing in code.
To this end, your task is to rewrite/refactor the given Python code in order that the re-written python code only consists of simple/rigid methods to index or slice a Numpy array. For example, you should eliminate advanced `take`, `choose`, `diag`, `select`, `place`, `put` methods in a given python code snippet and rewrite/refactor them from scratch.
In other words, your task is to refactor the following python code, if there exists advanced Numpy array indexing and slicing, through a more basic, explicit and rigid approach only using `integer array indexing`, `[i]`, `[i,j]`, `[:]` and `[i,:]` in Numpy.
```
import numpy as np

a = [4, 3, 5, 7, 6, 8]      # If a is an ndarray or List, advanced/“fancy” indexing can be used.
indices = [0, 1, 4]
array = np.take(a, indices) # Take elements from an array with indices along an axis (axis is optional).
```
"""

assistant_response_2 = \
"""
To refactor the code snippet and eliminate the use of the `np.take` method for advanced array indexing, we can use simple indexing techniques. Given that we only want to use basic slicing and indexing methods like `[i]`, `[i,j]`, `[:]`, and `[i,:]`, we can create a new array by directly accessing the elements of the original array (`a`) at the positions specified in `indices`. Here's how you can do it:

```python
import numpy as np

# Original array/List and indices
a = [4, 3, 5, 7, 6, 8]
indices = [0, 1, 4]

# Using a basic indexing approach to create the new array
array = np.array([a[i] for i in indices])
```

In this approach, we manually iterate over `indices`, using each index to access the corresponding element in `a`. This creates a list of the selected elements, which is then converted to a Numpy array with `np.array()`. This method strictly follows the constraints of using only basic indexing methods.
"""
# array manipulation
user_prompt_3 = \
"""
The following given Python code snippet among the triple backticks maybe includes a Numpy array manipulation statement. However, we don't like advanced Numpy array manipulation in code.
To this end, your task is to rewrite/refactor the given Python code in order that the re-written python code only consists of simple/rigid methods to manipulate a Numpy array. For example, you should eliminate `reshape`, `copy`, `delete`, `insert`, `append`, `stack`, `split` methods in a given python code snippet and rewrite/refactor them from scratch.
In other words, your task is to refactor the following python code, if there exists advanced Numpy array manipulation, through a more basic, explicit and rigid approach using `concatenate`, `transpose`, `array creation` and `array indexing/slicing` methods in Numpy.
```
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
np.stack((a, b))
```
"""

assistant_response_3 = \
"""
To refactor the given code snippet that uses `np.stack` for array manipulation without using advanced manipulation methods like `reshape`, `copy`, `delete`, `insert`, `append`, or `stack`, you can achieve the desired outcome through a combination of basic array creation and concatenation methods. Specifically, you can use `np.concatenate` along with a bit of manual reshaping by altering the shapes of `a` and `b` to make them 2D before concatenation. This approach, however, strictly adheres to using only simple, explicit methods as requested.

Here's how you can refactor the code:

```python
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Manually adjust the arrays to 2D if necessary and concatenate along the new axis
a_2d = a[np.newaxis, :]  # Adds a new axis, effectively reshaping a to 2D without using reshape
b_2d = b[np.newaxis, :]  # Does the same for b

# Use concatenate to achieve the stack effect along axis 0
array = np.concatenate((a_2d, b_2d), axis=0)
```

This code does not use the `np.stack` method directly. Instead, it first converts `a` and `b` into 2D arrays by adding a new axis (using `np.newaxis` for a more manual control which is aligned with simple methods). Then, it uses `np.concatenate` to join these arrays along the new axis (which is the first axis, `axis=0`), effectively stacking them similarly to how `np.stack` would.
"""

System_prompt = 'You are an expert to refacotr/re-write python. When you create, index, slice or manipulate a Numpy array or convert Python List into Numpy array, you only use the basic, common and simple array methods in Numpy and avoid using advanced array methods. Never modify the function name and never add example usage of the function, otherwise I will punish you!'

#******************** Instantiate rules with the above prompt **********************#

#* Instantiate实例化
eliminate_advanced_array_operations = ElimininateAdvancedArrayOperations(System_prompt,
                                                                         user_prompt_1, assistant_response_1, user_prompt_2, assistant_response_2, user_prompt_3, assistant_response_3, ElimininateAdvancedArrayOperations_rule_prompt
                                                                         )

#* Simplely choose all instances
rule_instances = [eliminate_advanced_array_operations]

#* Alternatively, use pattern match to smartly select necessary instances.
def pattern_match(code_snippet):
    rule_instances = []
    # 检查code_snippet是否存在上述pattern,存在哪种pattern就append相应的实例instance

    # 可以借助LLM，也可以借助词法分析工具使用AST或字符串匹配，来检查是否存在continue或者break
    # 直接在规则的prompt里判断是否需要apply规则了，如果不需要直接返回original code，所以就不再这里调用LLM判断是否需要apply规则了
    rule_instances = [eliminate_advanced_array_operations]

    return rule_instances
