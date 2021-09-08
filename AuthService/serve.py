import http.server
import socketserver
from http import HTTPStatus
import xml.etree.ElementTree as ET
from OpenSpyAuth import OpenSpyAuth
from collections import OrderedDict
import binascii
import hashlib
import rsa
import struct, os

API_URL = os.environ.get('API_URL')
API_KEY = os.environ.get('API_KEY')
PRIVATE_KEY_PATH = os.environ.get('AUTHSERVICES_PRIVKEY_PATH')
AUTH_TOKEN_EXPIRE_TIME = int(environ.get('AUTH_TOKEN_EXPIRE_TIME'))

class Handler(http.server.SimpleHTTPRequestHandler):
    LOGIN_RESPONSE_SUCCESS = 0
    LOGIN_RESPONSE_SERVERINITFAILED = 1
    LOGIN_RESPONSE_USER_NOT_FOUND = 2
    LOGIN_RESPONSE_INVALID_PASSWORD = 3
    LOGIN_RESPONSE_INVALID_PROFILE = 4
    LOGIN_RESPONSE_UNIQUE_NICK_EXPIRED = 5
    LOGIN_RESPONSE_DB_ERROR = 6
    LOGIN_RESPONSE_SERVER_ERROR = 7
    
    APIClient = OpenSpyAuth(API_URL, API_KEY, AUTH_TOKEN_EXPIRE_TIME)
    private_key_file = open(PRIVATE_KEY_PATH,"r")
    keydata = private_key_file.read()
    auth_private_key = rsa.PrivateKey.load_pkcs1(keydata)

    def do_GET(self):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
    def handle_remoteauth_login(self, xml_tree):
        authtoken_node = xml_tree.find('{http://gamespy.net/AuthService/}authtoken')
        authtoken = authtoken_node.text

        challenge_node = xml_tree.find('{http://gamespy.net/AuthService/}challenge')
        challenge = challenge_node.text
        
        params = {"mode": "test_preauth", "challenge": challenge, "auth_token": authtoken}

        results = self.APIClient.TestPreAuth(authtoken, challenge)

        #auth stuff

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_result = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginRemoteAuthResult')

        self.WriteAuthResponse(login_result, results)

        return resp_xml
    def handle_uniquenick_login(self, xml_tree):
        #get request info
        uniquenick_node = xml_tree.find('{http://gamespy.net/AuthService/}uniquenick')
        uniquenick = uniquenick_node.text

        partnercode_node = xml_tree.find('{http://gamespy.net/AuthService/}partnercode')
        partnercode = partnercode_node.text

        namespaceid_node = xml_tree.find('{http://gamespy.net/AuthService/}namespaceid')
        namespaceid = namespaceid_node.text

        #decrypt pw
        encrypted_pass = xml_tree.find('{http://gamespy.net/AuthService/}password').find('{http://gamespy.net/AuthService/}Value')
        try:
            password = rsa.decrypt(binascii.unhexlify(encrypted_pass.text),self.auth_private_key).decode("utf-8")
        except rsa.pkcs1.DecryptionError:
            password = ""

        #def UniqueNickLogin(self, uniquenick, namespaceid, partnercode, password):
        results = self.APIClient.UniqueNickLogin(uniquenick, namespaceid, partnercode, password)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_result = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginUniqueNickResult')

        self.WriteAuthResponse(login_result, results)
        
        return resp_xml
    def handle_profile_login(self, xml_tree):
        #get request info
        nick_node = xml_tree.find('{http://gamespy.net/AuthService/}profilenick')
        nick = nick_node.text

        email_node = xml_tree.find('{http://gamespy.net/AuthService/}email')
        email = email_node.text

        partnercode_node = xml_tree.find('{http://gamespy.net/AuthService/}partnercode')
        partnercode = partnercode_node.text

        namespaceid_node = xml_tree.find('{http://gamespy.net/AuthService/}namespaceid')
        namespaceid = namespaceid_node.text

        #decrypt pw
        encrypted_pass = xml_tree.find('{http://gamespy.net/AuthService/}password').find('{http://gamespy.net/AuthService/}Value')
        try:
            password = rsa.decrypt(binascii.unhexlify(encrypted_pass.text),self.auth_private_key).decode("utf-8")
        except rsa.pkcs1.DecryptionError:
            password = ""

        #def UniqueNickLogin(self, uniquenick, namespaceid, partnercode, password):
        results = self.APIClient.NickLogin(nick, email, namespaceid, partnercode, password)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_result = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginProfileResult')

        self.WriteAuthResponse(login_result, results)
        
        return resp_xml

    def GetProfileIdFromNpTicket(self, xml_tree):
        partnercode_node = xml_tree.find('{http://gamespy.net/AuthService/}partnercode')
        partnerCode = int(partnercode_node.text)

        namespaceid_node = xml_tree.find('{http://gamespy.net/AuthService/}namespaceid')
        namespaceId = int(namespaceid_node.text)
        npTicket = xml_tree.find('{http://gamespy.net/AuthService/}npticket').find('{http://gamespy.net/AuthService/}Value').text

        return 55697 #PS3Stub account
    def handle_ps3auth_login(self, xml_tree):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        

        profileId = self.GetProfileIdFromNpTicket(xml_tree)

        auth_data = self.APIClient.GenerateAuthToken(profileId)

        print(auth_data)


        login_request = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginPs3CertResult')

        results = OrderedDict()
        results['authToken'] = auth_data["token"]
        results['partnerChallenge'] = auth_data["challenge"]

        

        self.WritePS3AuthResponse(login_request, results)
        
        return resp_xml
    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        request_body = self.rfile.read(content_length) # <--- Gets the data itself

        ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
        ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
        tree = ET.ElementTree(ET.fromstring(request_body))

        login_profile_tree = tree.find('.//{http://gamespy.net/AuthService/}LoginProfile')
        login_remoteauth_tree = tree.find('.//{http://gamespy.net/AuthService/}LoginRemoteAuth')
        login_uniquenick_tree = tree.find('.//{http://gamespy.net/AuthService/}LoginUniqueNick')
        login_ps3_tree = tree.find('.//{http://gamespy.net/AuthService/}LoginPs3Cert')

        if login_remoteauth_tree != None:
            resp = self.handle_remoteauth_login(login_remoteauth_tree)
        elif login_uniquenick_tree != None:
            resp = self.handle_uniquenick_login(login_uniquenick_tree)
        elif login_profile_tree != None:
            resp = self.handle_profile_login(login_profile_tree)
        elif login_ps3_tree != None:
            resp = self.handle_ps3auth_login(login_ps3_tree)
        else:
            resp = None


        result = None
        if resp != None:
            result = ET.tostring(resp, encoding='utf8', method='xml')            
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type','application/xml')
        else:
            result = None
            self.send_response(HTTPStatus.BAD_REQUEST)

        self.end_headers()
        if result != None:
            self.wfile.write(result)
        

    def GetResponseProfileDict(self, response):
        result = OrderedDict()

        result['partnercode'] = response['profile']['user']['partnercode']
        result['namespaceid'] = response['profile']['namespaceid']
        result['userid'] = response['profile']['userid']
        result['profileid'] = response['profile']['id']
        result['expiretime'] = response['session']['expiresAt']
        result['profilenick'] = response['profile']['nick']
        result['uniquenick'] = response['profile']['uniquenick'] or ''
        result['cdkeyhash'] = '9f86d081884c7d659a2feaa0c55ad015'.upper() #XXX: FETCH FROM DB!!

        return result
    def WriteErrorResponse(self, xml_tree, response):
        response_code_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}responseCode')
        code = self.LOGIN_RESPONSE_SERVER_ERROR
        if response != None:
            error_data = response['error']
            if error_data['class'] == 'auth':
                if error_data['name'] == 'InvalidCredentials':
                    code = self.LOGIN_RESPONSE_INVALID_PASSWORD
            elif error_data['class'] == 'common':
                if response['name'] == 'NoSuchUser':
                    code = self.LOGIN_RESPONSE_USER_NOT_FOUND
            elif error_data['class'] == 'profile':
                if error_data['name'] == 'NickInvalid':
                    code = self.LOGIN_RESPONSE_INVALID_PROFILE


        response_code_node.text = str(code)

    def WritePS3AuthResponse(self, xml_tree, response):
        response_code_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}responseCode')
        response_code_node.text = str(self.LOGIN_RESPONSE_SUCCESS)

        response_code_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}authToken')
        response_code_node.text = response["authToken"]

        response_code_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}partnerChallenge')
        response_code_node.text = response["partnerChallenge"]
    def WriteAuthResponse(self, xml_tree, response):

        if response == None or 'error' in response or 'profile' not in response:
            self.WriteErrorResponse(xml_tree, response)
            return

        peerkeyprivate_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}peerkeyprivate')
        peerkeyprivate_node.text = '0'

        response_code_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}responseCode')
        response_code_node.text = str(self.LOGIN_RESPONSE_SUCCESS)

        certificate_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}certificate')


        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'length'))
        node.text = str(0)

        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'version'))
        node.text = str(1)

        response_dict = self.GetResponseProfileDict(response)
        for k,v in response_dict.items():
            node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",k))
            node.text = str(v)


        #encrypted server data
        peerkeymodulus_node = ET.SubElement(certificate_node, '{http://gamespy.net/AuthService/}peerkeymodulus')

        rsa_modulus = str(self.auth_private_key.n)
        peerkeymodulus_node.text = rsa_modulus[-128:].upper()

        peerkeyexponent_node = ET.SubElement(certificate_node, '{http://gamespy.net/AuthService/}peerkeyexponent')
        rsa_exponent = hex(self.auth_private_key.e)
        peerkeyexponent_node.text = rsa_exponent[2:]

        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'serverdata'))
        server_data = os.urandom(128)
        node.text = binascii.hexlify(server_data).decode('utf8')

        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'signature'))
        node.text = self.generate_signature(0,1, response_dict, server_data, True)

    def generate_signature(self, length, version, auth_user_dir, server_data, use_md5):

        peerkey = {}
        rsa_exponent = hex(self.auth_private_key.e)
        peerkey['exponent'] = rsa_exponent[2:]

        rsa_modulus = str(self.auth_private_key.n)
        peerkey['modulus'] = rsa_modulus[-128:].upper()

        buffer = struct.pack("I", length)
        buffer += struct.pack("I", version)

        buffer += struct.pack("I", int(auth_user_dir['partnercode']))
        buffer += struct.pack("I", int(auth_user_dir['namespaceid']))
        buffer += struct.pack("I", int(auth_user_dir['userid']))
        buffer += struct.pack("I", int(auth_user_dir['profileid']))
        buffer += struct.pack("I", int(auth_user_dir['expiretime']))
        buffer += auth_user_dir['profilenick'].encode('utf8')
        buffer += auth_user_dir['uniquenick'].encode('utf8')
        buffer += auth_user_dir['cdkeyhash'].encode('utf8')

        buffer += binascii.unhexlify(peerkey['modulus'])
        buffer += binascii.unhexlify("0{}".format(peerkey['exponent']))
        buffer += server_data

        hash_algo = 'MD5'
        if not use_md5:
            hash_algo = 'SHA-1'
        sig_key = rsa.sign(buffer, self.auth_private_key, hash_algo)
        key = sig_key.upper()
        key = binascii.hexlify(sig_key).decode('utf8').upper()    

        return key



httpd = socketserver.TCPServer(('', int(os.environ.get('PORT'))), Handler)
httpd.serve_forever()
