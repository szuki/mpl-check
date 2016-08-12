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


import os.path
import six

from mplcheck import error
from mplcheck.validators import base


class ManifestValidator(base.YamlValidator):
    def __init__(self, loaded_package):
        super(ManifestValidator, self).__init__(loaded_package)
        self.add_checker(self._valid_format, 'Format', False)
        self.add_checker(self._valid_string, 'Author', False)
        self.add_checker(self._valid_string, 'FullName')
        self.add_checker(self._valid_string, 'Name', False)
        self.add_checker(self._valid_tags, 'Tags', False)
        self.add_checker(self._valid_require, 'Require', False)
        self.add_checker(self._valid_type, 'Type')
        self.add_checker(self._valid_string, 'Description')
        self.add_checker(self._valid_ui, 'UI', False)
        self.add_checker(self._valid_logo, 'Logo', False)

    def _valid_format(self, value):
        if value not in ['1.0', '1.1', '1.2', '1.3', '1.4']:
            yield error.report.E030('Not supported format version "{0}"'
                                    .format(value), value)

    def _valid_tags(self, value):
        if not isinstance(value, list):
            yield error.report.E070('Tags should be a list', value)

    def _valid_require(self, value):
        if not isinstance(value, dict):
            yield error.report.E005('Require is not a dict type', value)

    def _valid_type(self, value):
        if value not in ('Application', 'Library'):
            yield error.report.E071('Type is invalid "{0}"'.format(value),
                                    value)

    def _valid_ui(self, value):
        if isinstance(value, six.string_types):
            if not self._loaded_package.exists(os.path.join('UI', value)):
                yield error.report.E073('There is no UI file mention in '
                                        'manifest "{0}"'.format(value), value)
        else:
            yield error.report.E072('UI is not a filename', value)

    def _valid_logo(self, value):
        if isinstance(value, six.string_types):
            if not self._loaded_package.exists(value):
                yield error.report.E074('There is no Logo file mention in '
                                        'manifest "{0}"'.format(value), value)
        else:
            yield error.report.E074('Logo is not a filename', value)

    def _valid_classes(self, value):
        files = set(value.values())
        existing_files = set(self._loaded_package.list('Classes'))
        for fname in files - existing_files:
            yield error.report.E050('File is present in Manfiest {fname}, '
                                    'but not in filesystem'
                                    .format(fname=fname),
                                    fname)
        for fname in existing_files - files:
            yield error.report.W020('File is not present in Manfiest, but '
                                    'it is in filesystem: {fname}'
                                    .format(fname=fname), fname)
