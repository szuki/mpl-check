class CheckError(Exception):

    def __init__(self, code, message, filename=None,
                 line=0, column=0, source=None):
        self.code = code
        self.message = message
        self.filename = filename
        self.line = line
        self.column = column
        self.source = source


def error(code, message, filename=None, line=0, column=0, source=None):
    return CheckError(code=code, message=message, filename=filename,
                      line=line, column=column, source=source)


def yaml_error(code, message, filename, yaml_obj):
    meta = getattr(yaml_obj, '__yaml_meta__', None)
    kwargs = {}
    if meta is not None:
        kwargs['line'] = meta.line + 1
        kwargs['column'] = meta.column + 1
        kwargs['source'] = meta.get_snippet()
    return CheckError(code=code, message=message, filename=filename, **kwargs)
