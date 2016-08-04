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

from mplcheck import error
from mplcheck import yaml_loader


class BaseValidator(object):
    def __init__(self):
        self.data = {}
        self._keys_checker = {}

    def add_checker(self, function, key=None, required=True):
        kcheckers = self._keys_checker.setdefault(key, {'checkers': [],
                                                        'required': False})
        kcheckers['checkers'].append(function)
        if key is None:
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

        file_check = self._keys_checker.get(None)
        if file_check:
            run_checkers(None, file_check['checkers'], self.data)
        for key, value in six.iteritems(self.data):
            key_checkers = self._keys_checker.get(key)
            if key_checkers:
                run_checkers(key, key_checkers['checkers'], self.data[key])
            else:
                reports_chain.append(self._unknown_keyword(key, value))
        missing = set(key for key, value in six.iteritems(self._keys_checker)
                      if value['required']) - set(self.data.keys())
        for m in missing:
            reports_chain.append([error.report.E020('Missing required key '
                                 '"{0}"'.format(m), m)])
        return chain(*reports_chain)

    def _unknown_keyword(self, name, value):
        yield error.report.W010('Extra key in manifest "{0}"'.format(name),
                                name)

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            yield error.report.E040('Value is not a string "{0}"'
                                    .format(value),
                                    value=value)
