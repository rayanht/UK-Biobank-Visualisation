from __future__ import print_function as _

import os as _os
import sys as _sys
import json

import dash as _dash

# noinspection PyUnresolvedReferences
from ._imports_ import *
from ._imports_ import __all__

if not hasattr(_dash, 'development'):
    print('Dash was not successfully imported. '
          'Make sure you don\'t have a file '
          'named \n"dash.py" in your current directory.', file=_sys.stderr)
    _sys.exit(1)

_BASEPATH = _os.path.dirname(__file__)
_filepath = _os.path.abspath(_os.path.join(_BASEPATH, 'package-info.json'))
with open(_filepath) as f:
    PACKAGE = json.load(f)

PACKAGE_NAME = PACKAGE['name'].replace(' ', '_').replace('-', '_')
__version__ = PACKAGE['version']

_current_path = _os.path.dirname(_os.path.abspath(__file__))

_THIS_MODULE = _sys.modules[__name__]

_JS_DIST = [
    {
        'relative_package_path': 'hierarchy_tree.min.js',
        'external_url': 'https://unpkg.com/{0}@{2}/{1}/{1}.min.js'.format(
            PACKAGE_NAME, __name__, __version__),
        'namespace': PACKAGE_NAME
    },
    {
        'relative_package_path': 'hierarchy_tree.min.js.map',
        'external_url': 'https://unpkg.com/{0}@{2}/{1}/{1}.min.js.map'.format(
            PACKAGE_NAME, __name__, __version__),
        'namespace': PACKAGE_NAME,
        'dynamic': True
    }
]

_CSS_DIST = []

for _component in __all__:
    setattr(locals()[_component], '_js_dist', _JS_DIST)
    setattr(locals()[_component], '_css_dist', _CSS_DIST)
