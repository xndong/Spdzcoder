import os, re, time
from typing import Any
import anthropic
# import google.generativeai as genai
from openai import OpenAI, AzureOpenAI

gpt_apis = ['PLACEHOLDER_FOR_YOUR_API_KEY']
claude_apis = ["PLACEHOLDER_FOR_YOUR_API_KEY"]
zhipu_apis = ["PLACEHOLDER_FOR_YOUR_API_KEY"]

AZURE_OPENAI_ENDPOINT = "PLACEHOLDER_FOR_YOUR_AZURE_OPENAI_ENDPOINT"
AZURE_OPENAI_API_KEY = "PLACEHOLDER_FOR_YOUR_AZURE_OPENAI_API_KEY"
os.environ["AZURE_OPENAI_ENDPOINT"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_OPENAI_API_KEY"] = AZURE_OPENAI_API_KEY

import logging 
logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG) 
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s]-[%(levelname)s]: %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

from colorama import Fore, init
init(autoreset=True)


class GPT:
    
    def __init__(self, model_name, temperature=0.9, seed=None, api_idx=0): 
        
        self.model_name = model_name
        self.client = OpenAI(api_key=gpt_apis[api_idx])
        self.T = temperature
        self.seed=seed
    
    def __call__(self, messages, n:int=1, **kwargs: Any) -> Any:    #* n: How many chat completion choices to generate for each input messages.
        return self.call_wrapper(messages, n, self.model_name, self.T, self.seed, **kwargs)
        
    def call_wrapper(self, messages, n, model, temperature, seed, **kwargs: Any) -> Any:
        retry_count, retries = 0, 5
        response = None
        while retry_count < retries:
            try:                
                if 'o1' not in self.model_name and 'o3-mini' not in self.model_name:    
                    response = self.client.chat.completions.create(messages=messages, n=n, model=model, temperature=temperature, seed=seed, max_tokens=2048, **kwargs)
                else:                                                                   
                    if 'o1-mini' in self.model_name:        
                        response = self.client.chat.completions.create(messages=messages, n=n, model=model, seed=seed, max_completion_tokens=2048, **kwargs)
                    else:                                   
                        response = self.client.chat.completions.create(messages=messages, n=n, model=model, seed=seed, max_completion_tokens=2048, reasoning_effort='medium', **kwargs)
                break
            except Exception as e:
                retry_count += 1
                backoff_time = 2**retry_count+1
                time.sleep(backoff_time)
                logger.exception(f"error exception: {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")     
        if response == None : logger.error(f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.')
        
        return response
    
    def resp_parse(self, response)->list:
        n = len(response.choices)
        return [response.choices[i].message.content for i in range(n)] if n > 1 else response.choices[0].message.content

    def code_parse(self, response):             # from response to code
        text_response = response.choices[0].message.content
        def extract_code_blocks(text):
            pattern = r"```(\w+-*\w+)?\s*(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)  # return a list that includes all matches
            return matches[-1][1]
        code_responese = extract_code_blocks(text_response)

        # token consumption
        completion_token_consumption = response.usage.completion_tokens
        prompt_token_consumption = response.usage.prompt_tokens
        total_token_consumption = response.usage.total_tokens

        return code_responese

class AzureGPT4o:
    
    def __init__(self, model_name, temperature=0.9, seed=None, api_idx=0):
        
        self.model_name = model_name
        if model_name in ["azure-gpt4o", "azure-gpt4o-mini", "azure-gpt4", "azure-gpt35-turbo"]:
            self.client = AzureOpenAI(azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), api_key=os.getenv("AZURE_OPENAI_API_KEY"),  api_version="2024-02-01")
        elif model_name in ["azure-openai-o1", "azure-openai-o1-mini", "azure-openai-o3-mini"]:
            AZURE_OPENAI_ENDPOINT_2 = "PLACEHOLDER_FOR_YOUR_AZURE_OPENAI_ENDPOINT"
            AZURE_OPENAI_API_KEY_2 = "PLACEHOLDER_FOR_YOUR_AZURE_OPENAI_API_KEY"
            self.client = AzureOpenAI(azure_endpoint = AZURE_OPENAI_ENDPOINT_2, api_key=AZURE_OPENAI_API_KEY_2,  api_version="2024-12-01-preview")                     
        self.T = temperature
        self.seed=seed
    
    def __call__(self, messages, n:int=1, **kwargs: Any) -> Any:    #* n: How many chat completion choices to generate for each input message.
        if self.model_name == "azure-gpt4o":
            azure_deploy_name = "spdzcoder"
        elif self.model_name == "azure-gpt4o-mini":
            azure_deploy_name = "gpt-4o-mini"
        elif self.model_name == "azure-gpt4":
            azure_deploy_name = "gpt-4"
        elif self.model_name == "azure-gpt35-turbo":
            azure_deploy_name = "gpt-35-turbo"
        elif self.model_name == "azure-openai-o1":
            azure_deploy_name = "o1"
        elif self.model_name == "azure-openai-o1-mini":
            azure_deploy_name = "o1-mini"
        elif self.model_name == "azure-openai-o3-mini":
            azure_deploy_name = "o3-mini"
        else:
            raise ValueError(f"model_name should be in ['azure-gpt4o', 'azure-gpt4o-mini', 'azure-gpt4', 'azure-gpt35-turbo', 'azure-openai-o1', 'azure-openai-o1-mini', 'azure-openai-o3-mini'], but got {self.model_name}")
        
        if self.model_name in ["azure-gpt4o", "azure-gpt4o-mini", "azure-gpt4", "azure-gpt35-turbo"]:
            return self.call_wrapper(messages=messages, n=n, model=azure_deploy_name, temperature=self.T, seed=self.seed, **kwargs)
        elif self.model_name in ["azure-openai-o1", "azure-openai-o1-mini", "azure-openai-o3-mini"]:    
            return self.call_wrapper(messages=messages, n=n, model=azure_deploy_name, seed=self.seed, **kwargs)
        else:
            raise NotImplementedError
        
    def call_wrapper(self, **kwargs: Any) -> Any:
        retry_count, retries = 0, 5
        response = None
        while retry_count < retries:
            try:
                if 'system' in kwargs: kwargs.pop('system')
                response = self.client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                retry_count += 1
                backoff_time = 2**retry_count+1
                time.sleep(backoff_time)
                logger.exception(f"error exception: {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")     
        if response == None : logger.error(f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.')
        
        return response
    
    def resp_parse(self, response)->list:
        n = len(response.choices)
        return [response.choices[i].message.content for i in range(n)] if n > 1 else response.choices[0].message.content

    def code_parse(self, response):             # from response to code
        text_response = response.choices[0].message.content
        def extract_code_blocks(text):
            pattern = r"```(\w+-*\w+)?\s*(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)  # return a list that includes all matches
            return matches[-1][1]                       
        code_responese = extract_code_blocks(text_response)

        # token consumption
        completion_token_consumption = response.usage.completion_tokens
        prompt_token_consumption = response.usage.prompt_tokens
        total_token_consumption = response.usage.total_tokens

        return code_responese

class AnthropicClaude:
    def __init__(self, model_name, temperature=0.9, api_idx=0) -> None:
        self.T = temperature
        if model_name == 'claude-v2':
            self.model_name = 'claude-2.0'                  # $8/$24
        elif model_name == 'claude-v2.1':
            self.model_name = 'claude-2.1'                  # $8/$24, an updated version of claude-2.0
        elif model_name == 'claude-3-opus':
            self.model_name = 'claude-3-opus-20240229'      # $15/$75
        elif model_name == 'claude-3-sonnet':
            self.model_name = 'claude-3-sonnet-20240229'    # $3/$15
        elif model_name == 'claude-3-haiku':
            self.model_name = 'claude-3-haiku-20240307'     # $0.25/$1.25
        elif model_name == 'claude-3.5-sonnet':
            self.model_name = 'claude-3-5-sonnet-20240620'  # $3/$15 # claude-3-5-sonnet-20241022
        elif model_name == 'claude-3.5-haiku':
            self.model_name = 'claude-3-5-haiku-20241022'   # $1/$5
        else:
            raise ValueError(f"model_name should be in https://docs.anthropic.com/en/docs/about-claude/models, but got {model_name}")
        self.client = anthropic.Anthropic(api_key = claude_apis[api_idx])
    
    def __call__(self, messages, n=1, **kwargs: Any) -> Any:
        return self.call_wrapper(messages, self.model_name, self.T, **kwargs)

    def call_wrapper(self, messages, model, temperature, **kwargs: Any) -> Any:
        retry_count, retries = 0, 5
        response = None
        while retry_count < retries:
            try:
                if 'system' in kwargs: 
                    print(Fore.RED + f"system_prompt: {kwargs['system']}" + Fore.RESET) 
                response = self.client.messages.create(messages=messages, model=model, temperature=temperature, max_tokens=2048, **kwargs) 
                break
            except Exception as e:
                retry_count += 1
                backoff_time = 2**retry_count+1
                time.sleep(backoff_time)
                logger.exception(f"error exception: {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")     
        if response == None : logger.error(f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.')

        return response

    def resp_parse(self, response) -> list:
        n = len(response.content)
        return [response.content[i].text for i in range(n)]  if n > 1 else response.content[0].text

import zhipuai
class ZhipuLLM:
    def __init__(self, model_name, temperature=0.9, api_idx=0, provider_name='zhipu') -> None:
        
        self.model_name = model_name
        self.client = zhipuai.ZhipuAI(api_key = zhipu_apis[api_idx])
        self.T = temperature
        
    def __call__(self, messages, n:int=1, **kwargs: Any) -> Any:    #* n: How many chat completion choices to generate for each input message.
        return self.call_wrapper(messages, n, self.model_name, self.T, **kwargs)
    
    def call_wrapper(self, messages, n, model, temperature, **kwargs: Any) -> Any:
        retry_count, retries = 0, 5
        response = None
        while retry_count < retries:
            try:
                response = self.client.chat.completions.create(messages=messages, model=model, temperature=temperature, max_tokens=2048, top_p=1.0, **kwargs)
                break
            except Exception as e:
                retry_count += 1
                backoff_time = 2**retry_count+1
                time.sleep(backoff_time)
                logger.exception(f"error exception: {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")
        if response == None : logger.error(f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.')
        
        return response
    
    def resp_parse(self, response)->list:
        n = len(response.choices)
        return [response.choices[i].message.content for i in range(n)] if n > 1 else response.choices[0].message.content
    
    def code_parse(self, response):             # from response to code
        text_response = response.choices[0].message.content
        def extract_code_blocks(text):
            pattern = r"```(\w+-*\w+)?\s*(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)  # return a list that includes all matches
            return matches[-1][1]                       
        code_responese = extract_code_blocks(text_response)
        
        return code_responese

class BaseAPIModels:
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        self.api = {"silicon":["PLACEHOLDER_FOR_YOUR_API_KEY"],
                    "deepinfra":"PLACEHOLDER_FOR_YOUR_API_KEY",
                    "bytedance":"PLACEHOLDER_FOR_YOUR_API_KEY",
                    "tencent": "PLACEHOLDER_FOR_YOUR_API_KEY",
                    }
        self.base_url = {"silicon":"https://api.siliconflow.cn/v1", 
                         "deepinfra":"https://api.deepinfra.com/v1/openai", 
                         "bytedance":"https://ark.cn-beijing.volces.com/api/v3",
                         "tencent":"https://api.lkeap.cloud.tencent.com/v1",
                         }
        self.api_key = self.api[provider_name][api_idx] if provider_name == 'silicon' else self.api[provider_name]
        self.base_url = self.base_url[provider_name]
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model_name = model_name
        self.provider_name = provider_name
        self.T = temperature
        self.model_DI = None
        
    def __call__(self, messages, n=1, top_p=0.9, **kwargs: Any) -> Any:
        
        if self.provider_name == 'tencent' and 'r1' in self.model_name:                                                 # tencent's deepseek-r1 does not support `top_p`
            response = self.call_wrapper(messages=messages, n=n, model=self.model_DI, temperature=self.T, **kwargs)
        else:
            response = self.call_wrapper(messages=messages, n=n, model=self.model_DI, temperature=self.T, top_p=top_p, **kwargs)
        return response
    

    def call_wrapper(self, **kwargs):
        logger.info(f'>>> model_name: {self.model_name}, provider_name: {self.provider_name}, model_DI: {self.model_DI}')
        retry_count, retries = 0, 5
        response = None
        while retry_count < retries:
            try:
                if 'system' in kwargs: kwargs.pop('system') 
                response = self.client.chat.completions.create(**kwargs)
                break
            except Exception as e:
                retry_count += 1
                backoff_time = 2**retry_count+1
                time.sleep(backoff_time)
                logger.exception(f"error exception: {e}")
                logger.info(f"Retrying in {backoff_time} seconds...")     
        if response == None : logger.error(f'>>> Fail to generate response after trying {retries} times invoking. The response will be initial `None`.')        
        
        return response


    def resp_parse(self, response)->list:       # from response to text
        n = len(response.choices)
        return [response.choices[i].message.content for i in range(n)] if n > 1 else response.choices[0].message.content

    def code_parse(self, response):             # from response to code
        text_response = response.choices[0].message.content
        def extract_code_blocks(text):
            pattern = r"```(\w+-*\w+)?\s*(.*?)```"
            matches = re.findall(pattern, text, re.DOTALL)  # return a list that includes all matches
            return matches[-1][1]                       
        code_responese = extract_code_blocks(text_response)

        # token consumption
        completion_token_consumption = response.usage.completion_tokens
        prompt_token_consumption = response.usage.prompt_tokens
        total_token_consumption = response.usage.total_tokens

        return code_responese



# Llama3.1
class Llama3_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert 'llama3-api' in model_name
        assert provider_name in ['silicon', 'deepinfra']
        
        if '8b' in model_name:
            self.model_DI = "meta-llama/Meta-Llama-3.1-8B-Instruct" 
        elif '70b' in model_name:
            self.model_DI = "meta-llama/Meta-Llama-3.1-70B-Instruct"
        else:
            raise ValueError(f"model_name should be 'llama3-api-7b' or 'llama3-api-70b', but got {model_name}")
      
  
# Deepseek-R1 and Deepseek-V3
class Deepseek_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.6) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert 'deepseek' in model_name
        assert provider_name in ['silicon', 'bytedance', 'tencent']
        
        if provider_name == 'silicon':
            if 'r1' in model_name:
                self.model_DI = "deepseek-ai/DeepSeek-R1" if 'sk-pgnyk' in self.api_key else "Pro/deepseek-ai/DeepSeek-R1"
            elif 'v3' in model_name:
                self.model_DI = "deepseek-ai/DeepSeek-V3"
            else:
                raise NotImplementedError
        elif provider_name == 'bytedance':
            if 'r1' in model_name:
                self.model_DI = "ep-20250213181123-cwwqh"
            elif 'v3' in model_name:
                self.model_DI = "ep-20250221204208-r8czf"
            else: 
                raise NotImplementedError
        elif provider_name == 'tencent':
            if 'r1' in model_name:
                self.model_DI = "deepseek-r1"
            else: 
                raise NotImplementedError
        else:
            raise ValueError(f"Got unsupported model name in LLM provider {provider_name}: {model_name}. Choices should be 'deepseek-r1' or 'deepseek-v3'.")


# Qwen2.5-coder is the upgraded version of CodeQwen
class QwenCoder_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert 'qwen2.5-coder' in model_name
        assert provider_name in ['silicon']
        
        if '7b' in model_name:
            self.model_DI = "Qwen/Qwen2.5-Coder-7B-Instruct" if 'sk-pgnyk' in self.api_key else "Pro/Qwen/Qwen2.5-Coder-7B-Instruct"
        elif '32b' in model_name:
            self.model_DI = "Qwen/Qwen2.5-Coder-32B-Instruct"
        else:
            raise ValueError(f"model_name should be `qwen2.5-coder-7b` or `qwen2.5-coder-32b`, but got {model_name}")
   
   
# DeepSeek-V2.5 is the upgraded version of DeepseekCoder-33B
class DeepseekV25_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert model_name == 'deepseek-v2.5'
        assert provider_name in ['silicon']
        
        self.model_DI = "deepseek-ai/DeepSeek-V2.5"


# QwQ is the reasoning model of Qwen
class QwQ_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert model_name == 'qwen-qwq'
        assert provider_name in ['silicon']

        self.model_DI = "Qwen/QwQ-32B-Preview"


# Distilled version of Qwen and Llama3.1
class Distilled_api(BaseAPIModels):
    def __init__(self, model_name, provider_name = 'silicon', api_idx = 0, temperature=0.9) -> None:
        super().__init__(model_name, provider_name, api_idx, temperature)
        assert 'distilled' in model_name
        assert provider_name in ['silicon']
        
        if 'qwen' in model_name:
            self.model_DI = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B" 
        elif 'llama3' in model_name:
           self.model_DI = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
        else:
            raise ValueError(f"model_name should be `distilled-llama3-70b` or `distilled-qwen-32b`, but got {model_name}")



def load_model(model_name, api_idx=0, **kwargs):
    
    if model_name in ["azure-gpt4o", "azure-gpt4o-mini", "azure-gpt4", "azure-gpt35-turbo", "azure-openai-o1", "azure-openai-o1-mini", "azure-openai-o3-mini"]:
        return AzureGPT4o(model_name, **kwargs)
    
    elif "gpt" in model_name and "gpt2" not in model_name:
        return GPT(model_name, **kwargs)
        
    elif "o1" in model_name or "o3-mini" in model_name:
        return GPT(model_name, **kwargs)
    
    elif "claude" in model_name:
        return AnthropicClaude(model_name, **kwargs)
    
    elif "llama3" in model_name:
        return Llama3_api(model_name, **kwargs)
    
    elif model_name in ["deepseek-r1", "deepseek-v3"]:
        return Deepseek_api(model_name, **kwargs)
    
    elif "qwen2.5-coder" in model_name:
        return QwenCoder_api(model_name, **kwargs)
    
    elif model_name == "deepseek-v2.5":
        return DeepseekV25_api(model_name, **kwargs)
    
    elif model_name == "qwen-qwq":
        return QwQ_api(model_name, **kwargs)

    elif "glm" in model_name:
        return ZhipuLLM(model_name, **kwargs)
    
    else:
        raise ValueError(f"model_name invalid")


