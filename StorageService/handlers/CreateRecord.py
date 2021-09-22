import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.Exceptions import SAKEException 
class CreateRecordHandler():
    def Handle(self, httpHandler, xml_tree, storageManager):

        inputHelper = InputHelper.InputHelper()

        request_root = xml_tree.find('.//{http://gamespy.net/sake}CreateRecord')
        
        tableid_node = request_root.find('{http://gamespy.net/sake}tableid')
        tableid = tableid_node.text

        values_node = request_root.find('{http://gamespy.net/sake}values')
        
        record_fields = values_node.findall('{http://gamespy.net/sake}RecordField')

        record_entries = {}
        for record in record_fields:            
            entry = inputHelper.GetRecordEntry(record)
            record_entries[entry["name"]] = entry
            del entry["name"]


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake}CreateRecordResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake}CreateRecordResult')

        try:
            auth_info = inputHelper.LoadAuthInfo(request_root, storageManager)
            recordId = storageManager.Create(auth_info, tableid, record_entries)
            result.text = "Success"
            recordid_node = ET.SubElement(response, '{http://gamespy.net/sake}recordid')
            recordid_node.text = str(recordId)
        except SAKEException as e:
            result.text = e.result

   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')