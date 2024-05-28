import xml.etree.ElementTree as ET

from modules.Exceptions import AuthServiceException, MissingParameterException
from modules.ResponseCode import ResponseCodes
class LoginPs3CertHandler():
    def __init__(self, APIClient):
        self.APIClient = APIClient
    def Handle(self, root_tree):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        login_result = ET.SubElement(body, '{http://gamespy.net/AuthService/}LoginPs3CertResult')
        
        response_code = ResponseCodes.LOGIN_RESPONSE_SUCCESS
        
        response_code_node = ET.SubElement(login_result, '{http://gamespy.net/AuthService/}responseCode') #order is important... must be after peer key and before sig
        
        try:
            request_root = root_tree.find('.//{http://gamespy.net/AuthService/}LoginPs3Cert')
            if request_root == None:
                raise MissingParameterException()

            profileid = self.GetProfileIdFromNpTicket(request_root)

            auth_data = self.APIClient.GenerateAuthToken(profileid)
            
            auth_token_node = ET.SubElement(login_result, '{http://gamespy.net/AuthService/}authToken')
            auth_token_node.text = auth_data["token"]

            partner_challenge_node = ET.SubElement(login_result, '{http://gamespy.net/AuthService/}partnerChallenge')
            partner_challenge_node.text = auth_data["challenge"]

        except AuthServiceException as e:
            response_code = e.response_code
        except:
            response_code = ResponseCodes.LOGIN_RESPONSE_SERVER_ERROR
        finally:
            response_code_node.text = str(response_code)
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')
    def GetProfileIdFromNpTicket(self, xml_tree):
        # partnercode_node = xml_tree.find('{http://gamespy.net/AuthService/}partnercode')
        # partnerCode = int(partnercode_node.text)

        # namespaceid_node = xml_tree.find('{http://gamespy.net/AuthService/}namespaceid')
        # namespaceId = int(namespaceid_node.text)
        # npTicket = xml_tree.find('{http://gamespy.net/AuthService/}npticket').find('{http://gamespy.net/AuthService/}Value').text

        return 55697 #PS3Stub account