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

from copy import deepcopy
import mock
import unittest

from mplcheck.validators.muranopl import MuranoPLValidator


MURANOPL_BASE = {
    'Name': 'Instance',
    'Namespaces': {
        '=': 'org.openstack.test',
        'res': 'io.murano.resources',
        'std': 'io.murano'},
    'Extends': 'res:LinuxMuranoInstance',
    'Properties': {
        'ports': {
            'Contract': '$.class(NeutronPort).notNull()',
            'Default': []}},
    'Methods': {
        'prepareStackTemplate': {
            'Scope': 'Public',
            'Arguments': {
                'instanceTemplate': {'Contract': {}}},
            'Body': [
                {'Do': [
                    '$port.deploy()',
                    {'$template': {
                        'resources': {
                            '$.name': {
                                'properties': {
                                    'networks': [
                                        {'port': '$port.getRef()'}]}}}}},
                    {'$instanceTemplate':
                        '$instanceTemplate.mergeWith($template)'}],
                 'For': 'port',
                 'In': '$.ports'},
                {'sth': 'new(res:Neutron)'},
                {'Return': '$instanceTemplate'}]}},
}


class MuranoPlTests(unittest.TestCase):
    def setUp(self):
        self.loaded_package = mock.Mock()
        self.mpl_validator = MuranoPLValidator(self.loaded_package)

    def test_double_underscored_name(self):
        result = [r for r in self.mpl_validator._valid_name('__Instance')]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "__Instance"', report.message)

    def test_not_camel_case_name(self):
        result = [r for r in self.mpl_validator._valid_name('notcamelcase')]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "notcamelcase"',
                      report.message)

    def test_whitespace_in_name(self):
        name = 'white space'
        result = [r for r in self.mpl_validator._valid_name(name)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "white space"',
                      report.message)

    def test_properties_usage(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Usage'] = 'OutIn'
        result = [r for r in self.mpl_validator._valid_properties(p_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Not allowed usage "OutIn"',
                      report.message)

    def test_wrong_type_namespace(self):
        result = [r for r in self.mpl_validator._valid_namespaces([1, 2, 3])]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong type of namespace',
                      report.message)

    def test_wrong_method_scope(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Scope'] = 'Wrong'
        result = [r for r in self.mpl_validator._valid_methods(m_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong Scope "Wrong"',
                      report.message)

    def test_dict_in_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'] = {'a': 'b'}
        result = [r for r in self.mpl_validator._valid_methods(m_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Body is not a list or scalar/yaql expression',
                      report.message)

    def test_wrong_default_expr(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Default'] = '$.deploy('
        result = [r for r in self.mpl_validator._valid_properties(p_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong type of default',
                      report.message)

    def test_error_in_method_scalar_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'] = '$.deploy('
        result = [r for r in self.mpl_validator._valid_methods(m_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)

    def test_error_in_method_for_loop_in(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'][0]['In'] =\
            '$.deploy('
        result = [r for r in self.mpl_validator._valid_methods(m_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)

    def test_error_in_method_for_loop_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'][0]['Do'][1] =\
            '$.deploy('
        result = [r for r in self.mpl_validator._valid_methods(m_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)

    def test_missing_contract_in_properties(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        del p_dict['ports']['Contract']
        result = [r for r in self.mpl_validator._valid_properties(p_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Missing Contract in property "ports"',
                      report.message)

    def test_contract_is_not_yaql(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = '$.deploy('
        result = [r for r in self.mpl_validator._valid_properties(p_dict)]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Contract is not valid yaql "$.deploy("',
                      report.message)
