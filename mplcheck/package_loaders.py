import abc
import os
import zipfile

import six


@six.add_metaclass(abc.ABCMeta)
class BaseLoader(object):
    def __init__(self, filename):
        self.filename = filename

    @classmethod
    @abc.abstractmethod
    def try_load(cls, filename):
        pass

    @abc.abstractmethod
    def open_file(self, path, mode='r'):
        pass

    def read_file(self, path):
        with self.open_file(path) as fp:
            return fp.read()


class DirectoryLoader(BaseLoader):

    @classmethod
    def try_load(cls, filename):
        if os.path.isdir(filename):
            return cls(filename)
        return None

    def open_file(self, path, mode='r'):
        return open(os.path.join(self.filename, path), mode)

    def list_files(self):
        # FIXME: Relative path needed
        files = []
        for dirpath, dirnames, filenames in os.walk(self.filename):
            files.extend(os.path.join(dirpath, filename)
                         for filename in filenames)
        return files


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

    def open_file(self, name, mode='r'):
        return self._zipfile.open(name, mode)

    def list_files(self):
        return self._zipfile.namelist()


def load_package(package):
    for loader_cls in [DirectoryLoader, ZipLoader]:
        loader = loader_cls.try_load(package)
        if loader is not None:
            return loader
    else:
        # FIXME:
        raise Exception('Cannot load package {0}: Unexpected format')
