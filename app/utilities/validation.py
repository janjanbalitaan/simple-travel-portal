import re
from datetime import datetime

class ValidationUtilities:
    def is_valid_email(string):
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

        if re.search(regex, string):
            return True
        else:
            return False

    def is_valid_bearer(auth):
        if len(auth) != 2:
            return False

        if auth[0] != 'Bearer':
            return False

        if auth[1] == '' or auth[1] is None:
            return False
        
        return True

    def is_valid_datetime_string(string):
        try:
            datetime.strptime(string, '%Y-%m-%d')
            return True
        except:
            return False

