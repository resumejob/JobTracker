import argparse
import logging
import csv

from src.JobTracker.utils import EmailMessage
from src.JobTracker.chatbot import ChatGPT
from src.JobTracker.config import AUTO_SAVE_EMAIL

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_email(email_path, output_csv):
    '''
    Process the emails at the given path and return the results.

    :param email_path: Path to the email file or directory
    :return: List of processed email data
    '''
    em = EmailMessage(email_path)
    mail_info = em.get_mail_info()
    res = []
    chatbot = ChatGPT()
    message = chatbot.get_cost(mail_info)
    logging.info(message)
    while True:
        k = input("Enter Y to Process, N to STOP: ")
        if k.lower() == "y":
            logging.info("---------Keep processing emails---------")
            break
        elif k.lower() == "n":
            logging.info("---------Stop processing emails---------")
            return
    email_counter = 0  
    for mail in mail_info:
        state, data = chatbot.get_content(mail)
        if state == 'Succeed':
            res.append(data)
            email_counter += 1
            if email_counter % AUTO_SAVE_EMAIL == 0:
                export_to_csv(res, output_csv)
                res = []
    return res, email_counter

def export_to_csv(data, filename):
    file_exists = False
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            file_exists = True
    except FileNotFoundError:
        pass
    mode = 'a' if file_exists else 'w'
    with open(filename, mode=mode, newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow(row)

def main(email_path, output_csv):
    result, count = process_email(email_path, output_csv)
    if count > 0:
        export_to_csv(result, output_csv)
        logging.info(f"Processed {str(count)} emails successfully and exported to CSV at {output_csv}.")
    else:
        logging.info("No emails processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some emails.")
    parser.add_argument('-p', '--path',
                        type=str,
                        help='The path to the email file or directory',
                        required=True)
    parser.add_argument('-o', '--output',
                        type=str,
                        help='The output path for the CSV file',
                        default='emails.csv',  # Default output filename if not specified
                        required=False)
    args = parser.parse_args()
    main(args.path, args.output)
