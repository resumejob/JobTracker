import json
import openai
from abc import ABC, abstractmethod
from .config import API_KEY, FUNCTION

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

    def gen_prompt(self, info):
        """Generate a prompt for the chatbot."""
        return ('If this is a mail from a company I applied to or interviewed with before, '
                'use get_mail_info to get information, here is the mail body: ' + info)

    def get_content(self, info):
        """Get content from the chatbot based on the provided information."""
        prompt = self.gen_prompt(info['body'])
        try:
            completion = openai.ChatCompletion.create(
                model='gpt-4-1106-preview',
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
