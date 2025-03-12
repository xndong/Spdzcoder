import argparse
import os
from pathlib import Path

#********************** parse arguments ****************************#

def parse_args():

    file_path = Path(__file__)
    current_dir = os.path.dirname(file_path)
    home_dir = os.path.dirname(current_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_name",
        default="gpt-3.5-turbo-1106",
        type=str,
        help="The name of chosen GPT model.",
    )
    parser.add_argument(
        "--provider_name",
        default=None,
        type=str,
        help="The provider name of MaaS.",
    )
    parser.add_argument(
        "--input_file",
        type=str,
        help="The input file that contains the input source code snippets.",
    )
    parser.add_argument(
        "--IR_file",
        default="intermediate_representation.jsonl",
        type=str,
        help="The intermediate representation (IR) file that contains the intermediate python codes.",
    )
    parser.add_argument(
        "--SPDZ_file",
        default="spdz.jsonl",
        type=str,
        help="The generated SPDZ code file after stage 2.",
    )
    parser.add_argument(
        "--output_file",
        default="output.jsonl",
        type=str,
        help="The output file to save the translated MP-SPDZ codes from GPT model after stage 3.",
    )
    parser.add_argument(
        "--feedback_flag",
        action='store_true',
        help="This flag controls whether run feedback or not.",
    )
    parser.add_argument(
        "--repetitions",
        default=2,
        type=int,
        help="The number of times that GPT model inferences.",
    )
    parser.add_argument(
        "--max_tokens",
        default=1536,
        type=int,
        help="The max_tokens parameter of GPT model.",
    )
    parser.add_argument(
        "--temperature",
        default=0.7,
        type=float,
        help="The temprature of GPT model.",
    )
    parser.add_argument(
        "--top_p",
        default=0.5,
        type=float,
        help="The `top_p` parameter of GPT model.",
    )
    parser.add_argument(
        "--frequency_penalty",
        default=0,
        type=float,
        help="The `frequency_penalty` parameter of GPT model.",
    )
    parser.add_argument(
        "--presence_penalty",
        default=0,
        type=float,
        help="The `presence_penalty` parameter of GPT model.",
    )
    parser.add_argument(
        "--stop_sequences",
        default=["\n\n"],
        nargs="+",
        help="The `stop_sequences` parameter of GPT model.",
    )
    parser.add_argument(
        "--logprobs",
        default=5,
        type=int,
        help="The `logprobs` parameter of GPT model"
    )
    parser.add_argument(
        "--n",
        default=1,
        type=int,
        help="The `n` parameter of GPT model. The number of responses to generate."
    )
    parser.add_argument(
        "--best_of",
        default=1,
        type=int,
        help="The `best_of` parameter of GPT model. The beam size on the GPT model server."
    )
    # check compilation error args and run evaluation args
    parser.add_argument(
        "--max_feedback",
        default=3,
        type=int,
        help="The max number of times that check whether there exists compilation errors in the generated spdz code."
    )
    parser.add_argument(
        '--compilation_dir',
        default=f"{home_dir}/data/stage_3_compilation_storage",
        type=str,
        help='Temporarily save the stage_2 output in order to compile it in stage_3.'
    )
    parser.add_argument(
        '--spdz_path',
        default="/Users/dongxn/mp-spdz-0.3.6",
        type=str,
        help='The MP-SPDZ home directory.'
    )
    # data storage directory v.s. Line 20~39 data storage filename.
    parser.add_argument(
        '--input_dir',
        default=f"{home_dir}/data/input_processed_data",
        type=str,
        help='The directory that stores processed data.')
    parser.add_argument(
        '--stage_1_IR_dir',
        default=f"{home_dir}/data/stage_1_IR_output",
        type=str,
        help='Stage_1 output directory is used to storge the generated python IR.')
    parser.add_argument(
        '--stage_2_SPDZ_dir',
        default=f"{home_dir}/data/stage_2_SPDZ_output",
        type=str,
        help='Stage_2 output directory is used to storge the generated MP-SPDZ code.')
    parser.add_argument(
        '--stage_3_output_dir',
        default=f"{home_dir}/data/stage_3_output",
        type=str,
        help='Stage_3 output directory is used to storge the generated MP-SPDZ code after fixing potentially existed errors.')

    parser.add_argument(
        '--baseline_output_dir',
        default=f"{home_dir}/data/baseline_output",
        type=str,
        help='Baseline output directory is used to storge the generated MP-SPDZ code by baselines.')

    # combine hand-crafted model name with mdHM to distinguish multiple experiments in stage2 (Optional)
    parser.add_argument(
        '--model_abbr',
        default='GPT4',
        type=str,
        help='For example, directory: SOME_FOLDER/GPT4/0426-1430')

    parser.add_argument(
        "--gpt4_model_name",
        default="gpt-4-turbo-2024-04-09", # "gpt-4-1106-preview"
        type=str,
        help="The name of chosen GPT-4 model.")
    parser.add_argument(
        "--use_gpt4_in_stage2_flag",
        default=False,
        action='store_true',
        help="This flag controls whether use gpt4 in stage2 or not.")
    parser.add_argument(
        "--experimental",
        default="",
        type=str,
        help="experimental prefix.")
    parser.add_argument(
        "--dump_IR_CoT",
        default=False,
        action='store_true',
        help="Dump used Python_IR in stage 2 and chosen/selected chat messages in stage 2.")
    parser.add_argument(
        "--eval_baseline",
        default=False,
        action='store_true',
        help="evaluate the baseline generation.")
    parser.add_argument(
        "--eval_extension",
        default=False,
        action='store_true',
        help="evaluate the generation from extension experiment.")
    parser.add_argument(
        '--eval_spdzcode_dir', 
        '--spdzcode_dir',
        dest='spdzcode_dir',
        type=str, 
        choices=['stage_2_SPDZ_output', 'stage_3_output', 'baseline_output', 'baseline_output/naive-baseline', 'baseline_output/unitrans-baseline', 'baseline_output/intertrans-baseline'], 
        help="Directory for SPDZ code to be evaluated."
    )

    return parser.parse_args()

#********************** feedback_stage and evaluation related functions ****************************#

