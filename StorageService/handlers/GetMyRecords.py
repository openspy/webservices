import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper

from modules.Exceptions import SAKEException 
class GetMyRecordsHandler():
    def Handle(self, httpHandler, xml_tree, storageManager):
        inputHelper = InputHelper.InputHelper()

        request_root = xml_tree.find('.//{http://gamespy.net/sake}GetMyRecords')
        
        tableid_node = request_root.find('{http://gamespy.net/sake}tableid')
        tableid = tableid_node.text

        fields = []
        fields_node = request_root.find('{http://gamespy.net/sake}fields')
        xml_fields = fields_node.findall('{http://gamespy.net/sake}string')
        for xml_field in xml_fields:
            fields.append(xml_field.text)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}GetMyRecordsResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}GetMyRecordsResult')


        try:
            auth_info = inputHelper.LoadAuthInfo(request_root, storageManager)
            db_results = storageManager.FindAllRecordsByProfileid(auth_info, tableid)
            result.text = "Success"

            values_node = ET.SubElement(response, '{http://gamespy.net/sake/}values')

            inputHelper.serializeResults(fields, db_results, values_node)
                        
        except SAKEException as e:
            result.text = e.result


        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')