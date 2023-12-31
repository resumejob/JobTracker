import re
import email.utils
import mailbox
import requests
from .config import KEYWORD
from email.header import decode_header
from email.utils import parseaddr
from bs4 import BeautifulSoup

class EmailMessage:

    def __init__(self, mbox_path):
        self.mail_lst = mailbox.mbox(mbox_path)
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def cleanup_body(self, text):
        # remove URL and New Lines in mail body
        text = self.url_pattern.sub('', text)
        text = re.sub(r'\r\n', '', text)
        text = re.sub(r'\n', '', text)
        return text

    def related_to_application(self, text):
        # Use KEYWORD list to fast detect if 
        # mail is related to joy application
        words = set(re.findall(r'\b\w+\b', text))
        return bool(KEYWORD & words)

    def get_mail_body(self, mail):
        body = []
        if mail.is_multipart():
            # TODO: mail multipart maybe recursive
            for part in mail.walk():
                body.append(self.get_text(part))
        else:
            body.append(self.get_text(mail))
        return ''.join(body)

    def get_text(self, mail):
        text = ''
        content_type = mail.get_content_type()
        if content_type == 'text/plain':
            text = self.cleanup_body(mail.get_payload(decode=True).decode(errors='ignore'))
        elif content_type == 'text/html':
            html_text = mail.get_payload(decode=True).decode(errors='ignore')
            soup = BeautifulSoup(html_text, 'html.parser')
            text = self.cleanup_body(soup.get_text())
        return text

    def get_mail_info(self):
        res = []
        # Loop over every mail and get info
        for mail in self.mail_lst:
            info = dict()
            subject = decode_header(mail['subject'])
            subject = ''.join(part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
                              for part, charset in subject)
            sender_name, sender_mail = email.utils.parseaddr(mail['from'])
            recipient_name, recipient_mail = email.utils.parseaddr(mail['to'])
            date = mail['date']
            body = self.get_mail_body(mail)
            if self.related_to_application(body + subject):
                info['subject'] = subject
                info['sender_name'] = sender_name
                info['sender_mail'] = sender_mail
                info['recipient_name'] = recipient_name
                info['recipient_mail'] = recipient_mail
                info['date'] = date
                info['body'] = body
                info['length'] = len(body)
                res.append(info)
        return res
