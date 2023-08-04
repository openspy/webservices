import xml.etree.ElementTree as ET
class GetPurchaseHistoryHandler():
    def Handle(self, xml_tree):


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/commerce/}GetPurchaseHistoryResponse')
        result = ET.SubElement(response, '{http://gamespy.net/commerce/}GetPurchaseHistoryResult')

        status = ET.SubElement(result, '{http://gamespy.net/commerce/}status')
        code = ET.SubElement(status, '{http://gamespy.net/commerce/}code')
        code.text = str(0)

        orderpurchases_node = ET.SubElement(result, '{http://gamespy.net/commerce/}orderpurchases')
        count_node = ET.SubElement(orderpurchases_node, '{http://gamespy.net/commerce/}count')
        count_node.text = str(0)
   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')