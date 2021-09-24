import xml.etree.ElementTree as ET
import modules.InputHelper as InputHelper

from modules.Exceptions import SAKEException 
class SearchForRecordsHandler():
    def Handle(self, httpHandler, xml_tree, storageManager):
        inputHelper = InputHelper.InputHelper()
        request_root = xml_tree.find('.//{http://gamespy.net/sake}SearchForRecords')
        
        tableid_node = request_root.find('{http://gamespy.net/sake}tableid')
        tableid = tableid_node.text

        fields = []
        fields_node = request_root.find('{http://gamespy.net/sake}fields')
        xml_fields = fields_node.findall('{http://gamespy.net/sake}string')
        for xml_field in xml_fields:
            fields.append(xml_field.text)

        filter_node = request_root.find('{http://gamespy.net/sake}filter')
        filterString = None
        if filter_node != None:
            filterString = filter_node.text

        sortString = None
        sort_node = request_root.find('{http://gamespy.net/sake}sort')
        if sort_node != None:
            sortString = sort_node.text

        queryOffset = None
        offset_node = request_root.find('{http://gamespy.net/sake}offset')
        if offset_node != None:
            queryOffset = int(offset_node.text)
        maxRows = None
        max_node = request_root.find('{http://gamespy.net/sake}max')
        if max_node != None:
            maxRows = int(max_node.text)

        resp_xml = ET.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope')
        body = ET.SubElement(resp_xml, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        response = ET.SubElement(body, '{http://gamespy.net/sake/}SearchForRecordsResponse')
        result = ET.SubElement(response, '{http://gamespy.net/sake/}SearchForRecordsResult')
        result.text = "Success"

        try:
            auth_info = inputHelper.LoadAuthInfo(request_root, storageManager)
            db_results = storageManager.SearchRecords(auth_info, tableid, fields, filterString, sortString, queryOffset, maxRows)
            result.text = "Success"

            values_node = ET.SubElement(response, '{http://gamespy.net/sake/}values')

            inputHelper.serializeResults(fields, db_results, values_node)
                        
        except SAKEException as e:
            result.text = e.result


        
        return ET.tostring(resp_xml, encoding='utf8', method='xml')