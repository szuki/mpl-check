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
    'E020': 'Missing required key "{element}"',
    'E030': 'Not supported format version "{element}"',
    'E040': 'Value is not a string "{element}"',
    'E050': 'File is present in Manfiest {fname}, but not in filesystem',
    'E060': 'Namespace of class {element} in {class_namespace} doesn\'t match '
            'namespace provided in Manifest',
    'E070': 'Tags should be a list',

    'W010': 'Extra key in manifest "{element}"',
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


class BaseValidator(object):
    def __init__(self):
        self.data = {}
        self._keys_checker = {}

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
            # XXX: fix it it should be yaml error
            print('Exception')
        return self.data

    def validate(self):
        extra_keys = set(self.data.keys()) - set(self._keys_checker.keys())
        reports_chain = []
        if extra_keys:
            for key in extra_keys:
                self._unknown_keyword(key, self.data[key])
        for k, v in six.iteritems(self._keys_checker):
            if k == '_AST_':
                for checker in v['checkers']:
                    result = checker(k, self.data)
                    if result:
                        reports_chain.append(result)
            elif k in self.data:
                for checker in v['checkers']:
                    result = checker(k, self.data[k])
                    if result:
                        reports_chain.append(result)
            else:
                if v['required']:
                    reports_chain.append([Report.E020(k)])
        return chain(*reports_chain)

    def _unknown_keyword(self, name, value):
        yield Report.W010(name)

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            yield Report.E040(value=value)
