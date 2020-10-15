"""
This file is used to validate publish settings.
"""
from __future__ import print_function

import os
import sys
import importlib


COMPONENTS_PACKAGE = 'hierarchy_tree'

COMPONENTS_LIB = importlib.import_module(COMPONENTS_PACKAGE)

MISSING_DIST_MSG = 'Warning {} was not found in `{}.__init__.{}`!!!'
MISSING_MANIFEST_MSG = '''
Warning {} was not found in `MANIFEST.in`!
It will not be included in the build!
'''

with open('MANIFEST.in', 'r') as f:
    MANIFEST = f.read()


def check_dist(dist, filename):
    """
    Verifies that the JS code has been bundled correctly
    """
    # Support the dev bundle.
    if filename.endswith('dev.js'):
        return True

    return any(
        filename in x
        for d in dist
        for x in (
            [d.get('relative_package_path')]
            if not isinstance(d.get('relative_package_path'), list)
            else d.get('relative_package_path')
        )
    )


def check_manifest(filename):
    """
    Cross-checks generated files with the MANIFEST file
    """
    return filename in MANIFEST


def check_file(dist, filename):
    """
    Ensures that build files have been generated correctly
    """
    if not check_dist(dist, filename):
        print(
            MISSING_DIST_MSG.format(filename, COMPONENTS_PACKAGE, '_JS_DIST'),
            file=sys.stderr
        )
    if not check_manifest(filename):
        print(MISSING_MANIFEST_MSG.format(filename),
              file=sys.stderr)


for cur, _, files in os.walk(COMPONENTS_PACKAGE):
    for f in files:

        if f.endswith('js'):
            # noinspection PyProtectedMember
            check_file(COMPONENTS_LIB._JS_DIST, f)
        elif f.endswith('css'):
            # noinspection PyProtectedMember
            check_file(COMPONENTS_LIB._CSS_DIST, f)
        elif not f.endswith('py'):
            check_manifest(f)
