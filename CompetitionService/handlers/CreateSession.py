import xml.etree.ElementTree as ET
class CreateSessionHandler():
    def Handle(self, httpHandler, xml_tree):
        #request_root = xml_tree.find('.//{http://gamespy.net/competition/}CreateSession')


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}CreateSessionResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}CreateSessionResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')
        resultcode_node.text = str(0)

        csid_node =  ET.SubElement(session_result_node, '{http://gamespy.net/competition/}csid')
        csid_node.text = str(111)

        ccid_node =  ET.SubElement(session_result_node, '{http://gamespy.net/competition/}ccid')
        ccid_node.text = str(111)


        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')