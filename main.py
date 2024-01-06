import argparse
import logging
import csv
import json
import re
from collections import defaultdict
from tqdm import tqdm
from src.JobTracker.utils import EmailMessage
from src.JobTracker.chatbot import ChatGPT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def format_cell(key, item):
    "Join list elements with a newline character, remove square brackets"
    if isinstance(item, list):
        if key in ['company', 'recipient_mail']:
            # merge repeating values to a single value
            if len(set(item)) == 1:
                return str(item[0])

        return '\n'.join(map(str, item))
    return str(item)

def remove_curly_braces(string):
    "Use regular expression to match JSON-like dictionaries"
    pattern = r'\{.*?\}'
    matches = re.findall(pattern, string)

    results = []
    for match in matches:
        try:
            # Convert each matched string to a dictionary
            dict_data = json.loads(match)
            formatted_string = '; '.join([f"{key}: {value}" for key, value in dict_data.items()])
            results.append(formatted_string)
        except json.JSONDecodeError:
            continue

    return '\n'.join(results)

def process_email(email_path):
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
    companys = defaultdict(list)
    key = ['company', 'state', 'next_step', 'subject', 'sender_name', 'sender_mail', 'recipient_name', 'recipient_mail', 'date', 'body', 'length', 'rank']
    for mail in tqdm(range(len(mail_info)), desc="Processing", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"):
        state, data = chatbot.get_content(mail_info[mail])
        if state == 'Succeed':
            content = [data[k] for k in key]
            companys[data['company']].append(content)

    for content in companys.values():
        if len(content) != 0:
            content.sort(key=lambda a: a[-1])
            combined_list = [list(column) for column in zip(*content)]
            data = dict(zip(key[:-1], combined_list[:-1]))
            res.append(data)
    return res

def export_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            # remove square and curly brackets
            # separate each item to a new line in a cell
            formatted_row = {key: format_cell(key, value) for key, value in row.items()}
            formatted_row['state'] = remove_curly_braces(formatted_row['state'])
            writer.writerow(formatted_row)

def main(email_path, output_csv):
    result = process_email(email_path)
    if result:
        export_to_csv(result, output_csv)
        logging.info(f"Processed emails successfully and exported to CSV at {output_csv}.")
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
