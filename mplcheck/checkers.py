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
