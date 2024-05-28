import xml.etree.ElementTree as ET
import os


import traceback
import rsa
from modules.OpenSpyAuth import OpenSpyAuth
from handlers.LoginUniqueNick import LoginUniqueNickHandler
from handlers.LoginProfile import LoginProfileHandler
from handlers.LoginRemoteAuth import LoginRemoteAuthHandler
from handlers.LoginPs3Cert import LoginPs3CertHandler
from modules.CryptoWriter import CryptoWriter

API_URL = os.environ.get('API_URL')
API_KEY = os.environ.get('API_KEY')
PRIVATE_KEY_PATH = os.environ.get('AUTHSERVICES_PRIVKEY_PATH')
AUTH_TOKEN_EXPIRE_TIME = int(os.environ.get('AUTH_TOKEN_EXPIRE_TIME'))
PEERKEY_KEY_PATH = os.environ.get('AUTHSERVICES_PEERKEY_KEY_PATH')


private_key_file = open(PRIVATE_KEY_PATH,"r")
keydata = private_key_file.read()
auth_private_key = rsa.PrivateKey.load_pkcs1(keydata)

peerkey_private_key_file = open(PEERKEY_KEY_PATH,"r")
peerkey_keydata = peerkey_private_key_file.read()
peerkey_private_key = rsa.PrivateKey.load_pkcs1(peerkey_keydata)

cryptoWriter = CryptoWriter(auth_private_key, peerkey_private_key)

APIClient = OpenSpyAuth(API_URL, API_KEY, AUTH_TOKEN_EXPIRE_TIME)
loginUniqueNickHandler = LoginUniqueNickHandler(APIClient, cryptoWriter)
loginProfileHandler = LoginProfileHandler(APIClient, cryptoWriter)
loginRemoteAuthHandler = LoginRemoteAuthHandler(APIClient, cryptoWriter)
loginPs3CertHandler = LoginPs3CertHandler(APIClient)

def handle_post(environ, start_response):
        ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
        ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
        try:
            if "HTTP_SOAPACTION" not in environ:
                start_response('400 BAD REQUEST', [])
                return None
            content_length = int(environ['CONTENT_LENGTH']) # <--- Gets the size of data
            request_type = environ['HTTP_SOAPACTION']

            result = None
            request_body = environ['wsgi.input'].read(content_length) # <--- Gets the data itself

            try:
                request_body = request_body.decode('utf8').replace("<s1", "<ns1").replace("</s1", "</ns1") #weird ps3 fix
                xml_tree = ET.ElementTree(ET.fromstring(request_body))
            except:
                xml_tree = None

            handler = None
            if request_type == "\"http://gamespy.net/AuthService/LoginUniqueNick\"":
                handler = loginUniqueNickHandler
            elif request_type == "\"http://gamespy.net/AuthService/LoginProfile\"":
                handler = loginProfileHandler
            elif request_type == "\"http://gamespy.net/AuthService/LoginRemoteAuth\"":
                handler = loginRemoteAuthHandler
            elif request_type == "\"http://gamespy.net/AuthService/LoginPs3Cert\"":
                handler = loginPs3CertHandler
                
            if handler != None:
                result = handler.Handle(xml_tree)
            else:
                result = None
            if result == None:
                start_response('400 BAD REQUEST', [('Content-Type','application/xml')])
            else:
                start_response('200 OK', [('Content-Type','application/xml'), ('Content-Length',str(len(result)))])
                return result
        except:
            traceback.print_exc()
            start_response('500 INTERNAL SERVER ERROR', [])

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        start_response('404 NOT FOUND', [])
    elif environ['REQUEST_METHOD'] == 'POST':
        result = handle_post(environ, start_response)
        if result != None:
            yield result