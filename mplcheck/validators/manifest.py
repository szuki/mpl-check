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
        BASE_CHECKERS = {
            'Format': self._valid_format,
            'Classes': self._valid_classes,
            'Author': self._valid_string,
            'FullName': self._valid_string,
            'Name': self._valid_string,
            'Tags': self._valid_tags,
            'Require': self._valid_require,
            'Type': self._valid_type,
            'Description': self._valid_string,
        }
        for key, checker in six.iteritems(BASE_CHECKERS):
            # Let's assume for now that all are required
            self.add_checker(checker, key, required=True)

    def _valid_format(self, name, value):
        if value not in ['1.0', '1.1', '1.2', '1.3']:
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
