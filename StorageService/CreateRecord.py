import xml.etree.ElementTree as ET
class CreateRecordHandler():
    def Handle(self, httpHandler, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}GetSpecificRecordsResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}GetSpecificRecordsResult')
        result.text = "Success"

        recordid_node = ET.SubElement(result, '{http://gamespy.net/sake/}recordid')
        recordid_node.text = str(123)

   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')