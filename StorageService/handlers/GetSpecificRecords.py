import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper

from modules.Exceptions import SAKEException 
class GetSpecificRecordsHandler():
    def Handle(self, xml_tree, storageManager):
        inputHelper = InputHelper.InputHelper()

        request_root = xml_tree.find('.//{http://gamespy.net/sake}GetSpecificRecords')
        
        tableid_node = request_root.find('{http://gamespy.net/sake}tableid')
        tableid = tableid_node.text

        recordids = []
        recordids_node = request_root.find('{http://gamespy.net/sake}recordids')
        xml_recordids = recordids_node.findall('{http://gamespy.net/sake}int')
        for xml_recordid in xml_recordids:
            recordids.append(int(xml_recordid.text))

        fields = []
        fields_node = request_root.find('{http://gamespy.net/sake}fields')
        xml_fields = fields_node.findall('{http://gamespy.net/sake}string')
        for xml_field in xml_fields:
            fields.append(xml_field.text)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}GetSpecificRecordsResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}GetSpecificRecordsResult')

        try:
            auth_info = inputHelper.LoadAuthInfo(request_root, storageManager)
            
            db_results = storageManager.FindAllRecordsByIDs(auth_info, tableid, recordids)
            result.text = "Success"

            values_node = ET.SubElement(response, '{http://gamespy.net/sake/}values')
            inputHelper.serializeResults(fields, db_results, values_node)
        except SAKEException as e:
            result.text = e.result
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')