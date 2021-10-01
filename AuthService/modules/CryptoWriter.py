import xml.etree.ElementTree as ET
import struct, os
import binascii
import hashlib
import rsa
from collections import OrderedDict
from modules.ResponseCode import ResponseCodes
class CryptoWriter():
    def __init__(self, auth_private_key, peer_private_key):
        self.auth_private_key = auth_private_key
        self.peer_private_key = peer_private_key
        self.peerkey_data = self.GetPeerKeyData()
    def WritePeerkeyPrivate(self, xml_tree):
        peerkeyprivate_node = ET.SubElement(xml_tree, '{http://gamespy.net/AuthService/}peerkeyprivate')
        peerkeyprivate_node.text = self.peerkey_data['private']
    def GetPeerKeyData(self):
        peerkey_data = {}
        rsa_exponent = hex(self.peer_private_key.e)


        #always output even hex string
        exponent = "{}{}".format("0" if len(rsa_exponent[2:]) % 2 else "", rsa_exponent[2:])
        peerkey_data['exponent'] = exponent

        rsa_modulus = hex(self.peer_private_key.n)
        modulus = "{}{}".format("0" if len(rsa_modulus[2:]) % 2 else "", rsa_modulus[2:])
        peerkey_data['modulus'] = modulus

        private_data = hex(self.peer_private_key.d)
        private = "{}{}".format("0" if len(private_data[2:]) % 2 else "", private_data[2:])
        peerkey_data['private'] = private
        return peerkey_data
    def WriteSignature(self, xml_tree, response):

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
        peerkeymodulus_node.text = self.peerkey_data['modulus']

        peerkeyexponent_node = ET.SubElement(certificate_node, '{http://gamespy.net/AuthService/}peerkeyexponent')
        peerkeyexponent_node.text = self.peerkey_data['exponent']

        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'serverdata'))
        server_data = os.urandom(128)
        node.text = binascii.hexlify(server_data).decode('utf8')

        node = ET.SubElement(certificate_node, '{}{}'.format("{http://gamespy.net/AuthService/}",'signature'))
        node.text = self.generate_signature(0,1, response_dict, server_data, True, self.peerkey_data)
    def generate_signature(self, length, version, auth_user_dir, server_data, use_md5, peerkey_data):
        buffer = struct.pack("I", length)
        buffer += struct.pack("I", version)

        if 'partnercode' in auth_user_dir and auth_user_dir['partnercode'] != None:
            buffer += struct.pack("I", int(auth_user_dir['partnercode']))

        if 'namespaceid' in auth_user_dir and auth_user_dir['namespaceid'] != None:
            buffer += struct.pack("I", int(auth_user_dir['namespaceid']))

        if 'userid' in auth_user_dir and auth_user_dir['userid'] != None:
            buffer += struct.pack("I", int(auth_user_dir['userid']))

        if 'profileid' in auth_user_dir and auth_user_dir['profileid'] != None:
            buffer += struct.pack("I", int(auth_user_dir['profileid']))

        if 'expiretime' in auth_user_dir and auth_user_dir['expiretime'] != None:
            buffer += struct.pack("I", int(auth_user_dir['expiretime']))

        if auth_user_dir['profilenick'] != None:
            buffer += auth_user_dir['profilenick'].encode('utf8')

        if auth_user_dir['uniquenick'] != None:
            buffer += auth_user_dir['uniquenick'].encode('utf8')

        if auth_user_dir['cdkeyhash'] != None:
            buffer += auth_user_dir['cdkeyhash'].encode('utf8')

        if 'modulus' in peerkey_data and peerkey_data['modulus'] != None:
            buffer += binascii.unhexlify(peerkey_data['modulus'])
        if 'exponent' in peerkey_data and peerkey_data['exponent'] != None:
            buffer += binascii.unhexlify(peerkey_data['exponent'])
        if server_data != None:
            buffer += server_data

        #print("hash: {}\n".format(hashlib.md5(buffer).hexdigest()))

        hash_algo = 'MD5'
        if not use_md5:
            hash_algo = 'SHA-1'
        sig_key = rsa.sign(buffer, self.auth_private_key, hash_algo)
        key = sig_key.upper()
        key = binascii.hexlify(sig_key).decode('utf8').upper()    

        return key
    def GetResponseProfileDict(self, response):
        result = OrderedDict()

        result['partnercode'] = response['profile']['user']['partnercode']
        result['namespaceid'] = response['profile']['namespaceid']
        result['userid'] = response['profile']['userid']
        result['profileid'] = response['profile']['id']
        result['expiretime'] = response['session']['expiresAt']
        result['profilenick'] = response['profile']['nick']
        result['uniquenick'] = response['profile']['uniquenick'] or ''
        result['cdkeyhash'] = 'd41d8cd98f00b204e9800998ecf8427e'.upper() #XXX: FETCH FROM DB!!

        return result
    def DecryptPassword(self, encrypted_password):
        password = None
        try:
            password = rsa.decrypt(binascii.unhexlify(encrypted_password),self.auth_private_key).decode("utf-8")
        except rsa.pkcs1.DecryptionError:
            pass
        return password
