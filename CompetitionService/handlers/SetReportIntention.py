import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.Exceptions import CompetitionException, MissingParameterException
class SetReportIntentionHandler():
    def Handle(self, xml_tree, storageManager):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}SetReportIntentionResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}SetReportIntentionResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')
        
        try:
            inputHelper = InputHelper.InputHelper()

            request_root = xml_tree.find('.//{http://gamespy.net/competition/}SetReportIntention')
            if request_root == None:
                raise MissingParameterException()
            
            certificate_node = request_root.find('{http://gamespy.net/competition/}certificate')
            if certificate_node == None:
                raise MissingParameterException()

            csid_node = request_root.find('{http://gamespy.net/competition/}csid')
            if csid_node == None:
                raise MissingParameterException()
            csid = csid_node.text

            ccid_node = request_root.find('{http://gamespy.net/competition/}ccid')
            if ccid_node == None:
                raise MissingParameterException()
            authoritative_node = request_root.find('{http://gamespy.net/competition/}authoritative')
            if authoritative_node == None:
                raise MissingParameterException()
            authoritative = int(authoritative_node.text)

            gameid_node = request_root.find('{http://gamespy.net/competition/}gameid')
            if gameid_node == None:
                raise MissingParameterException()
            gameid = int(gameid_node.text)

            auth_info = inputHelper.ParseCertificate(certificate_node)
            ccid = storageManager.SetReportIntention(csid, auth_info["profileid"], gameid, authoritative)
            ccid_node =  ET.SubElement(session_result_node, '{http://gamespy.net/competition/}ccid')
            ccid_node.text = ccid
            resultcode_node.text = str(0)
        except CompetitionException as e:
            resultcode_node.text = str(e.result)



        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')