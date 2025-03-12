#!/bin/bash
experimental=${1:-deepseek-v3-1-}

declare -a input_files=('if_test.json' 'math_test.json' 'for_test.json' 'all_rewrite_test.json' 'array_access_traverse_test.json' 'numpy_ufunc_test.json' 'numpy_operation_test.json')

for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_deepseekv3-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-v3 \
            --provider_name bytedance
done





# Running command
# bash scripts/run-baseline-DeepseekV3.sh