API_KEY = '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'
MODEL = 'gpt-4-1106-preview'
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
