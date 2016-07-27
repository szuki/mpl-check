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


from itertools import chain
import six
import yaml
import yaml_loader


class Report(object):
    PREFIX = '{code}:'
    COLUMN_LINE = ' at line {line}, column {column} in ${yaml_name}'

    def __init__(self, message, element, **kwargs):
        mark = getattr(element, '__yaml_meta__', None)
        self._msg = message.format(element=element, **kwargs)
        if mark:
            self._msg += self.COLUMN_LINE.format(line=mark.line,
                                                 column=mark.column,
                                                 yaml_name=mark.name)

    @property
    def msg(self):
        return self._msg

    def __repr__(self):
        return '{0}'.format(self._msg)

REPORTS = {
    'E011': 'Invalid class name "{element}"',
    'E020': 'Missing required key "{element}"',
    'E030': 'Not supported format version "{element}"',
    'E040': 'Value is not a string "{element}"',
    'E050': 'File is present in Manfiest {fname}, but not in filesystem',
    'E060': 'Namespace of class {element} in {class_namespace} doesn\'t match '
            'namespace provided in Manifest',
    'E070': 'Tags should be a list',

    'W010': 'Extra key in manifest "{element}"',
    'W011': 'Invalid Case of class name "{element}"',
    'W020': 'File is not present in Manfiest, but it is '
            'in filesystem: {fname}',
    'W030': 'Extra file in directory "{fname}"',
}

for key, value in six.iteritems(REPORTS):
    msg = REPORTS[key]

    def _w(message):
        prefix = Report.PREFIX.format(code=key)

        def __create(element, **kwargs):
            return Report(prefix + message, element, **kwargs)
        return __create
    setattr(Report, key, staticmethod(_w(msg)))


class BaseValidator(object):
    def __init__(self):
        self.data = {}
        self._keys_checker = {}

    def add_validator(self, key, function, required=True):
        kcheckers = self._keys_checker.setdefault(key, {'checkers': [],
                                                        'required': False})
        kcheckers['checkers'].append(function)
        if key == '_AST_':
            kcheckers['required'] = False
        elif required:
            kcheckers['required'] = True

    def parse(self, stream):
        try:
            self.data = yaml.load(stream, yaml_loader.YamlLoader)
        except Exception:
            # XXX: fix it it should be yaml error
            print('Exception')
        return self.data

    def validate(self):
        reports_chain = []

        def run_checkers(name, checkers, data):
            for checker in checkers:
                result = checker(name, data)
                if result:
                    reports_chain.append(result)

        file_check = self._keys_checker.get('_AST_')
        if file_check:
            run_checkers('_AST_', file_check['checkers'], self.data)
        for key, value in six.iteritems(self.data):
            key_checkers = self._keys_checker.get(key)
            if key_checkers:
                run_checkers(key, key_checkers['checkers'], self.data[key])
            else:
                self._unknown_keyword(key, value)
        missing = set(key for key, value in six.iteritems(self._keys_checker)
                      if value['required']) - set(self.data.keys())
        for m in missing:
            reports_chain.append([Report.E020(m)])
        return chain(*reports_chain)

    def _unknown_keyword(self, name, value):
        yield Report.W010(name)

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            yield Report.E040(value=value)
