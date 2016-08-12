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

import unittest

from mplcheck import checkers


class CodeStructureTest(unittest.TestCase):
    def setUp(self):
        self._checker = checkers.CheckCodeStructure()
        self.g = None

    def tearDown(self):
        with self.assertRaises(StopIteration):
            while True:
                print('Left Error: ', next(self.g))

    def test_simple(self):
        SIMPLE_BODY = '$.deploy()'
        self.g = self._checker.codeblock(SIMPLE_BODY)

    def test_multiline(self):
        MULTILINE_BODY = [
            '$.deploy()',
            {'res': 'new(YaqlStuff)'},
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
        p = next(self.g)
        self.assertIn('Not valid variable name', p.message)

    def test_if(self):
        MULTILINE_BODY = [
            {'If': '$.deploy()',
             'Then': [
                 '$.w()',
                 {'abc': 3}]}
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
        p = next(self.g)
        self.assertIn('Unknown keyword "Does" in "While"',
                      p.message)

    def test_empty_return(self):
        MULTILINE_BODY = [
            {'Return':''}
        ]
        self.g = self._checker.codeblock(MULTILINE_BODY)
