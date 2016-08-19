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

from mplcheck.checkers import code_structure
from mplcheck.checkers import yaql_checker
from mplcheck import error
from mplcheck.validators import base


SUPPORTED_FORMATS = frozenset(['1.0', '1.1', '1.2', '1.3', '1.4'])


class MuranoPLValidator(base.YamlValidator):
    def __init__(self, loaded_package):
        super(MuranoPLValidator, self).__init__(loaded_package,
                                                'Classes/.*\.yaml$')
        self.yaql_checker = yaql_checker.YaqlChecker()
        self.code_structure = code_structure.CheckCodeStructure()

        self.add_checker(self._valid_name, 'Name', False)
        self.add_checker(self._valid_extends, 'Extends', False)
        self.add_checker(self._valid_methods, 'Methods', False)
        self.add_checker(self._valid_namespaces, 'Namespaces', False)
        self.add_checker(self._valid_properties, 'Properties', False)

    def _valid_name(self, value):
        if value.startswith('__') or \
           not re.match('[a-zA-Z_][a-zA-Z0-9_]*', value):
            yield error.report.E011('Invalid class name "{0}"'.format(value),
                                    value)
        if not (value != value.lower() and value != value.upper()):
            yield error.report.W011('Invalid class name "{0}"'.format(value),
                                    value)

    def _valid_extends(self, value):
        if isinstance(value, list):
            for cls in value:
                if not isinstance(cls, six.string_types):
                    yield error.report.E024("Wrong Extended Class type", value)
        elif not isinstance(value, six.string_types):
            yield error.report.E024("Wrong Extended Class type", value)

    def _valid_contract(self, contract):
        if isinstance(contract, list):
            if len(contract) > 1:
                yield error.report.E042('Too many items in contract list',
                                        contract)
            elif len(contract) == 1:
                contract = contract[0]
                if not self.yaql_checker(contract):
                    yield error.report.E048('Contract is not valid '
                                            'yaql "{0}"'
                                            .format(contract),
                                            contract)
        elif isinstance(contract, dict):
            for c_key, c_value in six.iteritems(contract):
                yield self._valid_contract(c_value)
        elif isinstance(contract, six.string_types):
            if not self.yaql_checker(contract):
                yield error.report.E048('Contract is not valid '
                                        'yaql "{0}"'
                                        .format(contract),
                                        contract)
        else:
            yield error.report.E048('Contract is not valid '
                                    'yaql "{0}"'
                                    .format(contract),
                                    contract)

    def _valid_properties(self, value):
        usage_allowed = frozenset(['In', 'Out', 'InOut', 'Const', 'Static',
                                  'Runtime'])
        for property_, values in six.iteritems(value):
            usage = values.get('Usage')
            if usage:
                if usage not in usage_allowed:
                    yield error.report.E042('Not allowed usage '
                                            '"{0}"'.format(usage),
                                            usage)
            contract = values.get('Contract')
            if contract:
                yield self._valid_contract(contract)
            else:
                yield error.report.E047('Missing Contract in property "{0}"'
                                        .format(property_), property_)

    def _valid_namespaces(self, value):
        if not isinstance(value, dict):
            yield error.report.E044('Wrong type of namespace', value)

    def _valid_methods(self, value):
        for method_name, method_data in six.iteritems(value):
            if not isinstance(method_data, dict):
                yield error.report.E046('Method is not a dict',
                                        method_name)
                return
            scope = method_data.get('Scope')
            if scope is not None and scope not in ('Public', 'Session'):
                yield error.report.E044('Wrong Scope "{0}"'.format(scope),
                                        method_data)
            body = method_data.get('Body')
            if not isinstance(body, (list, six.string_types, dict)):
                yield error.report.E045('Body is not a list or scalar/yaql '
                                        'expression', body)
            else:
                yield self.code_structure.codeblock(body)
