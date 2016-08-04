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
import unittest
import yaml

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
        self.mpl_validator = MuranoPLValidator()

    def test_success(self):
        mpl = yaml.dump(MURANOPL_BASE)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(0, len(result))

    def test_no_name_in_file(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        del mpl_dict['Name']
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(0, len(result))

    def test_double_underscored_name(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Name'] = '__Instance'
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "__Instance"', report.message)
        self.assertEqual(22, report.line)
        self.assertEqual(7, report.column)

    def test_not_camel_case_name(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Name'] = 'notcamelcase'
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "notcamelcase"',
                      result[0].message)
        self.assertEqual(22, report.line)
        self.assertEqual(7, report.column)

    def test_whitespace_in_name(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Name'] = 'white space'
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Invalid class name "white space"',
                      report.message)
        self.assertEqual(22, report.line)
        self.assertEqual(7, report.column)

    def test_properties_usage(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Properties']['ports']['Usage'] = 'OutIn'
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Not allowed usage "OutIn"',
                      report.message)
        self.assertEqual(28, report.line)
        self.assertEqual(12, report.column)

    def test_wrong_type_namespace(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Namespaces'] = [1, 2, 3]
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong type of namespace',
                      report.message)
        self.assertEqual(23, report.line)
        self.assertEqual(13, report.column)

    def test_wrong_method_scope(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Methods']['prepareStackTemplate']['Scope'] = 'Wrong'
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong Scope "Wrong"',
                      report.message)
        self.assertEqual(4, report.line)
        self.assertEqual(5, report.column)

    def test_dict_in_body(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Methods']['prepareStackTemplate']['Body'] = {'a': 'b'}
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Body is not a list or scalar/yaql expression',
                      report.message)
        self.assertEqual(7, report.line)
        self.assertEqual(11, report.column)

    def test_wrong_default_expr(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Properties']['ports']['Default'] = '$.deploy('
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Wrong type of default',
                      report.message)
        self.assertEqual(25, report.line)
        self.assertEqual(62, report.column)

    def test_error_in_method_scalar_body(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Methods']['prepareStackTemplate']['Body'] = '$.deploy('
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)
        self.assertEqual(7, report.line)
        self.assertEqual(11, report.column)

    def test_error_in_method_for_loop_in(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Methods']['prepareStackTemplate']['Body'][0]['In'] =\
            '$.deploy('
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)
        self.assertEqual(18, report.line)
        self.assertEqual(11, report.column)

    def test_error_in_method_for_loop_body(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Methods']['prepareStackTemplate']['Body'][0]['Do'][1] =\
            '$.deploy('
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Error in expression "$.deploy("',
                      report.message)
        self.assertEqual(10, report.line)
        self.assertEqual(9, report.column)

    def test_missing_contract_in_properties(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        del mpl_dict['Properties']['ports']['Contract']
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Missing Contract in property "ports"',
                      report.message)
        self.assertEqual(25, report.line)
        self.assertEqual(3, report.column)

    def test_contract_is_not_yaql(self):
        mpl_dict = deepcopy(MURANOPL_BASE)
        mpl_dict['Properties']['ports']['Contract'] = '$.deploy('
        mpl = yaml.dump(mpl_dict)
        self.mpl_validator.parse(mpl)
        result = [r for r in self.mpl_validator.validate()]
        self.assertEqual(1, len(result))
        report = result[0]
        self.assertIn('Contract is not valid yaql "$.deploy("',
                      report.message)
        self.assertEqual(26, report.line)
        self.assertEqual(15, report.column)
