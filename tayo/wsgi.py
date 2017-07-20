import os, sys
import site

path = os.path.abspath(__file__+'/../..')
if path not in sys.path:
    sys.path.append(path)

#python_home = '/home/ubuntu/lee/django_project'

python_home = os.path.abspath(__file__ + '/../..')

activate_this = python_home + '/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
#python_home = '/home/ubuntu/lee/django_project'

##python_version = '.'.join(map(str, sys.version_info[:2]))
#site_packages = python_home + '/lib/python%s/site-packages' % python_version
#sys.path.append(site_packages)
#site.addsitedir(site_packages)
# Remember original sys.path.

#prev_sys_path = list(sys.path)

# Add the site-packages directory.

#site.addsitedir(site_packages)

# Reorder sys.path so new directories at the front.

#new_sys_path = []

#for item in list(sys.path):
    #if item not in prev_sys_path:
        #new_sys_path.append(item)
        #sys.path.remove(item)
#
#sys.path[:0] = new_sys_path

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tayo.settings")

application = get_wsgi_application()

