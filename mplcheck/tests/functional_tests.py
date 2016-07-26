from mock import patch
import yaml
import unittest

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
        self._gaf_patcher= patch('mplcheck.manifest_validator.get_all_files')
        self.gaf = self._gaf_patcher.start()
        self.gaf.return_value = ['Instance.yaml']

    def test_classes_namespaces(self):
        mpl_validator = MuranoPLValidator()
        manifest_validator = ManifestValidator('example')
        checker = NamespaceChecker()
        manifest_validator.add_validator('Classes', checker.valid_classes)
        mpl_validator.add_validator('Namespaces', checker.valid_namespace)
        mpl_validator.add_validator('Name', checker.valid_classname)

        manifest_validator.parse(yaml.dump(MANIFEST_DICT))
        manifest_result = [r for r in manifest_validator.validate()]
        mpl_validator.parse(yaml.dump(MURANOPL_BASE))
        mpl_result = [r for r in mpl_validator.validate()]

        self.assertEqual(0, len(manifest_result))
        self.assertEqual(1, len(mpl_result))

        self.assertIn('Namespace of class Name in org.openstack.test.Instance '
                      'doesn\'t match namespace provided in Manifest',
                      mpl_result[0].msg)

if __name__ == '__main__':
    unittest.main()
