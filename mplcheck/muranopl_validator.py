from mplcheck.base_validator import BaseValidator, Report

class MuranoPLValidator(BaseValidator):
    def __init__(self):
        super(MuranoPLValidator, self).__init__()
        self.add_validator('Extends', self._valid_string)
        self.add_validator('Name', self._valid_string)
        self.add_validator('Properties', self._valid_properties)
        self.add_validator('Namespaces', self._valid_namespaces)
        self.add_validator('Methods', self._valid_methods)

    def _valid_properties(self, name, value):
        pass

    def _valid_namespaces(self, name, value):
        pass

    def _valid_methods(self, name, value):
        pass
