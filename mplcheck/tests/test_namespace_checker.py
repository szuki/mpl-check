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

from mplcheck import checkers


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
        self.checker = checkers.NamespaceChecker()
        self.loader = mock.Mock()
        self.loader.list.return_value = 'Instance.yaml'

    def _test_classes_namespaces(self):
        cv = [v for v in self.checker.valid_namespace(self.loader)]
        self.assertEqual(len(cv), 1)
        report = cv[0]

        self.assertIn('Namespace of class "Instance" in '
                      '"org.openstack.test.Instance" doesn\'t match namespace '
                      'provided in Manifest',
                      report.message)
