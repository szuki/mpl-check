#    Copyright (c) 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from mplcheck.base_validator import BaseValidator
from mplcheck.base_validator import Report


class MuranoPLValidator(BaseValidator):
    def __init__(self):
        super(MuranoPLValidator, self).__init__()
        self.add_validator('Name', self._valid_string, False)
        self.add_validator('Name', self._valid_name, False)
        self.add_validator('Namespaces', self._valid_namespaces)
        self.add_validator('Extends', self._valid_extends, False)
        self.add_validator('Properties', self._valid_properties, False)
        self.add_validator('Methods', self._valid_methods, False)

    def _valid_name(self, name, value):
        if value.startswith('__'):
            yield Report.E011(value)
        if not (value != value.lower() and value != value.upper()):
            yield Report.W011(value)

    def _valid_extends(self, name, value):
        pass

    def _valid_properties(self, name, value):
        pass

    def _valid_namespaces(self, name, value):
        pass

    def _valid_methods(self, name, value):
        pass
