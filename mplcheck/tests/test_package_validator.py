
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

import mock

from mplcheck.validators import package
from mplcheck.tests import test_validator_helpers


class PackageValidatorTest(test_validator_helpers.BaseValidatorTestClass):
    def setUp(self):
        self.loaded_pkg = mock.Mock()
        self.pkg_validator = package.PackageValidator(self.loaded_pkg)

    def test_missing_manifest(self):
        self.loaded_pkg.search_for.return_value = []
        self.g = self.pkg_validator.run()
        self.assertIn('Missing manifest.yaml', next(self.g).message)
        self.loaded_pkg.search_for.assert_called_once_with('^manifest.yaml$')
