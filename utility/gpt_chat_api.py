import os
import re
import time
from colorama import Fore, Style
import openai
from openai import OpenAI
from openai import OpenAIError


#************* helper functions in processing response from LLMs *****************#

# extract code block from GPT response
def extract_code_blocks(text):

    pattern = r"```(\w+-*\w+)?\s*(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)  # return a list that includes all matches
    if matches:
        return matches[-1][1]
    else:
        raise Exception('No substring in text that matches the pattern.')

# extract code block from Claude response
def extract_code_blocks_claude(text):
    ...

#**************** make gpt request in official approach **************************#

def make_requests(
        messages, model_name, max_tokens, temperature, top_p,
        frequency_penalty, presence_penalty, stop_sequences, logprobs, n, best_of, retries=4, api_key=None, organization=None
    ):
    response = None

    if api_key is not None:
        openai.api_key = api_key
    if organization is not None:
        openai.organization = organization
    client = OpenAI()

    retry_cnt, backoff_time = 0, 3
    while retry_cnt <= retries:
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=model_name,
                # max_tokens=max_tokens,
                temperature=temperature,
                # top_p=top_p,
                # frequency_penalty=frequency_penalty,
                # presence_penalty=presence_penalty,
                # stop=stop_sequences,
                # logprobs=logprobs,
                # n=n,
                # best_of=best_of,
            )
            break
        except openai.OpenAIError as e:
            print(f"OpenAIError: {e}.")
            print(f"Retrying in {backoff_time} seconds...")
            time.sleep(backoff_time)
            backoff_time *= 2

            retry_cnt += 1

    if response == None : print(Fore.YELLOW + f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.' + Style.RESET_ALL)

    return response


def post_process_response(response):

    # text_response
    text_response = response.choices[0].message.content

    # extract code between ```
    # code_responese = text_response
    code_responese = extract_code_blocks(text_response)

    # token consumption
    completion_token_consumption = response.usage.completion_tokens
    prompt_token_consumption = response.usage.prompt_tokens
    total_token_consumption = response.usage.total_tokens

    return code_responese


#*************************** make Tsinghua Zhipu request ****************************#

def make_requests_zhipu(
        messages, model_name, max_tokens, temperature, top_p, stop_sequences=None,
        retries=4, api_key=None, request = 'use_sync'
    ):
    response = None

    zhipu_api_key = api_key if api_key is not None else os.environ.get("ZHIPU_API_KEY")
    client = zhipuai.ZhipuAI(api_key = zhipu_api_key)

    if request == 'use_sync':

        retry_cnt, backoff_time = 0, 3
        while retry_cnt <= retries:
            try:
                response = client.chat.completions.create(
                    messages=messages,
                    model=model_name,   # "glm-4"
                    # max_tokens=max_tokens,
                    temperature=temperature,
                    # top_p=top_p,
                    # stop=stop_sequences
                )
                break
            except (zhipuai.core._errors.APIStatusError, zhipuai.core._errors.APIResponseError, zhipuai.core._errors.APITimeoutError) as e:
                print(f"ZhiPu API Invoke Error: {e}.")
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
                backoff_time *= 2

                retry_cnt += 1

    elif request == 'use_async':
        print('Refer to the official API docs for async requests.')
        raise NotImplementedError
    else:
        raise NotImplementedError

    if response == None : print(Fore.YELLOW + f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.' + Style.RESET_ALL)

    return response

def post_process_response_zhipu(response):

    # text_response
    text_response = response.choices[0].message.content

    # extract code between ```
    code_responese = extract_code_blocks(text_response)

    # token consumption
    completion_token_consumption = response.usage.completion_tokens
    prompt_token_consumption = response.usage.prompt_tokens
    total_token_consumption = response.usage.total_tokens

    return code_responese

# https://open.bigmodel.cn/pricing
# https://open.bigmodel.cn/dev/api#language
# https://open.bigmodel.cn/dev/api#error-code