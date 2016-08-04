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


def get_all_files(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            matches.append(os.path.join(root, fname))
    return matches


class ManifestValidator(base.BaseValidator):
    def __init__(self, class_directory):
        super(ManifestValidator, self).__init__()
        self._class_directory = class_directory
        self.add_checker(self._valid_format, 'Format', required=False)
        self.add_checker(self._valid_classes, 'Classes', required=True)
        self.add_checker(self._valid_string, 'Author', required=True)
        self.add_checker(self._valid_string, 'FullName', required=True)
        self.add_checker(self._valid_string, 'Name', required=True)
        self.add_checker(self._valid_tags, 'Tags', required=True)
        self.add_checker(self._valid_require, 'Require', required=True)
        self.add_checker(self._valid_type, 'Type', required=True)
        self.add_checker(self._valid_string, 'Description', required=True)
        self.add_checker(self._valid_ui, 'UI', required=False)
        self.add_checker(self._valid_logo, 'Logo', required=False)

    def _valid_format(self, name, value):
        if value not in ['1.0', '1.1', '1.2', '1.3', '1.4']:
            yield error.report.E030('Not supported format version "{0}"'
                                    .format(value), value)

    def _valid_classes(self, name, value):
        files = set(value.values())
        existing_files = set(get_all_files(self._class_directory))
        for fname in files - existing_files:
            yield error.report.E050('File is present in Manfiest {fname}, '
                                    'but not in filesystem'
                                    .format(fname=fname),
                                    fname)
        for fname in existing_files - files:
            yield error.report.W020('File is not present in Manfiest, but '
                                    'it is in filesystem: {fname}'
                                    .format(fname=fname), fname)

    def _valid_tags(self, name, value):
        if not isinstance(value, list):
            yield error.report.E070('Tags should be a list', value)

    def _valid_require(self, name, value):
        if not isinstance(value, dict):
            yield error.report.E005('Require is not a dict type', value)

    def _valid_type(self, name, value):
        if value not in ('Application', 'Library'):
            yield error.report.E071('Type is invalid "{0}"'.format(value),
                                    value)

    def _valid_ui(self, name, value):
        if isinstance(value, six.string_types):
            if not os.path.exists(os.path.join('UI', value)):
                yield error.report.E073('There is no UI file mention in '
                                        'manifest "{0}"'.format(value), value)
        else:
            yield error.report.E072('UI is not a filename', value)

    def _valid_logo(self, name, value):
        if isinstance(value, six.string_types):
            if not os.path.exists(value):
                yield error.report.E074('There is no Logo file mention in '
                                        'manifest "{0}"'.format(value), value)
        else:
            yield error.report.E074('Logo is not a filename', value)
