# /bin/bash

# %%%%%%%%%%%%%%%%%%%%%%% Main Evaluation  %%%%%%%%%%%%%%%%%%%%%%%
declare -a experimentals=('experiment-1')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir stage_2_SPDZ_output \
        --model_name "" \
        --experimental ${experimental}
done

declare -a experimentals=('experiment-1')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir stage_3_output \
        --model_name "" \
        --experimental ${experimental}
done


# %%%%%%%%%%%%%%%%%% Evaluate direct translation with various LLMs %%%%%%%%%%%%%%%%%%
declare -a experimentals=('gpt-4o-naive-' 'deepseek-v3-naive-' 'deepseek-v2.5-naive-' 'Qwen2.5-coder-32b-naive-' 'deepseek-R1-naive-' 'QwQ-naive-')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir baseline_output/naive-baseline \
        --model_name "" \
        --experimental ${experimental} \
        --eval_baseline
done

declare -a experimentals=('openai-o1-naive-' 'openai-o3-mini-naive-')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir baseline_output/naive-baseline \
        --model_name "" \
        --experimental ${experimental} \
        --eval_baseline
done



# %%%%%%%%%%%%%%%%%%%% Evaluate API Doc with various LLMs %%%%%%%%%%%%%%%%%%%%%%%
declare -a experimentals=('deepseek-v3-1-' 'deepseek-v2.5-w-API-1-' 'Qwen2.5-coder-7b-w-API-1-' 'Qwen2.5-coder-32b-w-API-1-' 'deepseek-R1-w-API-1-' 'QwQ-w-API-1-')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir baseline_output \
        --model_name "" \
        --experimental ${experimental} \
        --eval_baseline
done

declare -a experimentals=('openai-o1-w-API-1-' 'openai-o3-mini-w-API-1-')
for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir baseline_output \
        --model_name "" \
        --experimental ${experimental} \
        --eval_baseline
done



# %%%%%%%%%%%%%%%%%%%%%%% Evaluate SPDZCoder with various LLMs as backbones  %%%%%%%%%%%%%%%%%%%%%%%
# declare -a experimentals=('glm4-2-')
# declare -a experimentals=('deepseek-v3-pure-')
declare -a experimentals=('deepseek-r1-pure-')

for experimental in "${experimentals[@]}"; do
    python evaluation/evaluate_experimental-mp.py \
        --spdz_path ~/mp-spdz-0.3.6 \
        --spdzcode_dir stage_3_output \
        --model_name "" \
        --experimental ${experimental}
done