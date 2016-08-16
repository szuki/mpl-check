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

from mplcheck.checkers import namespace
from mplcheck.tests import test_validator_helpers as helpers


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


class NamespacesCheckerTest(helpers.BaseValidatorTestClass):
    def setUp(self):
        super(NamespacesCheckerTest, self).setUp()
        self.checker = namespace.NamespaceChecker()
        self.loader = mock.Mock()
        self.loader.list.return_value = 'Instance.yaml'

    def _test_classes_namespaces(self):
        self.g = self.checker.valid_namespace(self.loader)
        self.assertIn('Namespace of class "Instance" in '
                      '"org.openstack.test.Instance" doesn\'t match namespace '
                      'provided in Manifest',
                      next(self.g).message)
