
import os
import sys

sys.path.append("/home/surefire/rd-flask/venv")

#sys.path.insert(0, os.path.dirname(__file__))


from app import app as application

'''
def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    message = 'It works!\n'
    version = 'Python %s\n' % sys.version.split()[0]
    response = '\n'.join([message, version])
    return [response.encode()]
'''