from mplcheck.base_validator import Report

class NamespaceChecker(object):
    def __init__(self):
        self._maifest_classes = {}
        self._namespace = {}
        self._classname = None

    def valid_classes(self, name, value):
        self._manifest_classes = value 

    def valid_namespace(self, name, value):
        self._namespace = value

    def valid_classname(self, name, value):
        namespace = self._namespace.get('=')
        if namespace:
            class_path = namespace + '.' + value 
            fname = self._manifest_classes.get(class_path)
            if not fname: 
                yield Report.E060(name, class_namespace=class_path)

