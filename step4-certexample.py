import ssl
import socket
import OpenSSL

website = 'google.com'
ctx = ssl.create_default_context()
connection = socket.create_connection((website, 443))
s = ctx.wrap_socket(connection, server_hostname=website)
cert = s.getpeercert(True)
s.close()
cert = ssl.DER_cert_to_PEM_cert(cert)
x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert) 
print(x509)
