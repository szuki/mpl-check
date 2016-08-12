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

from mplcheck.checkers import yaql_checker
from mplcheck import error
from mplcheck.validators import base


SUPPORTED_FORMATS = frozenset(['1.0', '1.1', '1.2', '1.3', '1.4'])


class MuranoPLValidator(base.YamlValidator):
    def __init__(self, loaded_package):
        super(MuranoPLValidator, self).__init__(loaded_package)
        self.yaql_checker = yaql_checker.YaqlChecker()

    def _valid_format(self, value):
        if value not in SUPPORTED_FORMATS:
            yield error.report.E001('Not Suported format of yaml "{0}"'
                                    .format(value))

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
                if not self.check_extended_class(cls):
                    yield error.report.E023('Wrong Extended Class', cls)
        elif isinstance(value, six.string_types):
            if not self.check_extended_class(value):
                yield error.report.E023('Wrong Extended Class', cls)
        else:
            yield error.report.E024("Wrong Extended Class type", value)

    def check_extended_class(self, cls):
        if isinstance(cls, six.string_types):
            if ':' not in cls:
                # This means we can check if class is defined in this
                # resources
                pass
            return True
        return False

    def _valid_properties(self, value):
        usage_allowed = frozenset(['In', 'Out', 'InOut', 'Const', 'Static',
                                  'Runtime'])
        for property_, values in six.iteritems(value):
            if not self.check_property_name(property_):
                yield error.report.E041('Wrong property name', property_)
            usage = values.get('Usage')
            if usage:
                if usage not in usage_allowed:
                    yield error.report.E042('Not allowed usage '
                                            '"{0}"'.format(usage),
                                            usage)
            contract = values.get('Contract')
            if contract:
                if not self.yaql_checker(contract):
                    yield error.report.E048('Contract is not valid yaql "{0}"'
                                            .format(contract), contract)
            else:
                yield error.report.E047('Missing Contract in property "{0}"'
                                        .format(property_), property_)
            default = values.get('Default')
            if default:
                if not isinstance(default, (float, int)):
                    if isinstance(default, six.string_types) and\
                            not self.yaql_checker(default):
                        # Note: yaql_checker will fail if string will have
                        # spaces
                        yield error.report.E043('Wrong type of default',
                                                default)

    def check_property_name(self, property_):
        return True

    def _valid_namespaces(self, value):
        if not isinstance(value, dict):
            yield error.report.E044('Wrong type of namespace', value)

    def _valid_methods(self, value):
        for method_name, method_data in six.iteritems(value):
            scope = method_data.get('Scope')
            if scope is not None and scope not in ('Public', 'Session'):
                yield error.report.E044('Wrong Scope "{0}"'.format(scope),
                                        method_data)
            body = method_data.get('Body')
            if not isinstance(body, (list, six.string_types)):
                yield error.report.E045('Body is not a list or scalar/yaql '
                                        'expression', body)
            else:
                for r in self._valid_method_body(body):
                    yield r

    def _valid_method_body(self, expr):
        if isinstance(expr, dict):
            for v in six.itervalues(expr):
                for r in self._valid_method_body(v):
                    yield r
        elif isinstance(expr, list):
            for v in expr:
                for r in self._valid_method_body(v):
                    yield r
        elif isinstance(expr, six.string_types):
            if not self.yaql_checker(expr):
                yield error.report.E046('Error in expression "{0}"'
                                        .format(expr), expr)
