import argparse
import logging
import csv
import json
from datetime import datetime
from src.JobTracker.utils import EmailMessage
from src.JobTracker.chatbot import ChatGPT

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def process_email(email_path, old_csv_path):
    '''
    Process the emails at the given path and return the results.

    :param email_path: Path to the email file or directory
    :return: List of processed email data
    '''
    em = EmailMessage(email_path, read_csv(old_csv_path))
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
    company = {}
    for mail in mail_info:
        state, data = chatbot.get_content(mail)
        if state == 'Succeed':
            if data['company'] not in company:
                company[data['company']] = len(res)
                res.append(data)
            else:
                state1 = res[company[data['company']]]['state']
                state1_dict = json.loads(state1)
                state2_dict = json.loads(mail['state'])
                state1_dict.update(state2_dict)
                date_objects = {key: datetime.strptime(value, '%b %d %Y') for key, value in state1_dict.items()}
                sorted_date = dict(sorted(date_objects.items(), key=lambda item: item[1]))
                sorted_date_dict = {key: date.strftime('%b %d %Y') for key, date in sorted_date.items()}
                res[company[data['company']]]['state'] = json.dumps(sorted_date_dict)
                if list(state2_dict.items()) == list(sorted_date_dict.items())[-1]:
                    res[company[data['company']]]['next_step'] = mail['next_step']
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


def main(email_path, output_csv, old_csv):
    result = process_email(email_path, old_csv)
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
