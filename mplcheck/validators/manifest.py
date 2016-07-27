import types

import yaml

from mplcheck import yaml_loader
from mplcheck.checks import manifest as checks
from mplcheck.error import error

from mplcheck.validators import base

MPL_CLASSES_DIR = 'Classes'
MANIFEST_FILE = 'manifest.yaml'


class ManifestValidator(base.BaseValidator):
    def __init__(self, loader, context, name=MANIFEST_FILE):
        super(ManifestValidator, self).__init__(name, loader, context)

    def run(self):
        try:
            fp = self.loader.open_file(self.name)
        except IOError:
            raise error('E000', 'Cannot open file', self.name)

        with fp:
            try:
                manifest = yaml.load(fp, yaml_loader.YamlLoader)
            except Exception:
                raise error('E000', 'Cannot load YAML file', self.name)

        format_, version = self._parse_version(manifest)

        self.context['manifest'] = {
            'format': format_,
            'version': version,
        }

        return self.run_checks(
            kwargs={'filename': self.name, 'manifest': manifest})

    def _parse_version(self, manifest):
        try:
            version = str(manifest[checks.FORMAT_KEY])
        except KeyError as exc:
            return checks.DEFAULT_FORMAT, checks.DEFAULT_VERSION

        format_, _, version = version.partition('/')
        if not version and format_[0].isdigit():
            return checks.DEFAULT_FORMAT, format_
        if version:
            return format_, version

        raise error('E000', 'Invid package version', filename=self.name)


ManifestValidator.add_check(checks.check_manifest_structure)
