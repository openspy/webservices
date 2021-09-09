import xml.etree.ElementTree as ET
class RateRecordHandler():
    def Handle(self, httpHandler, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}RateRecordResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}RateRecordResult')
        result.text = "Success"

        recordid_node = ET.SubElement(result, '{http://gamespy.net/sake/}numRatings')
        recordid_node.text = str(0)

        recordid_node = ET.SubElement(result, '{http://gamespy.net/sake/}averageRating')
        recordid_node.text = str(0.0)

   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')