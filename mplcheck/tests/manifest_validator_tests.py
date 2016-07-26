from copy import deepcopy
from mock import patch
import unittest
import yaml

from mplcheck.manifest_validator import ManifestValidator


MANIFEST_DICT = {
    'Author': 'Mirantis, Inc',
    'Classes': {'org.openstack.Flow': 'FlowClassifier.yaml',
                'org.openstack.Instance': 'Instance.yaml'},
    'Description': 'Integration with world.\n',
    'Format': '1.3',
    'FullName': 'org.openstack',
    'Name': 'Murano Test plugin',
    'Require': {'murano-test-plugin': None},
    'Tags': ['Openstack', 'Test'],
    'Type': 'Library'}


class TestUnit(unittest.TestCase):
    def setUp(self):
        self._gaf_patcher= patch('mplcheck.manifest_validator.get_all_files')
        self.gaf = self._gaf_patcher.start()
        self.gaf.return_value = ['FlowClassifier.yaml', 'Instance.yaml']

    def test_validate(self):
        mv = ManifestValidator('example/Classes')
        mv.parse(yaml.dump(MANIFEST_DICT))
        all_ = [w for w in mv.validate()]
        if all_:
            raise Exception('There should be not validation errors, but there'
                            ' are: {0}'.format(all_))

    def test_wrong_format(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        md['Format'] = '0.9'
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        self.assertIn('Not supported format version "0.9" at line', all_[0].msg)

    def test_missing_format(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        del md['Format']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        self.assertIn('Missing required key "Format"', all_[0].msg)

    def test_not_existing_file(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        self.gaf.return_value = ['FlowClassifier.yaml']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        self.assertIn('File is present in Manfiest Instance.yaml, but not in filesystem', all_[0].msg)

    def test_extra_file_in_directory(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        del md['Classes']['org.openstack.Flow']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        self.assertIn('File is not present in Manfiest, but it is in filesystem: FlowClassifier.yaml', all_[0].msg)

if __name__ == '__main__':
    unittest.main()