import xml.etree.ElementTree as ET
class GetRecordLimitHandler():
    def Handle(self, httpHandler, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}GetRecordLimitResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}GetRecordLimitResult')
        result.text = "Success"

        limit_node = ET.SubElement(response, '{http://gamespy.net/sake/}limitPerOwner')
        limit_node.text = str(5000)

        numowned_node = ET.SubElement(response, '{http://gamespy.net/sake/}numOwned')
        numowned_node.text = str(1)

        return ET.tostring(resp_xml, encoding='utf8', method='xml')