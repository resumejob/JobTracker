MODEL = 'gpt-4-1106-preview'
PRICE = {
            "gpt-4-1106-preview": (0.01, 0.03),
            "gpt-4-1106-vision-preview": (0.01, 0.03),
            "gpt-4-32k-0314": (0.06, 0.12),
            "gpt-4-0314": (0.03, 0.06),
            "gpt-4-32k-0613": (0.06, 0.12),
            "gpt-4-0613": (0.03, 0.06),
            "gpt-3.5-turbo-16k-0613": (0.0010, 0.0020),
            "gpt-3.5-turbo-0613": (0.0015, 0.0020)
        }
KEYWORD = set(['received', 'confirmation', 'apply', 'application', 'reviewing', 'interview', 'schedule', 'resume', 'evaluating', 'screening', 'assessment', 'hiring', 'onboarding', 'offer', 'salary', 'unfortunately', 'rejection', 'forword', 'feedback', 'interested'])
FUNCTION = [
    {
        'name': 'get_email_info',
        'description': 'return the info from email content with JSON format ',
        'parameters': {
            'type': 'object',
            'properties': {
                'company': {
                    'type': 'string',
                    'description': 'the company name',
                },
                'state': {
                    'type': 'string',
                    'description': 'state of job application, choose one of Applied/Next Round/Offer/Rejected',
                },
                'next_step': {
                    'type': 'string',
                    'description': 'What job seeker need to do next',
                },
            },
            'required': ['company', 'state', 'next_step'],
        },
    }
]
