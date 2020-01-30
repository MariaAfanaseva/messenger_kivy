class IncorrectDataNotDictError(Exception):
    """Create error wen data not dict"""
    def __str__(self):
        return 'Data must be a dictionary'


class FieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Missing a required field {self.missing_field}'


class IncorrectCodeError(Exception):
    """Create error wen invalid code in message"""
    def __init__(self, wrong_code):
        self.wrong_code = wrong_code

    def __str__(self):
        return f'Invalid code in message - {self.wrong_code}'


class ServerError(Exception):
    """Create error server with text"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
