import os

os.environ['SERVER_SOFTWARE'] = 'Development'


try:
    import webtest
except:
    raise Exception("""
could not import webtest. Maybe try:
 $ sudo easy_install webtest
or something to that effect?
""")


from distutils.spawn import find_executable
from os.path         import dirname

dev_server_path = find_executable('dev_appserver.py')
if not dev_server_path:
    raise Exception("""
# Google Cloud SDK isn't installed or is missing the AppEngine component:
# https://cloud.google.com/appengine/docs/standard/python/download
""")
sdk_path = dirname(dev_server_path)

import sys
sys.path.insert(1, sdk_path)

import dev_appserver
dev_appserver.fix_sys_path()