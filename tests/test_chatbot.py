import json
import unittest
from unittest.mock import patch, MagicMock
from src.JobTracker.chatbot import ChatBot, ChatGPT

MODEL_LIST_RETURN = {
    "object": "list",
    "data": [
        {
            "id": "gpt-3.5-turbo",
            "object": "model",
            "created": None,
            "owned_by": "openai",
        },
        {
            "id": "gpt-4-1106-preview",
            "object": "model",
            "created": None,
            "owned_by": "openai",
        }
    ],
    "model": None
}

class TestChatBot(unittest.TestCase):

    @patch('openai.Model.list')
    def test_gen_prompt(self, mock_model_list):
        mock_model_list.return_value = MODEL_LIST_RETURN
        chat_bot = ChatGPT()
        info = "test email body"
        expected_prompt = 'If this is a mail from a company I applied to or interviewed with before, ' + \
            'use get_mail_info to get information, here is the mail body: ' + info
        self.assertEqual(chat_bot.gen_prompt(info), expected_prompt)


class TestChatGPT(unittest.TestCase):

    @patch('openai.Model.list')
    def setUp(self, mock_model_list):
        mock_model_list.return_value = MODEL_LIST_RETURN
        self.chat_gpt = ChatGPT()

    @patch('openai.ChatCompletion.create')
    @patch('src.JobTracker.config')
    def test_get_content_succeed(self, mock_config, mock_openai_chatcompletion_create):
        info = {'body': 'test email body'}
        mock_config.API_KEY = 'test_api_key'
        mock_config.FUNCTION = 'test_function'
        # Mock the API response
        mock_choice = MagicMock()
        mock_choice.finish_reason = 'function_call'
        mock_choice.message = {
            'function_call': {
                'arguments': json.dumps({
                    'company': 'TestCompany',
                    'state': 'TestState',
                    'next_step': 'TestNextStep',
                    'score' : 100
                })
            }
        }

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai_chatcompletion_create.return_value = mock_response
        state, data = self.chat_gpt.get_content(info)
        self.assertEqual(state, 'Succeed')
        self.assertEqual(data['company'], 'TestCompany')
        self.assertEqual(data['state'], 'TestState')
        self.assertEqual(data['next_step'], 'TestNextStep')

    @patch('openai.ChatCompletion.create')
    @patch('src.JobTracker.config')
    def test_get_content_failed(self, mock_config, mock_openai_chatcompletion_create):
        info = {'body': 'test email body'}
        mock_config.API_KEY = 'test_api_key'
        mock_config.FUNCTION = 'test_function'
        # Mock the API response
        mock_choice = MagicMock()
        mock_choice.finish_reason = 'other'
        mock_choice.message = {}
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_openai_chatcompletion_create.return_value = mock_response

        state, data = self.chat_gpt.get_content(info)

        self.assertEqual(state, 'Failed')
        self.assertEqual(data, 'Not related to a job application or interview process')


if __name__ == '__main__':
    unittest.main()
