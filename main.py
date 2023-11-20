import argparse
import logging
import csv
import json
import ast
from datetime import datetime
from collections import defaultdict
from src.JobTracker.utils import EmailMessage
from src.JobTracker.chatbot import ChatGPT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_email(email_path, old_csv_path):
    '''
    Process the emails at the given path and return the results.

    :param email_path: Path to the email file or directory
    :return: List of processed email data
    '''

    old_file = read_csv(old_csv_path) if old_csv_path else None
    em = EmailMessage(email_path, old_file)
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
       
    companys = buildOldCompany(old_file) if old_file else defaultdict(list)
    key = ['subject', 'sender_name', 'sender_mail', 'recipient_name', 'recipient_mail', 'date', 'body', 'length', 'company', 'state', 'next_step', 'rank']
    for mail in mail_info:
        state, data = chatbot.get_content(mail)
        if state == 'Succeed':  
            content = list(data.values())
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
            writer.writerow(row)

def read_csv(filename):
    if not filename:
        return []
    data = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    except FileNotFoundError as e:
        logging.warning(f"File not found or path incorrect: {e}")
        return []
    except Exception as e:
        logging.warning(f"Error reading the file: {e}")
        return []
    return data

def buildOldCompany(old_companys):
    companys = defaultdict(list)
    for company in old_companys:
        data = list(company.values())
        formatData = [ast.literal_eval(element) for element in data]
        datetime = [convertDate(value) for value in formatData[5]]
        name = formatData[8][0]
        formatData.append(datetime)
        res = [list(column) for column in zip(*formatData)]
        companys[name] += res
    return companys

def convertDate(date):
    try:
        date_object = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
        return date_object
    except ValueError:
        try:
            date_object = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z (%Z)")
            return date_object
        except ValueError:
            logging.warn("not able to parse date")
            return datetime.max



def main(email_path, output_csv, old_csv_path):
    result = process_email(email_path, old_csv_path)
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
    parser.add_argument("-d", '--old',
                        type=str,
                        help='The old CSV file to avoid duplicate',
                        default=None,
                        required=False)
    args = parser.parse_args()
    main(args.path, args.output, args.old)
