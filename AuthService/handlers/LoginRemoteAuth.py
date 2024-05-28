import xml.etree.ElementTree as ET

from modules.Exceptions import AuthServiceException, MissingParameterException
from modules.ResponseCode import ResponseCodes
class LoginRemoteAuthHandler():
    def __init__(self, APIClient, CryptoWriter):
        self.APIClient = APIClient
        self.CryptoWriter = CryptoWriter
    def Handle(self, root_tree):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_result = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginRemoteAuthResult')
        
        response_code = ResponseCodes.LOGIN_RESPONSE_SUCCESS
        
        response_code_node = ET.SubElement(login_result, '{http://gamespy.net/AuthService/}responseCode') #order is important... must be after peer key and before sig
        
        try:
            request_root = root_tree.find('.//{http://gamespy.net/AuthService/}LoginRemoteAuth')
            if request_root == None:
                raise MissingParameterException()

            authtoken_node = request_root.find('{http://gamespy.net/AuthService/}authtoken')
            authtoken = authtoken_node.text

            challenge_node = request_root.find('{http://gamespy.net/AuthService/}challenge')
            challenge = challenge_node.text
            
            results = self.APIClient.TestPreAuth(authtoken, challenge)

            self.CryptoWriter.WritePeerkeyPrivate(login_result)
            self.CryptoWriter.WriteSignature(login_result, results)

        except AuthServiceException as e:
            response_code = e.response_code
        except:
            response_code = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
        finally:
            response_code_node.text = str(response_code)
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')