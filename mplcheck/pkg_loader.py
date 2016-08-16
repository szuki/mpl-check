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


import abc
import os
import re
import zipfile

import six
import yaml

from mplcheck import yaml_loader


class FileWrapper(object):

    def __init__(self, path, file_content):
        self._raw = file_content
        self._path = path
        try:
            self._yaml = yaml.load_all(file_content, yaml_loader.YamlLoader)
        except yaml.YAMLError as e:
            print path
            print e
            self._yaml = None

    def raw(self):
        return self._raw

    def yaml(self):
        return self._yaml

@six.add_metaclass(abc.ABCMeta)
class BaseLoader(object):
    def __init__(self, filename):
        self.filename = filename
        self._cached_files = dict()

    @classmethod
    @abc.abstractmethod
    def try_load(cls, filename):
        pass

    @abc.abstractmethod
    def list_files(self, subdir=None):
        pass

    @abc.abstractmethod
    def _open_file(self, path, mode='r'):
        pass

    @abc.abstractmethod
    def exists(self, name):
        pass

    def search_for(self, regex='.*'):
        r = re.compile(regex)
        return (self.read(f) for f in self.list_files() if r.match(f))

    def read(self, path):
        if path in self._cached_files:
            return self._cached_files[path]
        with self._open_file(path) as fp:
            self._cached_files[path] = FileWrapper(path, fp.read())
            return self._cached_files[path]


class DirectoryLoader(BaseLoader):

    @classmethod
    def try_load(cls, filename):
        if os.path.isdir(filename):
            return cls(filename)
        return None

    def _open_file(self, path, mode='r'):
        return open(os.path.join(self.filename, path), mode)

    def list_files(self, subdir=None):
        path = self.filename
        if subdir is not None:
            path = os.path.join(path, subdir)

        files = []
        for dirpath, dirnames, filenames in os.walk(path):
            files.extend(
                os.path.relpath(
                    os.path.join(dirpath, filename), self.filename)
                for filename in filenames)
        return files

    def exists(self, name):
        return os.path.exists(os.path.join(self.filename, name))


class ZipLoader(BaseLoader):

    def __init__(self, filename):
        super(ZipLoader, self).__init__(filename)
        self._zipfile = zipfile.ZipFile(self.filename)

    @classmethod
    def try_load(cls, filename):
        try:
            return cls(filename)
        except zipfile.BadZipfile:
            return None

    def _open_file(self, name, mode='r'):
        return self._zipfile.open(name, mode)

    def list_files(self, subdir=None):
        files = self._zipfile.namelist()
        if subdir is None:
            return files
        return [file_ for file_ in files
                if file_.startswith(subdir)]

    def exists(self, name):
        try:
            self._zipfile.getinfo(name)
            return True
        except KeyError:
            pass

        if not name.endswith('/'):
            try:
                self._zipfile.getinfo(name + '/')
                return True
            except KeyError:
                pass
        return False


PACKAGE_LOADERS = [DirectoryLoader, ZipLoader]


def load_package(package):
    for loader_cls in PACKAGE_LOADERS:
        loader = loader_cls.try_load(package)
        if loader is not None:
            return loader
    else:
        # FIXME:
        raise Exception('Cannot load package {0}: Unexpected format')
