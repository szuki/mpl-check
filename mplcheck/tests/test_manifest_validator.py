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

from mplcheck.validators import manifest


class ManfiestValidatorTests(unittest.TestCase):
    def setUp(self):
        self._oe_patcher = mock.patch('os.path.exists')
        self.exists = self._oe_patcher.start()
        self.exists.return_value = [True, True]
        self.mv = manifest.ManifestValidator()

    def test_wrong_format(self):
        all_ = [v for v in self.mv._valid_format('0.9')]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Not supported format version "0.9"',
                      report.message)

    def test_wrong_type(self):
        all_ = [w for w in self.mv._valid_type('Shared Library')]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Type is invalid "Shared Library"', report.message)

    def test_wrong_require_type(self):
        all_ = [w for w in self.mv._valid_require([1, 2, 3])]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Require is not a dict type', report.message)


class ClassesCheckerTest(unittest.TestCase):
    def setUp(self):
        self.loader = mock.Mock()
        self.checker = manifest.ClassesChecker(self.loader)

    def test_not_existing_file(self):
        data = {'org.openstack.Flow': 'FlowClassifier.yaml',
                'org.openstack.Instance': 'Instance.yaml'}
        self.loader.list.return_value = ['FlowClassifier.yaml']
        all_ = [w for w in self.checker._valid_classes(data)]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('File is present in Manfiest Instance.yaml, but not in '
                      'filesystem', report.message)

    def test_extra_file_in_directory(self):
        data = {'org.openstack.Instance': 'Instance.yaml'}
        self.loader.list.return_value = ['FlowClassifier.yaml',
                                         'Instance.yaml']
        all_ = [w for w in self.checker._valid_classes(data)]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('File is not present in Manfiest, but it is in '
                      'filesystem: FlowClassifier.yaml', report.message)


class LogoUICheckerTest(unittest.TestCase):
    def setUp(self):
        self.loader = mock.Mock()
        self.checker = manifest.LogoUIChecker(self.loader)

    def test_missing_ui_file(self):
        self.loader.exists.return_value = False
        all_ = [w for w in self.checker._valid_ui('ui.yaml')]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('There is no UI file mention in manifest "ui.yaml"',
                      report.message)

    def test_missing_logo_file(self):
        self.loader.exists.return_value = False
        all_ = [w for w in self.checker._valid_logo('logo.png')]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('There is no Logo file mention in manifest "logo.png"',
                      report.message)

    def test_wrong_logo_type(self):
        all_ = [w for w in self.checker._valid_logo([1, 2, 3])]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Logo is not a filename', report.message)

    def test_wrong_ui_type(self):
        all_ = [w for w in self.checker._valid_ui([1, 2, 3])]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('UI is not a filename', report.message)
