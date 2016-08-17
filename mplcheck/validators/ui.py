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

import six

from mplcheck import error
from mplcheck.validators import base

FIELDS_TYPE = frozenset(['string', 'boolean', 'text', 'integer', 'password',
                         'clusterip', 'floatingip', 'domain', 'databaselist',
                         'table', 'flavor', 'keypair', 'image', 'azone',
                         'psqlDatabase'])


class UiValidator(base.YamlValidator):
    def __init__(self, loaded_package):
        super(UiValidator, self).__init__(loaded_package, 'UI/.*\.yaml$')
        self.add_checker(self._validate_templates, 'Templates', False)
        self.add_checker(self._validate_forms, 'Forms', False)
        self.add_checker(self._validate_application, 'Application', False)
        self.add_checker(self._validate_application, 'Version', False)

    def _validate_templates(self, value):
        pass

    def _validate_forms(self, forms):
        for named_form in forms:
            for name, form in six.iteritems(named_form):
                yield self._valid_form(form['fields'])

    def _valid_form(self, form):
        for named_params in form:
            for key, value in six.iteritems(named_params):
                if key == 'type':
                    if value not in FIELDS_TYPE:
                        yield error.report.E80('Wrong type of field "{0}"'
                                               .format(value), value)
                elif key == 'required':
                    if not isinstance(value, bool):
                        yield error.report.E81('Value of {0} should be '
                                               'boolean "{1}"'
                                               .format(key, value), value)
                elif key == 'hidden':
                    if not isinstance(value, bool):
                        yield error.report.E81('Value of {0} should be '
                                               'boolean "{1}"'
                                               .format(key, value), value)
                else:
                    yield self._valid_string(value)

    def _validate_application(self, value):
        pass
