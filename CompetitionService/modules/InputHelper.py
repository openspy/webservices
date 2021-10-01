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
        if profileid_node == None:
            raise InvalidCertificateException()
        profileid = int(profileid_node.text)
        auth_data["profileid"] = profileid


        userid_node = cert_node.find('{http://gamespy.net/competition/}userid')
        if userid_node == None:
            raise InvalidCertificateException()
        userid = int(userid_node.text)
        auth_data["userid"] = userid

        partnercode_node = cert_node.find('{http://gamespy.net/competition/}partnercode')
        if partnercode_node == None:
            raise InvalidCertificateException()
        partnercode = int(partnercode_node.text)
        auth_data["partnercode"] = partnercode


        namespaceid_node = cert_node.find('{http://gamespy.net/competition/}namespaceid')
        if namespaceid_node == None:
            raise InvalidCertificateException()
        namespaceid = int(namespaceid_node.text)
        auth_data["namespaceid"] = namespaceid

        expiretime_node = cert_node.find('{http://gamespy.net/competition/}expiretime')
        if expiretime_node == None:
            raise InvalidCertificateException()
        expiretime = int(expiretime_node.text)
        auth_data["expiretime"] = expiretime

        profilenick_node = cert_node.find('{http://gamespy.net/competition/}profilenick')
        if profilenick_node == None:
            raise InvalidCertificateException()
        auth_data["profilenick"] = profilenick_node.text

        uniquenick_node = cert_node.find('{http://gamespy.net/competition/}uniquenick')
        if uniquenick_node == None:
            raise InvalidCertificateException()
        auth_data["uniquenick"] = uniquenick_node.text

        cdkeyhash_node = cert_node.find('{http://gamespy.net/competition/}cdkeyhash')
        if cdkeyhash_node == None:
            raise InvalidCertificateException()
        auth_data["cdkeyhash"] = cdkeyhash_node.text


        peerkey_data = {}
        modulus_node = cert_node.find('{http://gamespy.net/competition/}peerkeymodulus')
        if modulus_node == None:
            raise InvalidCertificateException()
        peerkey_data["modulus"] = modulus_node.text

        exponent_node = cert_node.find('{http://gamespy.net/competition/}peerkeyexponent')
        if exponent_node == None:
            raise InvalidCertificateException()
        peerkey_data["exponent"] = exponent_node.text

        serverdata_node = cert_node.find('{http://gamespy.net/competition/}serverdata')
        if serverdata_node == None:
            raise InvalidCertificateException()
        serverdata = binascii.unhexlify(serverdata_node.text)

        signature_node = cert_node.find('{http://gamespy.net/competition/}signature')
        if signature_node == None:
            raise InvalidCertificateException()
        signature = binascii.unhexlify(signature_node.text)

        length_node = cert_node.find('{http://gamespy.net/competition/}length')
        if length_node == None:
            raise InvalidCertificateException()
        length = int(length_node.text)

        version_node = cert_node.find('{http://gamespy.net/competition/}version')
        if version_node == None:
            raise InvalidCertificateException()
        version = int(version_node.text)

        try:
            self.verify_signature(length, version, auth_data, serverdata, True, peerkey_data, signature)
        except rsa.pkcs1.VerificationError:
            raise InvalidCertificateException()
        return auth_data

    def verify_signature(self, length, version, auth_user_dir, server_data, use_md5, peerkey_data, signature):
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

        hash_algo = 'MD5'
        if not use_md5:
            hash_algo = 'SHA-1'
        rsa.verify(buffer, signature, self.authservices_pubkey)