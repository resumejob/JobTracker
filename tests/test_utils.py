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
        self.mbox_old_path = ''
        self.email_message = EmailMessage(self.mbox_path, self.mbox_old_path)

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
