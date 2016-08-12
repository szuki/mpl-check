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

import mock
import unittest

from mplcheck.validators import ui


class UiValidatorTest(unittest.TestCase):
    def setUp(self):
        self.package = mock.Mock()
        self.ui_validator = ui.UiValidator(self.package)

    def list(self, generator):
        self.assertIsNot(generator, None,
                         "None reports where returned from validate function")
        return [v for v in generator]

    def one_report(self, generator):
        all_ = self.list(generator)
        self.assertEqual(len(all_), 1)
        return all_[0]

    def test_forms(self):
        forms = [
            {'name1': {
                'fields': [
                    {'n1': {
                        'name': 'whatever',
                        'type': 'integer',
                        'label': 'sth',
                        'description': 'something'
                    }}]}}]
        with self.assertRaises(StopIteration):
            next(self.ui_validator._validate_forms(forms))

    def test_forms_wrong_type(self):
        forms = [
            {'name1': {
                'fields': [
                    {'n1': {
                        'name': 'whatever',
                        'type': 'int',
                        'label': 'sth',
                        'description': 'something'
                    }}]}}]
        report = self.one_report(self.ui_validator._validate_forms(forms))
        self.assertIn('Wrong type of field "int"', report.message)
