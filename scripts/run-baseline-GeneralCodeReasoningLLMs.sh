
#!/bin/bash
declare -a input_files=('if_test.json' 'math_test.json' 'for_test.json' 'all_rewrite_test.json' 'array_access_traverse_test.json' 'numpy_ufunc_test.json' 'numpy_operation_test.json')

# GeneralLLMs
experimental=${1:-deepseek-v3-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-v3 \
            --provider_name bytedance
done

experimental=${1:-gpt-4o-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name azure-gpt4o
done



# CodeLLMs
experimental=${1:-deepseek-v2.5-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-v2.5
done

experimental=${1:-Qwen2.5-coder-32b-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name qwen2.5-coder-32b
done



# ReasoningLLMs
experimental=${1:-deepseek-R1-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name deepseek-r1 \
            --provider_name bytedance
done

experimental=${1:-QwQ-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name qwen-qwq
done

experimental=${1:-openai-o1-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name azure-openai-o1 
done

experimental=${1:-openai-o3-mini-naive-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python evaluation/baseline_GeneralCodeReasoningLLMs-mp.py \
            --input_file ${input_file} \
            --experimental ${experimental} \
            --model_name azure-openai-o3-mini 
done




# Running command
# bash scripts/run-baseline-GeneralCodeReasoningLLMs.sh