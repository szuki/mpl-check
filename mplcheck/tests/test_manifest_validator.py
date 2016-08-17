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

from mplcheck.tests import test_validator_helpers as helpers
from mplcheck.validators import manifest


class ManfiestValidatorTests(helpers.BaseValidatorTestClass):
    def setUp(self):
        super(ManfiestValidatorTests, self).setUp()
        self._oe_patcher = mock.patch('os.path.exists')
        self.exists = self._oe_patcher.start()
        self.exists.return_value = [True, True]
        self.loaded_package = mock.Mock()
        self.mv = manifest.ManifestValidator(self.loaded_package)

    def test_format_as_number(self):
        self.g = self.mv._valid_format(1.3)

    def test_wrong_format(self):
        self.g = self.mv._valid_format('0.9')
        self.assertIn('Not supported format version "0.9"',
                      next(self.g).message)

    def test_format(self):
        self.g = self.mv._valid_format('MuranoPL/1.0')

    def test_unsupported_format(self):
        self.g = self.mv._valid_format('Heat.HOT')
        self.assertIn('Not supported format version "Heat.HOT"',
                      next(self.g).message)

    def test_wrong_type(self):
        self.g = self.mv._valid_type('Shared Library')
        self.assertIn('Type is invalid "Shared Library"', next(self.g).message)

    def test_wrong_require_type(self):
        self.g = self.mv._valid_require([1, 2, 3])
        self.assertIn('Require is not a dict type', next(self.g).message)

    def test_not_existing_file(self):
        data = {'org.openstack.Flow': 'FlowClassifier.yaml',
                'org.openstack.Instance': 'Instance.yaml'}
        self.loaded_package.search_for.return_value = ['FlowClassifier.yaml']
        self.g = self.mv._valid_classes(data)
        self.assertIn('File is present in Manfiest Instance.yaml, but not in '
                      'filesystem', next(self.g).message)

    def test_extra_file_in_directory(self):
        data = {'org.openstack.Instance': 'Instance.yaml'}
        self.loaded_package.search_for.return_value = ['FlowClassifier.yaml',
                                                       'Instance.yaml']
        self.g = self.mv._valid_classes(data)
        self.assertIn('File is not present in Manfiest, but it is in '
                      'filesystem: FlowClassifier.yaml', next(self.g).message)

    def test_missing_ui_file(self):
        self.loaded_package.exists.return_value = False
        self.g = self.mv._valid_ui('ui.yaml')
        self.assertIn('There is no UI file mention in manifest "ui.yaml"',
                      next(self.g).message)

    def test_missing_logo_file(self):
        self.loaded_package.exists.return_value = False
        self.g = self.mv._valid_logo('logo.png')
        self.assertIn('There is no Logo file mention in manifest "logo.png"',
                      next(self.g).message)

    def test_wrong_logo_type(self):
        self.g = self.mv._valid_logo([1, 2, 3])
        self.assertIn('Logo is not a filename', next(self.g).message)

    def test_wrong_ui_type(self):
        self.g = self.mv._valid_ui([1, 2, 3])
        self.assertIn('UI is not a filename', next(self.g).message)
