import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.DIMEParser import DIMEParser
from modules.ScReportParser import ScReportParser
from io import BytesIO
from modules.Exceptions import CompetitionException, MissingParameterException
class SubmitReportHandler():
    def Handle(self, httpHandler, input_buffer, storageManager):
        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/competition/}SubmitReportResponse')

        session_result_node = ET.SubElement(response, '{http://gamespy.net/competition/}SubmitReportResult')
        resultcode_node = ET.SubElement(session_result_node, '{http://gamespy.net/competition/}result')

        try:
            inputHelper = InputHelper.InputHelper()

            parser = DIMEParser()
            dime_data = parser.Parse(input_buffer)
            if dime_data == None:
                raise MissingParameterException()
            
            xml_tree = ET.ElementTree(ET.fromstring(dime_data[0].binaryData))
            request_root = xml_tree.find('.//{http://gamespy.net/competition/}SubmitReport')
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
            ccid = ccid_node.text
            authoritative_node = request_root.find('{http://gamespy.net/competition/}authoritative')
            if authoritative_node == None:
                raise MissingParameterException()
            authoritative = int(authoritative_node.text)

            gameid_node = request_root.find('{http://gamespy.net/competition/}gameid')
            if gameid_node == None:
                raise MissingParameterException()
            gameid = int(gameid_node.text)

            scReportParser = ScReportParser()
            report_data = scReportParser.Parse(BytesIO(dime_data[1].binaryData))
            if report_data == None:
                raise MissingParameterException()
            
            auth_info = inputHelper.ParseCertificate(certificate_node)
            storageManager.SubmitReport(csid, auth_info["profileid"], gameid, authoritative, report_data, ccid)
            resultcode_node.text = str(0)
        except CompetitionException as e:
            resultcode_node.text = str(e.result)
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')