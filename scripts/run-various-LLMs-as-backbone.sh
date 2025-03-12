#!/bin/bash
declare -a input_files=('if_test.json' 'math_test.json' 'for_test.json' 'all_rewrite_test.json' 'array_access_traverse_test.json' 'numpy_ufunc_test.json' 'numpy_operation_test.json')

# %%%%%%%%%%%%%%%%%%%%%%% Main Inference  %%%%%%%%%%%%%%%%%%%%%%%
experimental=${1:-experiment-1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python src/pipeline-mp.py \
            --input_file ${input_file} \
            --IR_file intermediate_representation.jsonl \
            --experimental ${experimental} \
            --spdz_path ~/mp-spdz-0.3.6 \
            --feedback_flag \
            --model_name azure-gpt4 
done


# %%%%%%%%%%%%%%%%%%%%%%% Inference with various LLMs as backbones  %%%%%%%%%%%%%%%%%%%%%%%
experimental=${1:-deepseek-v3-pure-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python src/pipeline-mp.py \
            --input_file ${input_file} \
            --IR_file intermediate_representation.jsonl \
            --experimental ${experimental} \
            --spdz_path ~/mp-spdz-0.3.6 \
            --feedback_flag \
            --model_name deepseek-v3 \
            --provider_name bytedance
done


experimental=${1:-deepseek-r1-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python src/pipeline-mp.py \
            --input_file ${input_file} \
            --IR_file intermediate_representation.jsonl \
            --experimental ${experimental} \
            --spdz_path ~/mp-spdz-0.3.6 \
            --feedback_flag \
            --model_name deepseek-r1 \
            --provider_name bytedance
done


experimental=${1:-glm4-2-}
for input_file in ${input_files[@]};do
    echo ${input_file}
    python src/pipeline-mp.py \
            --input_file ${input_file} \
            --IR_file intermediate_representation.jsonl \
            --experimental ${experimental} \
            --spdz_path ~/mp-spdz-0.3.6 \
            --feedback_flag \
            --model_name glm-4-long 
done





# python src/pipeline-mp.py --input_file if_test.json --IR_file intermediate_representation.jsonl --experimental deepseek-v3- --spdz_path ~/mp-spdz-0.3.6 --feedback_flag --model_name deepseek-v3 --provider_name bytedance
