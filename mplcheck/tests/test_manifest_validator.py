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
from mock import patch
import unittest
import yaml

from mplcheck.validators.manifest import ManifestValidator


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
        self._gaf_patcher = patch('mplcheck.validators.manifest.get_all_files')
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
        report = all_[0]
        self.assertIn('Not supported format version "0.9"',
                      report.message)
        self.assertEqual(6, report.line)
        self.assertEqual(9, report.column)

    def test_missing_format(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        del md['Format']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        self.assertIn('Missing required key "Format"', all_[0].message)

    def test_not_existing_file(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        self.gaf.return_value = ['FlowClassifier.yaml']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('File is present in Manfiest Instance.yaml, but not in '
                      'filesystem', report.message)
        self.assertEqual(2, report.line)
        self.assertEqual(76, report.column)

    def test_extra_file_in_directory(self):
        mv = ManifestValidator('example/Classes')
        md = deepcopy(MANIFEST_DICT)
        del md['Classes']['org.openstack.Flow']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('File is not present in Manfiest, but it is in '
                      'filesystem: FlowClassifier.yaml', report.message)
