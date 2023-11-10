import json
import openai
import tiktoken
from abc import ABC, abstractmethod
from .config import API_KEY, FUNCTION, MODEL

# Set the API key for OpenAI once, assuming this is a module-level operation
openai.api_key = API_KEY


class ChatBot(ABC):
    """Abstract base class for a chatbot."""

    @abstractmethod
    def gen_prompt(self, info):
        """Generate a prompt for the chatbot based on the provided information."""
        pass

    @abstractmethod
    def get_content(self, info):
        """Abstract method to get content from the chatbot."""
        pass


class ChatGPT(ChatBot):
    """Concrete implementation of a ChatBot using OpenAI's GPT."""

    def get_cost(self, mails):
        message = []
        for mail in mails:
            message.append({'role': 'user', 'content': self.gen_prompt(mail['body'])})
        token = self.num_tokens_from_messages(message, MODEL)
        prices = self.pricing_for_1k_tokens(token, MODEL)
        input_price = prices[0] * token/1000.0
        print(f"{token} prompt tokens in total. Need $ f{str(input_price)} for input.")

    
    def gen_prompt(self, info):
        """Generate a prompt for the chatbot."""
        return ('If this is a mail from a company I applied to or interviewed with before, '
                'use get_mail_info to get information, here is the mail body: ' + info)

    def get_content(self, info):
        """Get content from the chatbot based on the provided information."""
        prompt = self.gen_prompt(info['body'])
        try:
            completion = openai.ChatCompletion.create(
                model=MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                functions=FUNCTION,
                function_call='auto'
            )

            if completion.choices[0].finish_reason == 'function_call':
                res = completion.choices[0].message['function_call']['arguments']
                res = json.loads(res)
                try:
                    info['company'] = res['company']
                    info['state'] = res['state']
                    info['next_step'] = res['next_step']
                except KeyError:
                    return ('Failed', 'JSON not formatted correctly')
                else:
                    return ('Succeed', info)
            else:
                return ('Failed', 'Not related to a job application or interview process')
        except openai.error.OpenAIError as e:
            return ('Failed', f'OpenAI API error: {str(e)}')
        except json.JSONDecodeError:
            return ('Failed', 'Failed to decode JSON from function call')

    def num_tokens_from_messages(self, messages, model="gpt-4-1106-preview"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            "gpt-4-1106-preview",
            "gpt-4-1106-vision-preview"
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
    
    def pricing_for_1k_tokens(self, model="gpt-4-1106-preview"):
        if model in {"gpt-4-1106-preview", "gpt-4-1106-vision-preview"}:
            return 0.01, 0.03
        elif "gpt-4-32k" in model:
            return 0.06, 0.12
        elif "gpt-4" in model:
            return 0.03, 0.06
        elif "gpt-3.5-turbo" in model:
            if "16k" in model:
                return 0.0010, 0.0020 
            else:
                return 0.0015, 0.0020
        else:
            raise NotImplementedError(
                f"""pricing_for_1k_tokens() is not implemented for model {model}. see https://openai.com/pricing#language-models"""
            )

