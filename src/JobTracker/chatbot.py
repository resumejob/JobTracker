import json
import openai
import tiktoken
import logging
import requests
from datetime import datetime
from abc import ABC, abstractmethod
from .config import OPENAI_API_KEY, FUNCTION, MODEL, PRICE, LLAMA_URL, LLAMA_MODEL, THRESHOLD, FIX_ANSWER

# Set the API key for OpenAI once, assuming this is a module-level operation
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


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


class Llama(ChatBot):
    def __init__(self) -> None:
        super().__init__()
        self.url = LLAMA_URL
        self.model= LLAMA_MODEL

    def gen_prompt(self, info):
        return super().gen_prompt(info)

    def get_confidence(self, info):
        return ('Rate my email as an application email on a scale of 1 to 100. return a a json \{"score": int\}  Here is the mail body: ' + info )

    def gen_prompt_company(self, info):
        return ('what is the company I appied? return a json \{"Company": string\} Here is the mail body: ' + info)

    def gen_prompt_state(self, info):
        return ('what is the state of this application? return a json \{"State": string\} Here is the mail body: ' + info)

    def gen_prompt_next_step(self, info):
        return ('what should be next step in the application process as an applicant? return a json \{"NextStep": string\} Here is the mail body: ' + info)

    def send_request(self, prompt, fix):
        data = None
        proxies = {
            "http": None,
            "https": None,
        }
        if fix:
            data = {
                "model": self.model,
                "prompt": prompt,
                "format": "json",
                "stream": False,
                "options": {"seed": 42}
            }
        else:
            data = {
                "model": self.model,
                "prompt": prompt,
                "format": "json",
                "stream": False
            }
        res = requests.post(self.url, json=data, proxies=proxies)
        return json.loads(res.text)["response"]

    def get_content(self, info):
        confidence = self.get_confidence(info['body'])
        level = self.send_request(confidence, FIX_ANSWER)
        prompt1 = self.gen_prompt_company(info['body'])
        name = self.send_request(prompt1, FIX_ANSWER)
        prompt2 = self.gen_prompt_state(info['body'])
        state = self.send_request(prompt2, FIX_ANSWER)
        prompt3 = self.gen_prompt_next_step(info['body'])
        step = self.send_request(prompt3, FIX_ANSWER)
        try:
            info['company'] = json.loads(name)["Company"]
            info['state'] = json.loads(state)["State"]
            info['next_step'] = json.loads(step)["NextStep"]
        except KeyError:
            return ('Failed', 'JSON not formatted correctly')
        except Exception:
            return ('Failed', 'Connection to Llama failed')
        else:
            try:
                date_object = datetime.strptime(info['date'], "%a, %d %b %Y %H:%M:%S %z")
                month_day_year_time = date_object.strftime("%b %d %Y %H:%M:%S")
            except ValueError:
                try:
                    date_object = datetime.strptime(info['date'], "%a, %d %b %Y %H:%M:%S %z (%Z)")
                    month_day_year_time = date_object.strftime("%b %d %Y %H:%M:%S")
                except ValueError:
                    logging.warn("Unable to parse date")
            info['state'] = json.dumps({info['state']:month_day_year_time})
            info['rank'] = date_object
            return ('Succeed', info)


class ChatGPT(ChatBot):
    """Concrete implementation of a ChatBot using OpenAI's GPT."""

    def __init__(self) -> None:
        super().__init__()
        self.models = set()
        try:
            for i in list(openai.Model.list().values())[1]:
                name = i["id"]
                if "gpt" in name:
                    self.models.add(name)
        except openai.error.OpenAIError as e:
            logger.error(f'Failed to fetch model list: {e}')

    def get_cost(self, mails):
        message = []
        for mail in mails:
            message.append({'role': 'user', 'content': self.gen_prompt(mail['body'])})
        token = self.num_tokens_from_messages(message, MODEL)
        prices = self.pricing_for_1k_tokens(MODEL)
        input_price = prices[0] * token / 1000.0
        return f"{token} prompt tokens in total. Need $ {str(round(input_price, 5))} for input."

    def gen_prompt(self, info):
        """Generate a prompt for the chatbot."""
        return (f'If this email has a {THRESHOLD}% confidence level that it is from a company I applied to or interviewed with before, '
                f'use get_mail_info to get information, otherwise just ignore it. Here is the mail body: {info}')

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
        except openai.error.OpenAIError as e:
            return ('Failed', f'OpenAI API error: {str(e)}')
        except json.JSONDecodeError:
            return ('Failed', 'Failed to decode JSON from function call')
        else:
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
                    # add initial value
                    month_day_year_time = 'Sun, 99 Dec 9999 99:99:99 '
                    date_object = datetime.strptime('Mon, 15 Mar 2021 14:45:30 +0000', "%a, %d %b %Y %H:%M:%S %z")
                    try:
                        date_object = datetime.strptime(info['date'], "%a, %d %b %Y %H:%M:%S %z")
                        month_day_year_time = date_object.strftime("%b %d %Y %H:%M:%S")
                    except ValueError:
                        try:
                            date_object = datetime.strptime(info['date'], "%a, %d %b %Y %H:%M:%S %z (%Z)")
                            month_day_year_time = date_object.strftime("%b %d %Y %H:%M:%S")
                        except ValueError:
                            print("Unable to parse date")
                    info['state'] = json.dumps({info['state']:month_day_year_time})
                    info['rank'] = date_object
                    return ('Succeed', info)
            else:
                return ('Failed', 'Not related to a job application or interview process')

    def num_tokens_from_messages(self, messages, model="gpt-4-1106-preview"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            logging.warn("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
            tokens_per_name = -1
        elif model in self.models:
            tokens_per_message = 3
            tokens_per_name = 1
            if model == "gpt-3.5-turbo":
                logging.warn("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            if model == "gpt-4":
                logging.warn("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
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
        if model in PRICE:
            return PRICE[model]
        elif "gpt-3.5-turbo" in model:
            logging.warn("Warning: unclear model, taking price of gpt-3.5-turbo-0613.")
            return PRICE["gpt-3.5-turbo-0613"]
        elif "gpt-4" in model:
            logging.warn("Warning: unclear model, taking price of gpt-4-0314.")
            return PRICE["gpt-4-0314"]
        else:
            raise NotImplementedError(
                f"""pricing_for_1k_tokens() is not implemented for model {model}.
                see https://openai.com/pricing#language-models"""
            )
