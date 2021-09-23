import xml.etree.ElementTree as ET
class SubmitReportHandler():
    def Handle(self, httpHandler, input_buffer):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}SubmitReportResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}SubmitReportResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')
        resultcode_node.text = str(0)
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')