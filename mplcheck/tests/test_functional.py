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


from mock import patch
import unittest
import yaml

from mplcheck.checkers import NamespaceChecker
from mplcheck.manifest_validator import ManifestValidator
from mplcheck.muranopl_validator import MuranoPLValidator
from mplcheck.tests.muranopl_validator_tests import MURANOPL_BASE


MANIFEST_DICT = {
    'Author': 'Mirantis, Inc',
    'Classes': {'org.openstack.test2.Instance': 'Instance.yaml'},
    'Description': 'Integration with world.\n',
    'Format': '1.3',
    'FullName': 'org.openstack',
    'Name': 'Murano Test plugin',
    'Require': {'murano-test-plugin': None},
    'Tags': ['Openstack', 'Test'],
    'Type': 'Library'}


class NamespacesTest(unittest.TestCase):
    def setUp(self):
        self._gaf_patcher = patch('mplcheck.manifest_validator.get_all_files')
        self.gaf = self._gaf_patcher.start()
        self.gaf.return_value = ['Instance.yaml']

    def test_classes_namespaces(self):
        mpl_validator = MuranoPLValidator()
        manifest_validator = ManifestValidator('example')
        checker = NamespaceChecker()
        manifest_validator.add_validator('Classes', checker.valid_classes)
        mpl_validator.add_validator('_AST_', checker.valid_mpl)

        manifest_validator.parse(yaml.dump(MANIFEST_DICT))
        manifest_result = [r for r in manifest_validator.validate()]
        mpl_validator.parse(yaml.dump(MURANOPL_BASE))
        mpl_result = [r for r in mpl_validator.validate()]

        self.assertEqual(0, len(manifest_result))
        self.assertEqual(1, len(mpl_result))

        self.assertIn('Namespace of class Instance in '
                      'org.openstack.test.Instance doesn\'t match namespace '
                      'provided in Manifest',
                      mpl_result[0].msg)
