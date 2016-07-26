import six
import yaml
import yaml_loader

class Report(object):
    COLUMN_LINE = ' at line {line}, column {column} in ${yaml_name}'
    def __init__(self, message, element, **kwargs):
        mark = getattr(element, '__yaml_meta__', None)
        self._msg = message.format(element=element, **kwargs)
        if mark:
            self._msg += self.COLUMN_LINE.format(line=mark.line,
                                                 column=mark.column,
                                                 yaml_name=mark.name)

    @property
    def msg(self):
        return self._msg

    def __repr__(self):
        return '{0}'.format(self._msg)

REPORTS = {
    'E020': 'Missing required key "{element}"',
    'E030': 'Not supported format version "{element}"',
    'E040': 'Value is not a string "{element}"',
    'E050': 'File is present in Manfiest {fname}, but not in filesystem',

    'W010': 'Extra key in manifest "{element}"',
    'W020': 'File is not present in Manfiest, but it is '
            'in filesystem: {fname}',
    'W030': 'Extra file in directory "{fname}"',
}

for key, value in six.iteritems(REPORTS):
    msg = REPORTS[key]
    def _w(message):
        def __create(element, **kwargs):
            return Report(message, element, **kwargs)
        return __create
    setattr(Report, key, staticmethod(_w(msg)))


class BaseValidator(object):
    def __init__(self):
        self.data = {}
        self._keys_checker = {}
        self._reports = []

    def add_validator(self, key, function, required=True):
        kcheckers = self._keys_checker.setdefault(key, {'checkers': [],
                                                        'required': False})
        kcheckers['checkers'].append(function)
        if required:
            kcheckers['required'] = True


    def parse(self, stream):
        try:
            self.data = yaml.load(stream, yaml_loader.YamlLoader)
        except Exception:
            # XXX: fix it it should be yaml error
            print('Exception')
        return self.data

    def validate(self):
        extra_keys = set(self.data.keys()) - set(self._keys_checker.keys())
        if extra_keys:
            for key in extra_keys:
                self._unknown_keyword(key, self.data[key])
        for k, v in six.iteritems(self._keys_checker):
            if k in self.data:
                for checker in v['checkers']:
                    checker(k, self.data[k])
            else:
                if v['required']:
                    self.report(Report.E020, k)
        return self._reports

    def _unknown_keyword(self, name, value):
        self.report(Report.W010, name)

    def report(self, type_, element, **kwargs):
        self._reports.append(type_(element, **kwargs))

    def _valid_string(self, name, value):
        if not isinstance(value, six.string_types):
            self.report(Error.E040(value=value))
