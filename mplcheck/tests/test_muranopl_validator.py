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
                {'$sth': 'new(res:Neutron)'},
                {'Return': '$instanceTemplate'}]}},
}


class MuranoPlTests(helpers.BaseValidatorTestClass):
    def setUp(self):
        super(MuranoPlTests, self).setUp()
        self.loaded_package = mock.Mock()
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
        m_dict['prepareStackTemplate']['Scope'] = 'Wrong'
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Wrong Scope "Wrong"',
                      next(self.g).message)

    def test_dict_in_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'] = {'$a': 'b'}
        self.g = self.mpl_validator._valid_methods(m_dict)

    def test_wrong_default_expr(self):
        p_dict = deepcopy(MURANOPL_BASE['Properties'])
        p_dict['ports']['Default'] = '$.deploy('
        self.g = self.mpl_validator._valid_properties(p_dict)
        self.assertIn('Wrong type of default',
                      next(self.g).message)

    def test_error_in_method_scalar_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'] = '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_method_body_is_return(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'] = {'Return': '3'}
        self.g = self.mpl_validator._valid_methods(m_dict)

    def test_error_in_method_for_loop_in(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'][0]['In'] =\
            '$.deploy('
        self.g = self.mpl_validator._valid_methods(m_dict)
        self.assertIn('Not a valid yaql expression "$.deploy("',
                      next(self.g).message)

    def test_error_in_method_for_loop_body(self):
        m_dict = deepcopy(MURANOPL_BASE['Methods'])
        m_dict['prepareStackTemplate']['Body'][0]['Do'][1] =\
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
