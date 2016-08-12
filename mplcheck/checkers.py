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
import yaql

from mplcheck import error


class NamespaceChecker(object):
    def valid_namespace(self, value):
        self._manifest_classes = value
        namespaces = value.get('Namespaces')
        name = value.get('Name')
        namespace = namespaces.get('=')
        if namespace:
            namespace = str(namespace)
        if name:
            name = str(name)
            class_path = namespace + '.' + name
            fname = self._manifest_classes.get(class_path)
            if not fname:
                yield error.report.E060('Namespace of class "{class_}" in '
                                        '"{class_namespace}" doesn\'t match '
                                        'namespace provided in Manifest'
                                        .format(class_=name,
                                                class_namespace=class_path),
                                        fname)

ITERATORS_LIMIT = 1000
EXPRESSION_MEMORY_QUOTA = 512*1024

ENGINE_10_OPTIONS = {
    'yaql.limitIterators': ITERATORS_LIMIT,
    'yaql.memoryQuota': EXPRESSION_MEMORY_QUOTA,
    'yaql.convertSetsToLists': True,
    'yaql.convertTuplesToLists': True,
    'yaql.iterableDicts': True
}

ENGINE_12_OPTIONS = {
    'yaql.limitIterators': ITERATORS_LIMIT,
    'yaql.memoryQuota': EXPRESSION_MEMORY_QUOTA,
    'yaql.convertSetsToLists': True,
    'yaql.convertTuplesToLists': True
}


def _add_operators(engine_factory):
    engine_factory.insert_operator(
        '>', True, 'is',
        yaql.factory.OperatorType.BINARY_LEFT_ASSOCIATIVE, False)
    engine_factory.insert_operator(
        None, True, ':',
        yaql.factory.OperatorType.BINARY_LEFT_ASSOCIATIVE, True)
    engine_factory.insert_operator(
        ':', True, ':',
        yaql.factory.OperatorType.PREFIX_UNARY, False)
    engine_factory.operators.insert(0, ())


def _create_engine():
    engine_factory = yaql.factory.YaqlFactory()
    _add_operators(engine_factory=engine_factory)
    options = ENGINE_12_OPTIONS
    return engine_factory.create(options=options)


class YaqlChecker(object):
    def __init__(self):
        self._engine = _create_engine()

    def __call__(self, data):
        try:
            self._engine(data)
        except yaql.utils.exceptions.YaqlParsingException:
            return False
        except TypeError:
            return False
        return True


def check_req(check, required=True):
    return locals()

CODE_STRUCTURE = {
    'Try': {
        'check': 'codeblock',
        'keywords': {
            'Catch': check_req('empty'),
            'With': check_req('string'),
            'As': check_req('string'),
            'Do': check_req('codeblock'),
            'Else': check_req('codeblock', False),
            'Finally': check_req('codeblock', False)}},
    'Parallel': {
        'keywords': {
            'Limit': check_req('codeblock', False)},
        'check': 'codeblock',
    },
    'Repeat': {
        'check': 'number',
        'keywords': {
            'Do': check_req('codeblock')}},
    'If': {
        'check': 'predicate',
        'keywords': {
            'Then': check_req('codeblock'),
            'Else': check_req('codeblock', False)}
    },
    'Breaks': {
        'check': 'empty',
    },
    'Return': {
        'check': 'expression',
    },
    'While': {
        'check': 'predicate',
        'keywords': {
            'Do': check_req('codeblock')}
    },
    'For': {
        'check': 'string',
        'keywords': {
            'In': check_req('expression'),
            'Do': check_req('codeblock')}
    },
    'Match': {
        'check': {'expression': 'codeblock'},
        'keywords': {
            'Value': check_req('expression'),
            'Default': check_req('codeblock'),
        }
    },
    'Switch': {
        'check': {'predicate': 'codeblock'},
        'keywords': {
            'Default': check_req('codeblock')}
    }
}


class CheckCodeStructure(object):
    def __init__(self):
        self._check_mappings = {
            'codeblock': self.codeblock,
            'predictate': self.yaql,
            'empty': self.empty,
            'expression': self.yaql,
            'string': self.string,
            'number': self.yaql,
        }
        self._yaql_checker = YaqlChecker()

    def string(self, value):
        if isinstance(value, six.string_types):
            yield error.report.E203('Value should be string type'
                                    '"{0}"'.format(value), value)

    def empty(self, value):
        if value:
            yield error.report.E200('There should be no value here '
                                    '"{0}"'.format(value), value)

    def yaql(self, value):
        if not self._yaql_checker(value):
            yield error.report.E202('Not valid yaql expression '
                                    '"{0}"'.format(value), value)

    def codeblock(self, codeblocks):
        if isinstance(codeblocks, six.string_types):
            for p in self._single_block(codeblocks):
                yield p
        elif isinstance(codeblocks, list):
            for block in codeblocks:
                for p in self._single_block(block):
                    yield p
        else:
            for p in self._single_block(codeblocks):
                yield p

    def _check_assigment(self, block):
        key = block.keys()[0]
        if not isinstance(key, six.string_types) or not key.startswith('$'):
            yield error.report.E201('Not valid variable name '
                                    '"{0}"'.format(key), key)
        value = block.values()[0]
        for p in self.yaql(value):
            yield p

    def _single_block(self, block):
        if isinstance(block, dict):
            for p in self._check_structure(block):
                yield p

    def _run_check(self, check, value):
        for p in self._check_mappings[check](value):
            yield p

    def _check_structure(self, block):
        block_keys = block.keys()
        for key, value in six.iteritems(CODE_STRUCTURE):
            if key in block_keys:
                break
        else:
            if len(block_keys) == 1:
                for p in self._check_assigment(block):
                    yield p
            else:
                yield error.report.E200('Wrong code structure probably '
                                        'typo in keyword "{0}"'
                                        .format(key), key)
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
                    for p in self._run_check(check[0], left):
                        yield p
                    for p in self._run_check(check[1], right):
                        yield p
            else:
                for p in self._run_check(check, data):
                    yield p
