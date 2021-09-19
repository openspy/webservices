import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper
from modules.Exceptions import SAKEException 
class DeleteRecordHandler():
    def Handle(self, httpHandler, xml_tree, storageManager):

        inputHelper = InputHelper.InputHelper()

        request_root = xml_tree.find('.//{http://gamespy.net/sake}DeleteRecord')
        
        tableid_node = request_root.find('{http://gamespy.net/sake}tableid')
        tableid = tableid_node.text


        recordid_node = request_root.find('{http://gamespy.net/sake}recordid')
        recordid = int(recordid_node.text)


        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}DeleteRecordResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}DeleteRecordResult')

        try:
            auth_info = inputHelper.LoadAuthInfo(request_root, storageManager)
            storageManager.Delete(auth_info, tableid, recordid)
            result.text = "Success"
        except SAKEException as e:
            result.text = e.result
   
        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')