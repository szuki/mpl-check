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

import mock

from mplcheck import pkg_loader


class FileWrapperTest(unittest.TestCase):

    def test_file_wrapper(self):
        m_file = mock.mock_open(read_data='text')
        with mock.patch('mplcheck.pkg_loader.open', m_file):
            f = pkg_loader.FileWrapper('fake_path')
            self.assertEqual('text', f.raw())
            self.assertEqual(['text'], f.yaml())

        m_file = mock.mock_open(read_data='!@#$%')
        with mock.patch('mplcheck.pkg_loader.open', m_file):
            f = pkg_loader.FileWrapper('fake_path')
            self.assertEqual('!@#$%', f.raw())
            self.assertEqual(None, f.yaml())


class FakeLoader(pkg_loader.BaseLoader):

    @classmethod
    def try_load(cls, path):
        pass

    def _open_file(self, path, mode='r'):
        pass

    def exists(self, name):
        pass

    def list_files(self, subdir=None):
        if subdir is None:
            return ['1.yaml', '2.sh', 'sub/3.yaml']
        else:
            return ['3.yaml']


class BaseLoaderTest(unittest.TestCase):

    def test_search_for(self):
        fake = FakeLoader('fake')
        self.assertEqual(['1.yaml', 'sub/3.yaml'],
                         list(fake.search_for('.*\.yaml$')))
        self.assertEqual(['3.yaml'],
                         list(fake.search_for('.*\.yaml$', subdir='sub')))

    def test_read(self):
        fake = FakeLoader('fake')
        m_file_wrapper = mock.Mock()
        m_file = m_file_wrapper.return_value
        with mock.patch('mplcheck.pkg_loader.FileWrapper', m_file_wrapper):
            loaded = fake.read('fake')
            self.assertEqual(m_file, loaded)
            # check that cache works
            loaded = fake.read('fake')
            self.assertEqual(m_file, loaded)


class DirectoryLoaderTest(unittest.TestCase):

    def _load_fake_pkg(self):
        with mock.patch('mplcheck.pkg_loader.os.path.isdir') as m_isdir:
            m_isdir.return_value = True
            return pkg_loader.DirectoryLoader.try_load('fake')


    def test_try_load(self):
        #NOTE(sslypushenko) Using mock.patch here as decorator breaks pdb
        pkg = self._load_fake_pkg()
        self.assertEqual('fake', pkg.path)
        with mock.patch('mplcheck.pkg_loader.os.path.isdir') as m_isdir:
            m_isdir.return_value = False
            pkg = pkg_loader.DirectoryLoader.try_load('fake')
            self.assertEqual(None, pkg)

    def test_list_files(self):
        #NOTE(sslypushenko) Using mock.patch here as decorator breaks pdb
        pkg = self._load_fake_pkg()
        with mock.patch('mplcheck.pkg_loader.os.walk') as m_walk:
            m_walk.return_value = (item for item in [
                ('fake', ['subdir'], ['1', '2']),
                ('fake/subdir', [], ['3', '4']),
            ])
            self.assertEqual(['1', '2', 'subdir/3', 'subdir/4'],
                             pkg.list_files())
            m_walk.return_value = (item for item in [
                ('fake/subdir', [], ['3', '4']),
            ])
            self.assertEqual(['3', '4'],
                             pkg.list_files(subdir='subdir'))

    def test_exist(self):
        #NOTE(sslypushenko) Using mock.patch here as decorator breaks pdb
        pkg = self._load_fake_pkg()
        with mock.patch('mplcheck.pkg_loader.os.path.exists') as m_exists:
            m_exists.return_value = True
            self.assertTrue(pkg.exists('1.yaml'))
            m_exists.return_value = False
            self.assertFalse(pkg.exists('1.yaml'))
