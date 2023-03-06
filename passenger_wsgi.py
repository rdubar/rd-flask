import os
import sys

#PROJECT_DIR="/home/surefire/rd-flask/"
#sys.path.insert(0, PROJECT_DIR)

sys.path.append("/home/surefire/rd-flask/venv")

#sys.path.insert(0, os.path.dirname(__file__))
#sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from app import app as application

'''
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python %s\n' % sys.version.split()[0]
    response = '\n'.join([message, version])
    return [response.encode()]
'''
