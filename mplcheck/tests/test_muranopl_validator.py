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


from mplcheck.muranopl_validator import MuranoPLValidator
import unittest
import yaml


MURANOPL_BASE = {
    'Name': 'Instance',
    'Namespaces': {
        '=': 'org.openstack.test',
        'res': 'io.murano.resources',
        'std': 'io.murano'},
    'Extends': 'res:LinuxMuranoInstance',
    'Properties': {
        'ports': {
            'Contract': [
                '$.class(NeutronPort).notNull()'],
            'Default': []}},
    'Methods': {
        'prepareStackTemplate': {
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
