import xml.etree.ElementTree as ET
from dateutil import parser
from modules.Exceptions import LoginTicketInvalidException 
from modules.ReservedKeys import IsReservedKey
class InputHelper():
    def LoadAuthInfo(self, xml_tree, storageManager):
        auth_info = {}
        lt_node = xml_tree.find('{http://gamespy.net/sake}loginTicket')
        if lt_node != None:
            profileId = storageManager.GetProfileIdFromLoginTicket(lt_node.text)
            if profileId == None:
                raise LoginTicketInvalidException()    
            auth_info["profileId"] = profileId
        else:
            raise LoginTicketInvalidException()
        gameid_node = xml_tree.find('{http://gamespy.net/sake}gameid')
        auth_info["gameid"] = int(gameid_node.text)

        return auth_info

    def GetRecordEntry(self, record):
        data = {}
        name_node = record.find('{http://gamespy.net/sake}name')
        data["name"] = name_node.text

        value_node = record.find('{http://gamespy.net/sake}value')

        typed_value_node = value_node.find('{http://gamespy.net/sake}asciiStringValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = value_node.text
            data["type"] = "ascii"

        typed_value_node = value_node.find('{http://gamespy.net/sake}unicodeStringValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = value_node.text
            data["type"] = "unicode"


        typed_value_node = value_node.find('{http://gamespy.net/sake}byteValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = int(value_node.text)
            data["type"] = "byte"

        typed_value_node = value_node.find('{http://gamespy.net/sake}shortValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = int(value_node.text)
            data["type"] = "short"

        typed_value_node = value_node.find('{http://gamespy.net/sake}intValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = int(value_node.text)
            data["type"] = "int"

        typed_value_node = value_node.find('{http://gamespy.net/sake}floatValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = float(value_node.text)
            data["type"] = "float"

        typed_value_node = value_node.find('{http://gamespy.net/sake}booleanValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = bool(value_node.text)
            data["type"] = "boolean"

        typed_value_node = value_node.find('{http://gamespy.net/sake}dateAndTimeValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = parser.parse(value_node.text)
            data["type"] = "datetime"

        typed_value_node = value_node.find('{http://gamespy.net/sake}binaryDataValue')
        if typed_value_node != None:
            value_node = typed_value_node.find('{http://gamespy.net/sake}value')
            data["value"] = value_node.text
            data["type"] = "binary"
        
        return data
    def WriteLiteralIntField(self, xml_tree, key, record):
        recordfield_node = ET.SubElement(xml_tree, '{http://gamespy.net/sake/}RecordValue')

        name_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}name')
        name_node.text = key

        value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}intValue')


        value_node = ET.SubElement(value_data_node, '{http://gamespy.net/sake/}value')
        value_node.text = str(record[key])
    def WriteField(self, xml_tree, field, name):
        recordfield_node = ET.SubElement(xml_tree, '{http://gamespy.net/sake/}RecordValue')

        name_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}name')
        name_node.text = name

        if field["type"] == "ascii":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}asciiStringValue')
        elif field["type"] == "unicode":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}unicodeStringValue')
        elif field["type"] == "byte":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}byteValue')
        elif field["type"] == "short":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}shortValue')
        elif field["type"] == "int":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}intValue')
        elif field["type"] == "float":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}floatValue')
        elif field["type"] == "boolean":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}booleanValue')
        elif field["type"] == "datetime":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}dateAndTimeValue')
            field["value"] = "{}Z".format(field["value"]) #lame hack due to python not outputing timezone info
        elif field["type"] == "binary":
            value_data_node = ET.SubElement(recordfield_node, '{http://gamespy.net/sake/}binaryDataValue')
        

        value_node = ET.SubElement(value_data_node, '{http://gamespy.net/sake/}value')
        value_node.text = str(field["value"])

    def serializeResults(self, fields, db_results, values_node):
        for result in db_results:
            result_node = ET.SubElement(values_node, '{http://gamespy.net/sake/}ArrayOfRecordValue')
            for field in fields:
                if IsReservedKey(field):
                    self.WriteLiteralIntField(result_node, field, result)
                else:
                    if field in result["data"]:
                        self.WriteField(result_node, result["data"][field], field)

                    
