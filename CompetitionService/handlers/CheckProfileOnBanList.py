import xml.etree.ElementTree as ET
from modules.Exceptions import MissingParameterException
class CheckProfileOnBanListHandler():
    def Handle(self, xml_tree, storageManager):

        request_root = xml_tree.find('.//{http://gamespy.net/competition/}CheckProfileOnBanList')
        if request_root == None:
            raise MissingParameterException()

        profileid_node = request_root.find('{http://gamespy.net/competition/}HostProfileId')
        if profileid_node == None:
            raise MissingParameterException()
        profileid = profileid_node.text

        platformid_node = request_root.find('{http://gamespy.net/competition/}HostPlatformId')
        platformid = None
        if profileid_node != None:
            platformid = platformid_node.text
        

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}CheckProfileOnBanListResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}CheckProfileOnBanListResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')
        resultcode_node.text = str(0)

        userconfig_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}UserConfig')

        profileid_node = ET.SubElement(userconfig_node, '{http://gamespy.net/competition/}ProfileID')
        profileid_node.text = profileid

        platformid_node = ET.SubElement(userconfig_node, '{http://gamespy.net/competition/}PlatformID')
        platformid_node.text = platformid

        isbanned_node = ET.SubElement(userconfig_node, '{http://gamespy.net/competition/}IsBanned')
        isbanned_node.text = 'false'

        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')