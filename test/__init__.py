from distutils.spawn import find_executable
from os import environ
from os.path import dirname, realpath
import sys

try:
    import webtest
    webtest  # Linter.. I beat you ;)
except:
    raise Exception("""
could not import webtest. Maybe try:
 $ sudo easy_install webtest
or something to that effect?
""")

dev_server_path = find_executable('dev_appserver.py')
if dev_server_path:
    dev_server_dir = dirname(realpath(dev_server_path))
    sys.path.insert(1, dev_server_dir)
    sys.path.insert(1, dev_server_dir + '/../platform/google_appengine')
else:
    raise Exception("""
# Google Cloud SDK isn't installed or is missing the AppEngine component:
# https://cloud.google.com/appengine/docs/standard/python/download
""")

import dev_appserver
dev_appserver.fix_sys_path()

environ['SERVER_SOFTWARE'] = 'Development'
