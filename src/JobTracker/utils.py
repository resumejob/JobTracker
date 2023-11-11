import re
import csv
import logging
import email.utils
import mailbox
import hashlib
import requests
from .config import KEYWORD
from email.header import decode_header
from email.utils import parseaddr
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class EmailMessage:

    def __init__(self, mbox_path, old_csv_mails):
        self.mail_lst = mailbox.mbox(mbox_path)
        self.old_mail_list = self.get_old_csv_hash_list(old_csv_mails)
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
            date = mail['date']
            sender_name, sender_mail = email.utils.parseaddr(mail['from'])
            if self.get_hash(sender_mail+date) not in self.old_mail_list:
                subject = decode_header(mail['subject'])
                subject = ''.join(part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
                                for part, charset in subject)
                recipient_name, recipient_mail = email.utils.parseaddr(mail['to'])
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
    
    def get_old_csv_hash_list(self, mails):
        old_pools = set()
        for mail in mails:
            concatenated_key = mail['sender_mail'] + mail['date']
            old_pools.add(self.get_hash(concatenated_key))
        return old_pools
    
    def get_hash(self, key):
        return hashlib.sha256(key.encode()).hexdigest()


    
