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


from mplcheck.base_validator import Report


class NamespaceChecker(object):
    def __init__(self):
        self._maifest_classes = {}
        self._classname = None

    def valid_classes(self, name, value):
        self._manifest_classes = value

    def valid_mpl(self, ast, value):
        namespaces = value.get('Namespaces')
        namespace = namespaces.get('=')
        if namespace:
            namespace = str(namespace)
            name = value.get('Name')
            if name:
                name = str(name)
                class_path = namespace + '.' + name
                fname = self._manifest_classes.get(class_path)
                if not fname:
                    yield Report.E060(name, class_namespace=class_path)
