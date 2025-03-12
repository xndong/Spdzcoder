from dataclasses import dataclass

@dataclass
class SelfReflection:
    system_prompt: str
    rule_prompt: str


System_prompt = \
"""
Correct/refectify the given MP-SPDZ program with given instruction if applicable.\nYou must/always use triple backticks for code blocks in your response and never include any usage example in the code blocks!
"""

SelfReflection_rule_prompt = \
"""
Review the following MP-SPDZ program and follow the given instructions as below:
1. Rectify those incorrectly imported modules. Here are the correct examples to import Python and MP-SPDZ modules. If `mpc_math` is used, never forget to import it!
```
# import math related module
import math
from Compiler import mpc_math

# import type related module
from Compiler.types import sint
from Compiler.types import sfix
from Compiler.types import cint
from Compiler.types import cfix
from Compiler.types import regint
from Compiler.types import Array
from Compiler.types import Matrix
from Compiler.types import MemValue

# import all modules from standard library (optional)
from Compiler.library import *
```

2. Rectify non-exist MP-SPDZ Functions.
- `mpc_math.exp(x)` should be `mpc_math.pow_fx(math.e, x)` which computes `e^x`
- `mpc_math.log(x)` should be `mpc_math.log_fx(x, math.e)` which computes `ln(x)`
- `mpc_math.log_fx(x, cfix(math.e)) should be `mpc_math.log_fx(x, math.e)` which computes `ln(x)`
- `mpc_math.sqrt_fx(x)` should be `mpc_math.sqrt(x)` which computes `sqrt(x). Before computing square root, convert `x` into `sfix` data type by `x = sfix(x)`.
- `mpc_math.pi` should be `sfix(mpc_math.pi)` which provides a fixed-point approximation of pi.
- `math.pi` should be `sfix(math.pi)` which provides a fixed-point approximation of pi.
- `mpc_math.pi_fx()` should be `sfix(mpc_math.pi)` or `sfix(math.pi)` which provides a fixed-point approximation of pi.

3. Delete/Remove the part of `example usage of the function` in the code if applicable.
4. Tenary expression `x if condition else y` should be `condition.if_else(x,y)`.
5. `mpc_math.max(y, 0)` should be `y.get_vector().max(0)`.

Strictly follow the above 5 aspects and start to review the code. If applicable, return the modified code, otherwise return the original code as your response.
```MP-SPDZ
{CODE}
```
"""


self_reflection = SelfReflection(System_prompt, SelfReflection_rule_prompt)

rule_instances = [self_reflection]