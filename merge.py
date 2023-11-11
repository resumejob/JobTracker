import argparse

from src.JobTracker.utils import EmailMessage
from main import export_to_csv, read_csv


def main(path1, path2, output_csv):
  data1 = read_csv(path1)
  data2 = read_csv(path2)
  export_to_csv(data1+data2, output_csv)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Process some emails.")
  parser.add_argument('-p1', '--path1',
                      type=str,
                      help='The path first CSV file',
                      required=True)
  parser.add_argument("-p2", '--path2',
                      type=str,
                      help='The path second CSV file',
                      default=None,
                      required=True)
  parser.add_argument('-o', '--output',
                      type=str,
                      help='The output path for the CSV file',
                      default='new_emails.csv',  # Default output filename if not specified
                      required=False)
  args = parser.parse_args()
  main(args.path1, args.path2, args.output)