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

from mplcheck.checkers import code_structure
from mplcheck.tests import test_validator_helpers as helpers


class CodeStructureTest(helpers.BaseValidatorTestClass):
    def setUp(self):
        super(CodeStructureTest, self).setUp()
        self._checker = code_structure.CheckCodeStructure()

    def test_simple(self):
        SIMPLE_BODY = '$.deploy()'
        self.g = self._checker.codeblock(SIMPLE_BODY)

    def test_double_assigment(self):
        SIMPLE_BODY = [{
                '$a':'$.deploy()',
                '$b':'$.string()'}]
        self.g = self._checker.codeblock(SIMPLE_BODY)
        self.assertIn('Wrong code structure/assigment probably typo',
                      next(self.g).message)

    def test_multiline(self):
        MULTILINE_BODY = [
            '$.deploy()',
            {'$res': 'new(YaqlStuff)'},
            '$.call($res)',
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)

    def test_bad_assigment(self):
        MULTILINE_BODY = [
            '$.deploy()',
            {1: 'new(YaqlStuff)'},
            '$.call($res)',
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        self.assertIn('Not valid variable name "1"', next(self.g).message)

    def test_bad_assigment_case2(self):
        MULTILINE_BODY = [
            '$.deploy()',
            {'res': 'new(YaqlStuff)'},
            '$.call($res)',
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        p = next(self.g)
        self.assertIn('Not valid variable name "res"', p.message)

    def test_if(self):
        MULTILINE_BODY = [
            {'If': '$.deploy()',
             'Then': [
                 '$.w()',
                 {'$abc': '$a'}]}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)

    def test_while_missing_do(self):
        MULTILINE_BODY = [
            {'While': '$.deploy()'}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        p = next(self.g)
        self.assertIn('Missing keyword "Do" for "While" code structure',
                      p.message)

    def test_while_unknown_does(self):
        MULTILINE_BODY = [
            {'While': '$.deploy()',
             'Does': ['$.a()', '$.b()']}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        p1 = next(self.g)
        p2 = next(self.g)
        self.assertItemsEqual([
            'Unknown keyword "Does" in "While"',
            'Missing keyword "Do" for "While" code structure'],
            [p1.message, p2.message])

    def test_empty_return(self):
        MULTILINE_BODY = [
            {'Return': ''}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)

    def test_switch(self):
        MULTILINE_BODY = [
            {'Switch': {
                '$.black()': '$.single()',
                '$.blue()': [
                    '$.b()',
                    {'$w': 3}]},
             'Default': '$.a()'}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)

    def test_error_under_while_in_if(self):
        MULTILINE_BODY = [
            {'If': '1',
             'Then': {'While': '$.deploy()',
                      'Do': [
                          {'www': '$.a()'},
                          '$.b()']}}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        self.assertIn('Not valid variable name "www"', next(self.g).message)

    def test_not_string(self):
        MULTILINE_BODY  = [
            {'Try': [
                '$port.deploy()'],
                'Catch': '',
                'With': 213,
                'As': 'what',
                'Do': [
                    '$.string()']}]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        self.assertIn('Value should be string type "213"',
                      next(self.g).message)

    def test_not_empty(self):
        MULTILINE_BODY = [
            '$.deploy()',
            {'$d': 'new(YaqlStuff)'},
            '$.call($res)',
            {'Break':'a'},
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
        self.assertIn('There should be no value here "a"',
                      next(self.g).message)

