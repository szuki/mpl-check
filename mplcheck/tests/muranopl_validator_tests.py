from copy import deepcopy
from mplcheck.muranopl_validator import MuranoPLValidator
import unittest
import yaml


MURANOPL_BASE = {
    'Extends': 'res:LinuxMuranoInstance',
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
    'Name': 'Instance',
    'Namespaces': {
         '=': 'org.openstack.networkingSfc',
         'res': 'io.murano.resources',
         'std': 'io.murano'},
    'Properties': {
        'ports': {
            'Contract': [
                '$.class(NeutronPort).notNull()'],
            'Default': []}}}


class MuranoPlTests(unittest.TestCase):
    def setUp(self):
        self.mpl_validator = MuranoPLValidator()

    def test_success(self):
        mpl = yaml.dump(MURANOPL_BASE)
        self.mpl_validator.parse(mpl)
        result = self.mpl_validator.validate()
        print result
        self.assertEqual(0, len(result))

if __name__ == '__main__':
    unittest.main()
