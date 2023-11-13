# JobTracker

JobTracker that relies on email to trace application status and next step.

## Getting Started

### Prerequisites

- Python 3.10
- An OpenAI API key for ChatGPT access

### Installation

1. Clone the repository and install the required dependencies:

   ```bash
   git clone https://github.com/resumejob/JobTracker.git
   cd JobTracker
   # It is recommended to create a virtual environment for this project before install
   pip install -r requirements.txt

2. Configure your OpenAI API key:
    - create `.env` file under `./src/JobTracker/`
    - fill `API_KEY = 'your_api_key'`

## Usage

Export your emails in MBOX format and run the script with the following command:

    python3 main.py -p path_to_your_email_file.mbox -o output_filename.csv

Replace `path_to_your_email_file.mbox` with the path to your MBOX file and `output_filename.csv` with your desired output file name.

## How It Works

1. Access Data
    - Users export their emails in MBOX format from their email service provider.

2. Clean Up and Collect Data
    - The system extracts basic information such as the sender, recipient, and body of the message.
    - It uses predefined keywords from `config.KEYWORD` to determine if an email is related to a job application.
    - If an email is related, the system collects the relevant information and forwards it to the ChatBot for analysis.

3. Understand and Format Data
    - The ChatBot assesses whether the email pertains to a job application.
    - For job-related emails, it identifies the current status of the application and suggests subsequent steps.
    - A function call is utilized to neatly format the data.

4. Export Data
    - The processed data is exported in CSV or Excel format for easy access and use by the job seeker.

## Run Tests

Execute the following command to run tests:

    python3 -m unittest discover -s tests

Roadmap

- [ ] Support Local LLMs like Llama



## Contributing
We welcome contributions from the community. If you would like to contribute, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

### Contact
For any queries, you can reach out to Project Maintainer.
