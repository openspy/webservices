import xml.etree.ElementTree as ET
class GetStoreAvailabilityHandler():
    def Handle(self, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/commerce/}GetStoreAvailabilityResponse')
        result = ET.SubElement(response, '{http://gamespy.net/commerce/}GetStoreAvailabilityResult')

        status = ET.SubElement(result, '{http://gamespy.net/commerce/}status')
        code = ET.SubElement(status, '{http://gamespy.net/commerce/}code')
        code.text = str(0)

        recordid_node = ET.SubElement(result, '{http://gamespy.net/commerce/}storestatusid')
        recordid_node.text = str(10)
   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')