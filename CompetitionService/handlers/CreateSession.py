import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.Exceptions import CompetitionException
class CreateSessionHandler():
    def Handle(self, httpHandler, xml_tree, storageManager):
        inputHelper = InputHelper.InputHelper()

        request_root = xml_tree.find('.//{http://gamespy.net/competition/}CreateSession')
        
        certificate_node = request_root.find('{http://gamespy.net/competition/}certificate')

        gameid_node = request_root.find('{http://gamespy.net/competition/}gameid')
        gameid = int(gameid_node.text)


        platformid_node = request_root.find('{http://gamespy.net/competition/}platformid')
        platformid = None
        if platformid_node != None:
            platformid = int(platformid_node.text)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}CreateSessionResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}CreateSessionResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')

        try:
            auth_info = inputHelper.ParseCertificate(certificate_node)
            connection_session_id = storageManager.CreateSession(auth_info["profileid"], gameid, platformid, False)
            csid_node =  ET.SubElement(session_result_node, '{http://gamespy.net/competition/}csid')
            csid_node.text = connection_session_id

            ccid = storageManager.SetReportIntention(connection_session_id, auth_info["profileid"], gameid, False)

            ccid_node =  ET.SubElement(session_result_node, '{http://gamespy.net/competition/}ccid')
            ccid_node.text = ccid

            resultcode_node.text = str(0)
        except CompetitionException as e:
            resultcode_node.text = str(e.result)




        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')