from mplcheck.validators import base

UI_FILE = 'UI/ui.yaml'


class UiValidator(base.BaseValidator):

    def __init__(self, loader, context, name=UI_FILE):
        super(UiValidator, self).__init__(name, loader, context)

    def run(self):
        pass
