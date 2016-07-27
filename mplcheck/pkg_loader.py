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

    @abc.abstractmethod
    def exists(self, name):
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

    def open_file(self, name, mode='r'):
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
