import rsa
import struct, os
import binascii

from modules.Exceptions import InvalidCertificateException
class InputHelper():
    AUTHSERVICES_PUBKEY_PATH = os.environ.get('AUTHSERVICES_PUBKEY_PATH')
    authservices_pubkey_file = open(AUTHSERVICES_PUBKEY_PATH,"r")
    authservices_pubkey_keydata = authservices_pubkey_file.read()
    authservices_pubkey = rsa.PublicKey.load_pkcs1(authservices_pubkey_keydata)

    def ParseCertificate(self, cert_node):
        auth_data = {}

        profileid_node = cert_node.find('{http://gamespy.net/competition/}profileid')
        profileid = int(profileid_node.text)
        auth_data["profileid"] = profileid


        userid_node = cert_node.find('{http://gamespy.net/competition/}userid')
        userid = int(userid_node.text)
        auth_data["userid"] = userid

        partnercode_node = cert_node.find('{http://gamespy.net/competition/}partnercode')
        partnercode = int(partnercode_node.text)
        auth_data["partnercode"] = partnercode


        namespaceid_node = cert_node.find('{http://gamespy.net/competition/}namespaceid')
        namespaceid = int(namespaceid_node.text)
        auth_data["namespaceid"] = namespaceid

        expiretime_node = cert_node.find('{http://gamespy.net/competition/}expiretime')
        expiretime = int(expiretime_node.text)
        auth_data["expiretime"] = expiretime

        profilenick_node = cert_node.find('{http://gamespy.net/competition/}profilenick')
        auth_data["profilenick"] = profilenick_node.text

        uniquenick_node = cert_node.find('{http://gamespy.net/competition/}uniquenick')
        auth_data["uniquenick"] = uniquenick_node.text

        cdkeyhash_node = cert_node.find('{http://gamespy.net/competition/}cdkeyhash')
        auth_data["cdkeyhash"] = cdkeyhash_node.text


        peerkey_data = {}
        modulus_node = cert_node.find('{http://gamespy.net/competition/}peerkeymodulus')
        peerkey_data["modulus"] = modulus_node.text

        exponent_node = cert_node.find('{http://gamespy.net/competition/}peerkeyexponent')
        peerkey_data["exponent"] = exponent_node.text

        serverdata_node = cert_node.find('{http://gamespy.net/competition/}serverdata')
        serverdata = binascii.unhexlify(serverdata_node.text)

        signature_node = cert_node.find('{http://gamespy.net/competition/}signature')
        signature = binascii.unhexlify(signature_node.text)

        length_node = cert_node.find('{http://gamespy.net/competition/}length')
        length = int(length_node.text)

        version_node = cert_node.find('{http://gamespy.net/competition/}version')
        version = int(version_node.text)

        try:
            self.verify_signature(length, version, auth_data, serverdata, True, peerkey_data, signature)
        except rsa.pkcs1.VerificationError:
            raise InvalidCertificateException()
        return auth_data

    def verify_signature(self, length, version, auth_user_dir, server_data, use_md5, peerkey_data, signature):
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

        buffer += binascii.unhexlify(peerkey_data['modulus'])
        buffer += binascii.unhexlify(peerkey_data['exponent'])
        buffer += server_data

        hash_algo = 'MD5'
        if not use_md5:
            hash_algo = 'SHA-1'
        rsa.verify(buffer, signature, self.authservices_pubkey)