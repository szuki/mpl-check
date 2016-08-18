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

import argparse

from mplcheck import log
from mplcheck import manager

LOG = log.get_logger(__name__)


def parse_cli_args(args=None):

    usage_string = 'mpl-check [options] <path to package>'

    parser = argparse.ArgumentParser(
        description='murano-pkg-checker arguments',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        usage=usage_string
    )

    parser.add_argument('--select',
                        dest='select',
                        required=False,
                        type=str,
                        help='select errors and warnings (e.g. E001,W002)')

    parser.add_argument('--ignore',
                        dest='ignore',
                        required=False,
                        type=str,
                        help='skip errors and warnings (e.g. E042,W007)')

    parser.add_argument('pkg_path',
                        type=str,
                        help='Path to package')

    return parser.parse_args(args=args)


def run():
    args = parse_cli_args()
    m = manager.Manager(args.pkg_path)
    m.load_plugins()
    if args.select:
        select = args.select.split(',')
    else:
        select = None
    if args.ignore:
        ignore = args.ignore.split(',')
    else:
        ignore = None
    errors = m.validate(select=select, ignore=ignore)
    fmt = manager.PlainTextFormatter()
    for l in fmt.format(errors):
        print(l)

if __name__ == '__main__':
    run()
