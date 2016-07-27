import types


class BaseValidator(object):

    checks = []

    # FIXME: Make something with argument order
    def __init__(self, name, loader, context):
        self.name = name
        self.loader = loader
        self.context = context

    @classmethod
    def add_check(cls, check):
        cls.checks.append(check)

    # TODO: Filter checks by version etc.
    def run_checks(self, args=(), kwargs=None):
        if not kwargs:
            kwargs = {}

        for check in self.checks:
            try:
                result = check(self.context, *args, **kwargs)
            except Exception:
                raise

            if isinstance(result, types.GeneratorType):
                for error in result:
                    print(error)
