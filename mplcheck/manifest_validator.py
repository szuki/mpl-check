from copy import deepcopy
from itertools import chain
from mock import patch
import os.path
import six
import unittest
import yaml
import yaml_loader



class Report(object):
    COLUMN_LINE = ' at line {line}, column {column}'
    def __init__(self, message, element, **kwargs):
        mark = getattr(element, '__yaml_meta__', None)
        self._msg = message.format(element=element, **kwargs)
        if mark:
            self._msg += self.COLUMN_LINE.format(line=mark.line,
                                                  column=mark.column)

    @property
    def msg(self):
        return self._msg

    def __repr__(self):
        return '{0}'.format(self._msg)

REPORTS = {
    'E020': 'Missing required key "{element}"',
    'E030': 'Not supported format version "{element}"',
    'E040': 'Value is not a string "{element}"',
    'E050': 'File is present in Manfiest {fname}, but not in filesystem',

    'W020': 'File is not present in Manfiest, but it is '
            'in filesystem: {fname}',
    'W030': 'Extra file in directory "{fname}"',
}

for key, value in six.iteritems(REPORTS):
    msg = REPORTS[key]
    def _w(message):
        def __create(element, **kwargs):
            return Report(message, element, **kwargs)
        return __create
    setattr(Report, key, staticmethod(_w(msg)))


#Note: It would be best to use glob, but untill python 3.5
#      recursive is not supported...
def get_all_files(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            matches.append(os.path.join(root, fname))
    return matches


class ManifestValidator(object):

    def __init__(self, class_directory):
        self.data = {}
        self._class_directory = class_directory
        self._keys_checker = {}
        self._reports = []
        BASE_CHECKERS = {
            'Format': self._valid_format,
            'Classes': self._valid_classes,
            'Author': self._valid_string,
            'FullName': self._valid_string,
            'Name': self._valid_string,
            'Tags': self._valid_tags,
            'Require': self._valid_require,
            'Type': self._valid_type,
            'Description': self._valid_string,
        }
        for key, checker in six.iteritems(BASE_CHECKERS):
            # Let's assume for now that all are required
            self.add_validator(key, checker, required=True)

    def add_validator(self, key, function, required=True):
        kcheckers = self._keys_checker.setdefault(key, {'checkers': [],
                                                        'required': False})
        kcheckers['checkers'].append(function)
        if required:
            kcheckers['required'] = True


    def parse(self, stream):
        try:
            self.data = yaml.load(stream, yaml_loader.YamlLoader)
        except Exception:
            # XXX: fix it it should be yaml
            print('Exception')
        return self.data

    def validate(self):
        extra_keys = set(self.data.keys()) - set(self._keys_checker.keys())
        if extra_keys:
            for key in extra_keys:
                self._unknown_keyword(key, self.data[key])
        for k, v in six.iteritems(self._keys_checker):
            if k in self.data:
                for checker in v['checkers']:
                    checker(k, self.data[k])
            else:
                if v['required']:
                    self.report(Report.E020, k)
        return self._reports

    def _unknown_keyword(self, name, value):
        self.report(Report.W020, key)

    def _valid_format(self, name, value):
        if value not in ['1.0', '1.1', '1.2', '1.3']:
            self.report(Report.E030, value)


    def _valid_classes(self, name, value):
        files = set(value.values())
        existing_files = set(get_all_files(self._class_directory))
        for fname in files - existing_files:
            self.report(Report.E050, name, fname=fname)
        for fname in existing_files - files:
            self.report(Report.W020, value, fname=fname)

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            self.report(Error.E040(value=value))

    def _valid_tags(self, name, value):
        if not isinstance(value, list):
            raise Error('Tags should be a list')

    def _valid_require(self, name, value):
        pass

    def _valid_type(self, name, value):
        pass

    def report(self, type_, element, **kwargs):
        self._reports.append(type_(element, **kwargs))


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
        self._gaf_patcher= patch('__main__.get_all_files')
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
