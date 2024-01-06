import unittest
from unittest.mock import patch, MagicMock
from src.JobTracker.utils import EmailMessage
import mailbox
import re

mock_config = MagicMock()
mock_config.KEYWORD = {'application', 'interview', 'job'}

mock_BeautifulSoup = MagicMock()

class TestEmailMessage(unittest.TestCase):

    @patch('mailbox.mbox', return_value=MagicMock())
    def setUp(self, mock_mbox):
        self.mbox_path = 'path/to/mbox'
        self.email_message = EmailMessage(self.mbox_path)

    def create_mock_mail(self):
        # Create a mock mail item
        mock_mail = MagicMock()
        mock_mail.__getitem__.side_effect = lambda key: {
            'subject': '=?utf-8?B?U3ViamVjdA==?=', # Base64 encoded "Subject"
            'from': 'John Doe <johndoe@example.com>',
            'to': 'Jane Doe <janedoe@example.com>',
            'date': 'Fri, 01 Jan 2021 10:00:00 +0000'
        }.get(key, '')
        return [mock_mail]

    @patch('src.JobTracker.utils.EmailMessage.get_mail_body', return_value="Mail body")
    @patch('src.JobTracker.utils.EmailMessage.related_to_application', return_value=True)
    def test_get_mail_info(self, mock_related_to_application, mock_get_mail_body):
        self.email_message.mail_lst = self.create_mock_mail()
        info = self.email_message.get_mail_info()[0]
        self.assertEqual(info['subject'], 'Subject')
        self.assertEqual(info['sender_name'], 'John Doe')
        self.assertEqual(info['sender_mail'], 'johndoe@example.com')
        self.assertEqual(info['recipient_name'], 'Jane Doe')
        self.assertEqual(info['recipient_mail'], 'janedoe@example.com')
        self.assertEqual(info['date'], 'Fri, 01 Jan 2021 10:00:00 +0000')
        self.assertEqual(info['body'], 'Mail body')
        self.assertTrue(mock_related_to_application.called)
        self.assertTrue(mock_get_mail_body.called)


    def test_clenup_body(self):
        text = "This is a test message. Visit http://example.com for details.\r\nNew line here."
        cleaned_text = self.email_message.cleanup_body(text)
        self.assertEqual(cleaned_text, "This is a test message. Visit  for details.New line here.")

    @patch('src.JobTracker.config', mock_config)
    def test_related_to_application(self):
        text = "This is about a job application."
        self.assertTrue(self.email_message.related_to_application(text))
        text = "This is a general message."
        self.assertFalse(self.email_message.related_to_application(text))

if __name__ == '__main__':
    unittest.main()
