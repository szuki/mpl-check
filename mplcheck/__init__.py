import sys

from mplcheck.package_loaders import load_package



def check_manifest(manifest):


def check_package(package):
    pkg_loader = load_package(package)
    pkg_loader.open_file('manifest.yaml')


def main()
    check_package(sys.argv[1])