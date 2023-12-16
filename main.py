import argparse
import logging
import csv
import os

from src.JobTracker.utils import EmailMessage
from src.JobTracker.config import AUTO_SAVE_EMAIL
from src.JobTracker.chatbot import ChatGPT, Llama

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def process_email(email_path, output_csv, model="chatgpt"):
    '''
    Process the emails at the given path and return the results.

    :param email_path: Path to the email file or directory
    :return: List of processed email data
    '''
    em = EmailMessage(email_path)
    mail_info = em.get_mail_info()
    res = 0
    chatbot = None
    if model == "chatgpt":
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
    elif model == "llama":
        chatbot = Llama()
        
    for mail in mail_info:
        state, data = chatbot.get_content(mail)
        if state == 'Succeed':
            res += 1
            cur.append(data)
            if len(cur) % AUTO_SAVE_EMAIL == 0:
                export_to_csv(cur, output_csv)
                cur = []
    if cur:
        export_to_csv(cur, output_csv)
    return res

def export_to_csv(data, filename):
    file_exists = os.path.exists(filename)
    with open(filename, mode="a", newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames) 
        if not file_exists:  
            writer.writeheader()
        for row in data:
            writer.writerow(row)
    logging.info(f"Processed {str(len(data))} emails and exported to CSV at {filename}.")

    
def main(email_path, output_csv, model):
    result = process_email(email_path, output_csv, model)
    if result > 0:
        logging.info(f"Total {str(result)} emails Processed successfully and exported to CSV at {output_csv}.")
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
    parser.add_argument('-m', '--model',
                        type=str,
                        help='The model to process tasks. chatgpt/llama',
                        choices=["chatgpt", "llama"],
                        required=True)
    args = parser.parse_args()
    main(args.path, args.output, args.model)
