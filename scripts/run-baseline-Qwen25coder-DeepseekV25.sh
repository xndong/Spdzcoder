#!/bin/bash
# 使用默认值 "deepseek-v2.5-w-API-1-"如果 $1 没有被传递或为空
experimental=${1:-deepseek-v2.5-w-API-1-}

declare -a input_files=('if_test.json' 'math_test.json' 'for_test.json' 'all_rewrite_test.json' 'array_access_traverse_test.json' 'numpy_ufunc_test.json' 'numpy_operation_test.json')

for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-v2.5
done



experimental=${1:-Qwen2.5-coder-32b-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name qwen2.5-coder-32b
done





experimental=${1:-Qwen2.5-coder-7b-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name qwen2.5-coder-7b
done














# Running command
# bash scripts/run-baseline-Qwen25coder-DeepseekV25.sh