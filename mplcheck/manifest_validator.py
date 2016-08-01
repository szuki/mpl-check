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

from mplcheck.base_validator import BaseValidator
from mplcheck.base_validator import Report


def get_all_files(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            matches.append(os.path.join(root, fname))
    return matches


class ManifestValidator(BaseValidator):
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
            yield Report.E030(value)

    def _valid_classes(self, name, value):
        files = set(value.values())
        existing_files = set(get_all_files(self._class_directory))
        for fname in files - existing_files:
            yield Report.E050(name, fname=fname)
        for fname in existing_files - files:
            yield Report.W020(value, fname=fname)

    def _valid_tags(self, name, value):
        if not isinstance(value, list):
            raise Report.E070('Tags should be a list')

    def _valid_require(self, name, value):
        pass

    def _valid_type(self, name, value):
        pass
