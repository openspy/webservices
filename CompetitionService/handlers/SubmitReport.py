import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.DIMEParser import DIMEParser
from modules.ScReportParser import ScReportParser
from io import BytesIO
from modules.Exceptions import CompetitionException
class SubmitReportHandler():
    def Handle(self, httpHandler, input_buffer, storageManager):
        inputHelper = InputHelper.InputHelper()

        parser = DIMEParser()
        dime_data = parser.Parse(input_buffer)
        
        xml_tree = ET.ElementTree(ET.fromstring(dime_data[0].binaryData))
        request_root = xml_tree.find('.//{http://gamespy.net/competition/}SubmitReport')
        
        certificate_node = request_root.find('{http://gamespy.net/competition/}certificate')

        csid_node = request_root.find('{http://gamespy.net/competition/}csid')
        csid = csid_node.text

        ccid_node = request_root.find('{http://gamespy.net/competition/}ccid')
        ccid = ccid_node.text
        authoritative_node = request_root.find('{http://gamespy.net/competition/}authoritative')
        authoritative = int(authoritative_node.text)

        gameid_node = request_root.find('{http://gamespy.net/competition/}gameid')
        gameid = int(gameid_node.text)

        scReportParser = ScReportParser()
        report_data = scReportParser.Parse(BytesIO(dime_data[1].binaryData))

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}SubmitReportResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}SubmitReportResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')

        try:
            auth_info = inputHelper.ParseCertificate(certificate_node)
            storageManager.SubmitReport(csid, auth_info["profileid"], gameid, authoritative, report_data, ccid)
            resultcode_node.text = str(0)
        except CompetitionException as e:
            resultcode_node.text = str(e.result)
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')