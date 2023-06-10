import os

from router import router

from puppy.http.server import HTTPServer
from puppy.simple.process import execute

# Path to certificate
path = "/opt/ssl.pem"

# Make sure certificate exists
if not os.path.exists(path):
    # Create new certificate
    execute("openssl req -new -x509 -days 3650 -nodes -out %s -keyout %s -subj /" % (path, path))

# Create new server
server = HTTPServer(router)
server.context.load_cert_chain(certfile=path, keyfile=path)
