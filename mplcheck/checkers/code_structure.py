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

import six

from mplcheck.checkers import yaql_checker
from mplcheck import error


def check_req(check, required=True):
    return locals()

CODE_STRUCTURE = {
    'Try': {
        'keywords': {
            'Try': check_req('codeblock'),
            'Catch': check_req('empty'),
            'With': check_req('string'),
            'As': check_req('string'),
            'Do': check_req('codeblock'),
            'Else': check_req('codeblock', False),
            'Finally': check_req('codeblock', False)}},
    'Parallel': {
        'keywords': {
            'Limit': check_req('codeblock', False),
            'Parallel': check_req('codeblock')},
    },
    'Repeat': {
        'keywords': {
            'Repeat': check_req('number'),
            'Do': check_req('codeblock')}},
    'If': {
        'keywords': {
            'If': check_req('predicate'),
            'Then': check_req('codeblock'),
            'Else': check_req('codeblock', False)}
    },
    'Break': {
        'keywords': {
            'Break': check_req('empty')}
    },
    'Return': {
        'Return': check_req('expression'),
    },
    'While': {
        'keywords': {
            'While': check_req('predicate'),
            'Do': check_req('codeblock')}
    },
    'For': {
        'keywords': {
            'For': check_req('string'),
            'In': check_req('expression'),
            'Do': check_req('codeblock')}
    },
    'Match': {
        'keywords': {
            'Match': check_req(('expression', 'codeblock')),
            'Value': check_req('expression'),
            'Default': check_req('codeblock'),
        }
    },
    'Switch': {
        'keywords': {
            'Switch': check_req(('predicate', 'codeblock')),
            'Default': check_req('codeblock')}
    }
}


class CheckCodeStructure(object):
    def __init__(self):
        self._check_mappings = {
            'codeblock': self.codeblock,
            'predicate': self.yaql,
            'empty': self.empty,
            'expression': self.yaql,
            'string': self.string,
            'number': self.yaql,
        }
        self._yaql_checker = yaql_checker.YaqlChecker()

    def string(self, value):
        if not isinstance(value, six.string_types):
            yield error.report.E203('Value should be string type '
                                    '"{0}"'.format(value), value)

    def empty(self, value):
        if value:
            yield error.report.E200('There should be no value here '
                                    '"{0}"'.format(value), value)

    def yaql(self, value):
        if not self._yaql_checker(value):
            yield error.report.E202('Not a valid yaql expression '
                                    '"{0}"'.format(value), value)

    def codeblock(self, codeblocks):
        if isinstance(codeblocks, six.string_types):
            yield self._single_block(codeblocks)
        elif isinstance(codeblocks, list):
            for block in codeblocks:
                yield self._single_block(block)
        else:
            yield self._single_block(codeblocks)

    def _check_assigment(self, block):
        key = block.keys()[0]
        if not isinstance(key, six.string_types) or not key.startswith('$'):
            yield error.report.E201('Not valid variable name '
                                    '"{0}"'.format(key), key)

        value = block.values()[0]
        if isinstance(value, six.string_types):
            yield self.yaql(value)

    def _single_block(self, block):
        if isinstance(block, dict):
            yield self._check_structure(block)
        elif isinstance(block, six.string_types):
            yield self.yaql(block)

    def _run_check(self, check, value):
        yield self._check_mappings[check](value)

    def _check_structure(self, block):
        block_keys = block.keys()
        for key, value in six.iteritems(CODE_STRUCTURE):
            if key in block_keys:
                break
        else:
            if len(block_keys) == 1:
                yield self._check_assigment(block)
            else:
                yield error.report.E200('Wrong code structure/assigment '
                                        'probably typo', block)
            return

        keywords = value.get('keywords', {})
        kset = set(keywords.keys())
        block_keys_set = set(block_keys)
        for missing in (kset - block_keys_set):
            if keywords[missing]['required']:
                yield error.report.E200('Missing keyword "{0}" for "{1}" '
                                        'code structure'
                                        .format(missing, key), key)
        for unknown in (block_keys_set - kset - set([key])):
            yield error.report.E201('Unknown keyword "{0}" in "While"'
                                    .format(unknown), unknown)
        for ckey, cvalue in six.iteritems(keywords):
            check = cvalue['check']
            data = block.get(ckey)
            if not data:
                continue
            if isinstance(check, tuple):
                for left, right in six.iteritems(data):
                    yield self._run_check(check[0], left)
                    yield self._run_check(check[1], right)
            else:
                yield self._run_check(check, data)
