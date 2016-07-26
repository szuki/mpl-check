from mplcheck.base_validator import BaseValidator, Report

class MuranoPLValidator(BaseValidator):
    def __init__(self):
        super(MuranoPLValidator, self).__init__()
        self.add_validator('Extends', self._valid_string)


