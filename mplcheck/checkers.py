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
