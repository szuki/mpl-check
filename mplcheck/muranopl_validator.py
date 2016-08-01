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

import re
import six

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
        if value.startswith('__') or \
           not re.match('[a-zA-Z_][a-zA-Z0-9_]*', value):
            yield Report.E011(value)
        if not (value != value.lower() and value != value.upper()):
            yield Report.W011(value)

    def _valid_extends(self, name, value):
        if isinstance(value, list):
            for cls in value:
                if not self.check_extended_class(cls):
                    yield Report.E023(cls)
        elif isinstance(value, six.string_types):
            if not self.check_extended_class(value):
                yield Report.E023(cls)
        else:
            yield Report.E023(value)

    def check_extended_class(self, cls):
        if isinstance(cls, six.string_types):
            if ':' not in cls:
                # This means we can check if class is defined in this
                # resources
                pass
            return True
        return False

    def _valid_properties(self, name, value):
        usage_allowed = frozenset(['In', 'Out', 'InOut', 'Const', 'Static',
                                  'Runtime'])
        for property_, values in six.iteritems(value):
            if not self.check_property_name(property_):
                yield Report.E041(property_)
            usage = values.get('Usage')
            if usage:
                if usage not in usage_allowed:
                    yield Report.E042(usage)
            default = value.get('Default')
            if default:
                if not (isinstance(default, (six.string_types, float, int)) or
                        self.check_yaql(default)):
                    yield Report.E043(default)

    def check_yaql(self, yaql):
        return True

    def check_property_name(self, property_):
        return True

    def _valid_namespaces(self, name, value):
        pass

    def _valid_methods(self, name, value):
        pass
