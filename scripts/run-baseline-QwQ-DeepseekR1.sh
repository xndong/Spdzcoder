#!/bin/bash
declare -a input_files=('if_test.json' 'math_test.json' 'for_test.json' 'all_rewrite_test.json' 'array_access_traverse_test.json' 'numpy_ufunc_test.json' 'numpy_operation_test.json')

experimental=${1:-deepseek-R1-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-r1 \
            --provider_name bytedance
done



experimental=${1:-QwQ-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name qwen-qwq
done



experimental=${1:-openai-o1-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name azure-openai-o1 \
            --spdzcode_dir baseline_output
done



experimental=${1:-openai-o3-mini-w-API-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_Qwen25coder-DeepseekV25_plus-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name azure-openai-o3-mini \
            --spdzcode_dir baseline_output
done

















# Running command
# bash scripts/run-baseline-QwQ-DeepseekR1-2.sh