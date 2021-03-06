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

from mplcheck.tests import test_validator_helpers as helpers
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
        'foo': {
            'Scope': 'Public',
            'Arguments':[{
                'arg1': {'Contract': '$.string()',
                         'Usage': 'Standard'}}],
            'Body': [
                {'Do': [
                    '$port.deploy()',
                    {'$template': {
                        'resources': {
                            '$.name': {
                                'properties': {
                                    'networks': [
                                        {'port': '$port.getRef()'}]}}}}},
                    {'$arg1':
                        '$arg1.mergeWith($template)'}],
                 'For': 'port',
                 'In': '$.ports'},
                {'$sth': 'new(res:Neutron)'},
                {'Return': '$arg1'}]}},
}


class MuranoPlTests(helpers.BaseValidatorTestClass):
    def setUp(self):
        super(MuranoPlTests, self).setUp()
        self.loaded_package = mock.Mock()
        self.loaded_package.format = '1.4'
        self.mpl_validator = MuranoPLValidator(self.loaded_package)

    def test_double_underscored_name(self):
        self.g = self.mpl_validator._valid_name('__Instance')
        self.assertIn('Invalid class name "__Instance"', next(self.g).message)

    def test_not_camel_case_name(self):
        self.g = self.mpl_validator._valid_name('notcamelcase')
        self.assertIn('Invalid class name "notcamelcase"',
                      next(self.g).message)

    def test_whitespace_in_name(self):
        name = 'white space'
        self.g = self.mpl_validator._valid_name(name)
        self.assertIn('Invalid class name "white space"',
                      next(self.g).message)

    def test_properties_usage(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Usage'] = 'OutIn'
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Not allowed usage "OutIn"',
                      next(self.g).message)

    def test_wrong_type_namespace(self):
        self.g = self.mpl_validator._valid_namespaces([1, 2, 3])
        self.assertIn('Wrong type of namespace',
                      next(self.g).message)

    def test_wrong_method_scope(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Scope'] = 'Wrong'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Wrong Scope "Wrong"',
                      next(self.g).message)

    def test_dict_in_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'] = {'$a': 'b'}
        self.g = self.mpl_validator._valid_methods(m_dict)

    def test_error_in_method_scalar_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'] = '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_method_body_is_return(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'] = {'Return': '3'}
        self.g = self.mpl_validator._valid_methods(m_dict)

    def test_error_in_method_for_loop_in(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'][0]['In'] =\
            '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_error_in_method_for_loop_in(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'][0]['In'] =\
            '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_error_in_method_for_loop_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'][0]['Do'][1] =\
            '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_missing_contract_in_properties(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        del p_dict['ports']['Contract']
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Missing Contract in property "ports"',
                      next(self.g).message)

    def test_contract_is_not_yaql(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = '$.deploy('
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Contract is not valid yaql "$.deploy("',
                      next(self.g).message)

    def test_contract_is_a_dict(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = {
            'instance': '$.string()',
            'ports': ['$.ports()']
        }
        self.g = self.mpl_validator._valid_properties(p_dict)

    def test_contract_is_a_dict_with_two_levels(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = {
            'instance': '$.string()',
            'ports': {'a': '$.ports()', 'b': {'c': [], 'd': '$.string()'}}
        }
        self.g = self.mpl_validator._valid_properties(p_dict)

    def test_contract_is_a_dict_with_list(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = {
            'instance': [],
            'ports': {}
        }
        self.g = self.mpl_validator._valid_properties(p_dict)

    def test_contract_two_items_list(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = ['$.string()', '$.string()']
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Too many items in contract list',
                      next(self.g).message)

    def test_contract_is_a_number(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = 1
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Contract is not valid yaql "1"',
                      next(self.g).message)

    def test_contract_a_list_with_invalid_yaql(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Contract'] = ['$.string(']
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Contract is not valid yaql "$.string("',
                      next(self.g).message)

    def test_extends_is_not_a_valid_list(self):
        p_dict = deepcopy(MURANOPL_BASE['Extends'])
        p_dict = ['abc:def', 1]
        self.g = self.mpl_validator._valid_extends(p_dict)
        self.assertIn('Wrong Extended Class',
                      next(self.g).message)

    def test_extends_is_not_valid(self):
        p_dict = deepcopy(MURANOPL_BASE['Extends'])
        p_dict = 4
        self.g = self.mpl_validator._valid_extends(p_dict)
        self.assertIn('Wrong Extended Class',
                      next(self.g).message)

    def test_body_number(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Body'] = 1
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Body is not a list or scalar/yaql expression',
                      next(self.g).message)

    def test_method_is_a_list(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo'] = []
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Method is not a dict',
                      next(self.g).message)

    def test_method_scope_in_1_2(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        del m_dict['foo']['Arguments'][0]['arg1']['Usage']
        self.loaded_package.format = '1.2'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Scope is not supported version earlier than 1.3',
                      next(self.g).message)

    def test_method_usage_action_in_1_4(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Usage'] = 'Action'
        self.loaded_package.format = '1.4'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Usage "Action" is deprecated since 1.4',
                      next(self.g).message)

    def test_method_usage_action(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Usage'] = 'Action'
        self.loaded_package.format = '1.4'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Usage "Action" is deprecated since 1.4',
                      next(self.g).message)

    def test_method_wrong_usage_action(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['foo']['Usage'] = 'Runtimed'
        self.loaded_package.format = '1.4'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Unsupported usage type "Runtimed"',
                      next(self.g).message)

    def test_method_wrong_usage_static_in_1_3(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        del m_dict['foo']['Scope']
        del m_dict['foo']['Arguments'][0]['arg1']['Usage']
        m_dict['foo']['Usage'] = 'Static'
        self.loaded_package.format = '1.3'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Usage "Static" is available from 1.3',
                      next(self.g).message)

    def test_method_arguments_are_dict(self):
        self.g = self.mpl_validator._valid_arguments({'a':'b'})
        self.assertIn('Methods arguments should be a list',
                      next(self.g).message)

    def test_method_arguments_element_is_two_key(self):
        arguments = [
            {'a':{'Contract': '$.string()'},
             'b':{'Contract': '$.string()'}}]
        self.g = self.mpl_validator._valid_arguments(arguments)
        self.assertIn('Methods single argument should be a one key dict',
                      next(self.g).message)

    def test_method_arguments_usage_1_3(self):
        self.loaded_package.format = '1.3'
        self.g = self.mpl_validator._valid_argument_usage('Standard')
        self.assertIn('Arguments usage is available since 1.4',
                      next(self.g).message)

    def test_wrong_method_arguments_usage(self):
        self.g = self.mpl_validator._valid_argument_usage('Standard1')
        self.assertIn('Usage is invalid value "Standard1"',
                      next(self.g).message)
