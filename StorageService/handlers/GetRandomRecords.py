import xml.etree.ElementTree as ET
class GetRandomRecordsHandler():
    def Handle(self, httpHandler, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}GetRandomRecordsResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}GetRandomRecordsResult')
        result.text = "Success"

        values_node = ET.SubElement(response, '{http://gamespy.net/sake/}values')
   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')