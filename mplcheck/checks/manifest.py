import os

import six

from mplcheck.error import yaml_error


FORMAT_KEY = 'Format'
FORMAT_MPL_PREFIX = 'MuranoPL'
DEFAULT_FORMAT = 'MuranoPL'
DEFAULT_VERSION = '1.0'


def check_manifest_structure(context, filename, manifest):
    classes = manifest.get('Classes', [])

    for classname, classfile in six.iteritems(classes):
        classfile = os.path.join('Classes', classfile)
        if not context['loader'].exists(classfile):
            yield yaml_error(
                'E000', "Class file '{0}' referenced in manifest.yaml "
                        "is not found.".format(filename), filename, classname)

    context['manifest']['classes'] = classes
