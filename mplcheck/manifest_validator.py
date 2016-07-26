import os.path
import six

from mplcheck.base_validator import BaseValidator, Report


#Note: It would be best to use glob, but untill python 3.5
#      recursive is not supported...
def get_all_files(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for fname in filenames:
            matches.append(os.path.join(root, fname))
    return matches

class ManifestValidator(BaseValidator):

    def __init__(self, class_directory):
        super(ManifestValidator, self).__init__()
        self._class_directory = class_directory
        BASE_CHECKERS = {
            'Format': self._valid_format,
            'Classes': self._valid_classes,
            'Author': self._valid_string,
            'FullName': self._valid_string,
            'Name': self._valid_string,
            'Tags': self._valid_tags,
            'Require': self._valid_require,
            'Type': self._valid_type,
            'Description': self._valid_string,
        }
        for key, checker in six.iteritems(BASE_CHECKERS):
            # Let's assume for now that all are required
            self.add_validator(key, checker, required=True)

    def _valid_format(self, name, value):
        if value not in ['1.0', '1.1', '1.2', '1.3']:
            self.report(Report.E030, value)

    def _valid_classes(self, name, value):
        files = set(value.values())
        existing_files = set(get_all_files(self._class_directory))
        for fname in files - existing_files:
            self.report(Report.E050, name, fname=fname)
        for fname in existing_files - files:
            self.report(Report.W020, value, fname=fname)

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            self.report(Error.E040(value=value))

    def _valid_tags(self, name, value):
        if not isinstance(value, list):
            raise Error('Tags should be a list')

    def _valid_require(self, name, value):
        pass

    def _valid_type(self, name, value):
        pass

    def report(self, type_, element, **kwargs):
        self._reports.append(type_(element, **kwargs))
