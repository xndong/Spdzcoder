# ICSE_code
We make artifacts available to the program committee in ICSE 2026 1st Cycle.

We release the main component of our code: inference, evaluation and analysis

## Preparation
### 1. Create Environment for the Experiments

Install the required packages
```bash
# ignore the dependencies
pip install --no-deps -r requirements.txt
# alternatively, install the dependencies
pip install -r requirements.txt
```
### 2. Prepare API Keys or Service Endpoint for the Experiments
Make sure setup your API keys or service endpoint in `utility/model.py` and `utility/model_msg.py` before running experiments.
- OpenAI API key
- Claude API key
- API key in cloud services: DeepInfra or SiliconFlow
- Azure OpenAI endpoint and API key (optional)

We leave the API keys or service endpint as a placeholder in the code. You need to replace them with your own API keys or service endpoint. The place holder is like `PLACEHOLDER_FOR_YOUR_API_KEY` or `PLACEHOLDER_FOR_YOUR_AZURE_OPENAI_ENDPOINT`.

## Structure of the code repo
### 1. data
The data directory consists the raw data (generated MP-SPDZ code) of the main experiment results. Concretely,

    a. ./data/input_processed_data: the splits of SPDZEval
    
    b. ./data/stage_1_output: the generated CFP code after refactoring stage.

    c. ./data/stage_2_SPDZ_output: the generated MP-SPDZ code by SPDZCoder after generation stage.

    d. ./data/stage_3_output: the refined MP-SPDZ code by SPDZCoder, if potential bugs are introduced, after repair stage.

    e. ./data/baseline_output: the generated MP-SPDZ code by baseline methods.

### 2. inference:
The src directory includes the implementation of our SPDZCoder pipeline.
    
a. `pipeline-mp.py` is the entry point for running our framework. It will use apply_high_rules.py, apply_low_rules.py, and apply_feedback_tc.py to perform the three stages of our method. To run the pipeline, you can use the following command:
    
```bash
bash scripts/run-various-LLMs-as-backbone.sh
```

We also provide a single process version: `pipeline.py`

To run direct translation, you can use the following command:

```bash
bash scripts/run-baseline-GeneralCodeReasoningLLMs.sh
```

To run API Doc, we provide the following command:
```bash
# For general LLMs
bash scripts/run-baseline-DeepseekV3.sh
# For code LLMs
bash scripts/run-baseline-Qwen25coder-DeepseekV25.sh
# For reasonging LLMs
bash scripts/run-baseline-QwQ-DeepseekR1.sh
```

### 3. evaluation
The evaluation the effective of SPDZCoder and baseline methods. We provide the following command to run the evaluation:
```
scripts/run-evaluate-experimental-mp.sh
```


### 4. utility:
The utility directory includes helperf module of our code repo, including parsing argument, computing token consumption of LLMs, and invoking LLM AIP service (`model.py` and `model_msg.py`).
