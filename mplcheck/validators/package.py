from mplcheck import pkg_loader
from mplcheck.validators import base
from mplcheck.validators import manifest
from mplcheck.validators import mplclass
from mplcheck.validators import ui


class PackageValidator(base.BaseValidator):

    def __init__(self, name):
        loader = pkg_loader.load_package(name)
        super(PackageValidator, self).__init__(
            name,
            loader=loader,
            context={'loader': loader})

    def run(self):
        validator = manifest.ManifestValidator(
            loader=self.loader, context=self.context)
        validator.run()

        validator = ui.UiValidator(loader=self.loader, context=self.context)
        validator.run()

        class_files = self.loader.list_files('Classes')
        for class_file in class_files:
            validator = mplclass.MplClassValidator(
                name=class_file, loader=self.loader, context=self.context)
            validator.run()
