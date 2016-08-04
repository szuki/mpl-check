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


from collections import OrderedDict
from copy import deepcopy
from mock import call
from mock import patch
import unittest
import yaml

from mplcheck.validators.manifest import ManifestValidator


def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u'tag:yaml.org,2002:map', value)

yaml.add_representer(OrderedDict, represent_ordereddict)


MANIFEST_LIST = [
    ('Author', 'Mirantis, Inc'),
    ('Classes', {'org.openstack.Flow': 'FlowClassifier.yaml',
                 'org.openstack.Instance': 'Instance.yaml'}),
    ('Description', 'Integration with world.\n'),
    ('Format', '1.3'),
    ('FullName', 'org.openstack'),
    ('Name', 'Murano Test plugin'),
    ('Require', {'murano-test-plugin': None}),
    ('Tags', ['Openstack', 'Test']),
    ('Type', 'Library'),
    ('UI', 'ui.yaml'),
    ('Logo', 'logo.png')]


class ManfiestValidatorTests(unittest.TestCase):
    def setUp(self):
        self._gaf_patcher = patch('mplcheck.validators.manifest.get_all_files')
        self.gaf = self._gaf_patcher.start()
        self.gaf.return_value = ['FlowClassifier.yaml', 'Instance.yaml']
        self._oe_patcher = patch('os.path.exists')
        self.exists = self._oe_patcher.start()
        self.exists.return_value = [True, True]

    def test_validate(self):
        mv = ManifestValidator('example/Classes')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(len(all_), 0, 'There should not be any check errors')

    def test_wrong_format(self):
        mv = ManifestValidator('example/Classes')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
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
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        md['Format'] = '0.9'
        del md['Format']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(0, len(all_))

    def test_not_existing_file(self):
        mv = ManifestValidator('example/Classes')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
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
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        del md['Classes']['org.openstack.Flow']
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('File is not present in Manfiest, but it is in '
                      'filesystem: FlowClassifier.yaml', report.message)

    def test_wrong_type(self):
        mv = ManifestValidator('example/Classes')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        md['Type'] = 'Shared Library'
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Type is invalid "Shared Library"', report.message)
        self.assertEqual(11, report.line)
        self.assertEqual(7, report.column)

    def test_wrong_require_type(self):
        mv = ManifestValidator('example/Classes')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        md['Require'] = [1, 2, 3]
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Require is not a dict type', report.message)
        self.assertEqual(9, report.line)
        self.assertEqual(10, report.column)

    def test_wrong_ui_type(self):
        mv = ManifestValidator('')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        md['UI'] = [1, 2, 3]
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('UI is not a filename', report.message)
        self.assertEqual(12, report.line)
        self.assertEqual(5, report.column)

    def test_wrong_logo_type(self):
        mv = ManifestValidator('')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        md['Logo'] = [1, 2, 3]
        mv.parse(yaml.dump(md))
        all_ = [w for w in mv.validate()]
        self.assertEqual(1, len(all_))
        report = all_[0]
        self.assertIn('Logo is not a filename', report.message)
        self.assertEqual(13, report.line)
        self.assertEqual(7, report.column)

    def test_missing_ui_and_logo_file(self):
        mv = ManifestValidator('')
        md = OrderedDict(deepcopy(MANIFEST_LIST))
        mv.parse(yaml.dump(md))
        self.exists.side_effect = [False, False]
        all_ = [w for w in mv.validate()]
        self.exists.assert_has_calls([call('UI/ui.yaml'), call('logo.png')],
                                     any_order=True)
        self.assertEqual(2, len(all_))
        if self.exists.call_args[0][0] == 'UI/ui.yaml':
            r1, r2 = all_[1], all_[0]
        else:
            r1, r2 = all_[0], all_[1]
        self.assertIn('There is no UI file mention in manifest "ui.yaml"',
                      r1.message)
        self.assertEqual(12, r1.line)
        self.assertEqual(5, r1.column)
        self.assertIn('There is no Logo file mention in manifest "logo.png"',
                      r2.message)
        self.assertEqual(13, r2.line)
        self.assertEqual(7, r2.column)
