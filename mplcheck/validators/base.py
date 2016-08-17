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

import itertools

import six

from mplcheck import error
from mplcheck import log

LOG = log.get_logger(__name__)


def check_version(method, version):
    pass


class BaseValidator(object):
    def __init__(self, loaded_package, _filter='.*'):
        self._loaded_pkg = loaded_package
        self._filter = _filter

    def _run_single(self, file_):
        pass

    def run(self):
        chain_of_suits = []
        for filename in self._loaded_pkg.search_for(self._filter):
            file_ = self._loaded_pkg.read(filename)
            chain_of_suits.append(self._run_single(file_))
        return itertools.chain(*chain_of_suits)

    def _valid_string(self, value):
        if not isinstance(value, six.string_types):
            yield error.report.E040('Value is not a string "{0}"'
                                    .format(value),
                                    value)


class YamlValidator(BaseValidator):
    def __init__(self, loaded_package, _filter='.*'):
        super(YamlValidator, self).__init__(loaded_package, _filter)
        self._checkers = {}

    def add_checker(self, function, key=None, required=True):
        checkers = self._checkers.setdefault(key, {'checkers': [],
                                                   'required': False})
        checkers['checkers'].append(function)
        if key is None:
            checkers['required'] = False
        elif required:
            checkers['required'] = True

    def _run_single(self, file_):
        multi_documents = file_.yaml()
        reports_chain = []

        def run_helper(name, checkers, data):
            for checker in checkers:
                try:
                    result = checker(data)
                except Exception:
                    result = error.report.E000('Checker failed for "{0}" more '
                                               'information in logs'
                                               .format(name))
                    LOG.info('Checker failed for keyword "{0}"', name)
                if result:
                    reports_chain.append(result)

        for ast in multi_documents:
            file_check = self._checkers.get(None)
            if file_check:
                run_helper(None, file_check['checkers'], ast)
            for key, value in six.iteritems(ast):
                checkers = self._checkers.get(key)
                if checkers:
                    run_helper(key, checkers['checkers'], ast[key])
                else:
                    reports_chain.append(self._unknown_keyword(key, value))
            missing = set(key for key, value in six.iteritems(self._checkers)
                          if value['required']) - set(ast.keys())
            for m in missing:
                reports_chain.append([error.report.E020('Missing required key '
                                     '"{0}"'.format(m), m)])
        return itertools.chain(*reports_chain)

    def _unknown_keyword(self, key, value):
        yield error.report.W010('Unknown keyword "{0}"'.format(key), key)
