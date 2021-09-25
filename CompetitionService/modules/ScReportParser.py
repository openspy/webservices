import struct
import binascii
class ScDataType():
    ScDataType_Int32 = 0
    ScDataType_Int16 = 1
    ScDataType_Byte = 2
    ScDataType_String = 3
    ScDataType_Float = 4
    ScDataType_Int64 = 5
class ScReportParser():
    CONNECTION_ID_LEN = 16
    AUTH_DATA_LEN = 16
    def Parse(self, report_file):
        return self.ParseScReportData(report_file)
    def ParseRosterData(self, report_file, playerCount):
        currentIndex = 0
        results = []
        while currentIndex < playerCount:
            connectionId = binascii.hexlify(report_file.read(self.CONNECTION_ID_LEN)).decode('ascii')
            team_index = struct.unpack(">I", report_file.read(4))[0]
            results.append({'connection_id': connectionId, 'team': team_index})
            currentIndex += 1
        return results
    def ParseAuthData(self, report_file, playerCount):
        currentIndex = 0
        results = []
        while currentIndex < playerCount:
            authData = binascii.hexlify(report_file.read(self.AUTH_DATA_LEN)).decode('ascii')
            results.append({'auth_data': authData})
            currentIndex += 1
        return results
    def ParseResultsSection(self, report_file, playerCount, teamCount):
        currentIndex = 0
        results = {}
        player_results = []
        team_results = []
        while currentIndex < playerCount:
            player_result = struct.unpack(">I", report_file.read(4))[0]
            player_results.append({'result': player_result})
            currentIndex += 1
        currentIndex = 0
        while currentIndex < teamCount:
            team_result = struct.unpack(">I", report_file.read(4))[0]
            team_results.append({'result': team_result})
            currentIndex += 1

        results["player_results"] = player_results
        results["team_results"] = team_results
        return results

    def decode_from_7bit(self, file_stream):
        result = 0

        index = 0
        while True:
            char = file_stream.read(1)
            byte_value = ord(char)
            result |= (byte_value & 0x7f) << (7 * index)
            if byte_value & 0x80 == 0 or index >= 5:
                break
            index += 1
        return result
    def ParseSectionData(self, report_file, keyCount):
        index = 0
        results = {}
        while index < keyCount:
            key_id = struct.unpack(">H", report_file.read(2))[0]
            key_type = struct.unpack(">H", report_file.read(2))[0]
            value = None
            
            if key_type == ScDataType.ScDataType_String:
                str_len = self.decode_from_7bit(report_file)
                value = report_file.read(str_len).decode('utf8')
            elif key_type == ScDataType.ScDataType_Int32:
                value = struct.unpack(">I", report_file.read(4))[0]
            elif key_type == ScDataType.ScDataType_Int16:
                value = struct.unpack(">H", report_file.read(2))[0]
            elif key_type == ScDataType.ScDataType_Float:
                value = struct.unpack("f", report_file.read(4))[0]
            elif key_type == ScDataType.ScDataType_Byte:
                value = struct.unpack("B", report_file.read(1))[0]
            else:
                print("unknown key: {} {}\n".format(key_id, key_type))
                break

            results[str(key_id)] = value
            index += 1
        return results

    def ParseScReportData(self, report_file):
        result = {}
        protocolVersion = struct.unpack(">I", report_file.read(4))[0]
        developerVersion = struct.unpack(">I", report_file.read(4))[0]
        checksum = binascii.hexlify(report_file.read(16)).decode('ascii')

        gameStatus = struct.unpack(">I", report_file.read(4))[0]
        flags = struct.unpack(">I", report_file.read(4))[0]
        playerCount = struct.unpack(">H", report_file.read(2))[0]
        teamCount = struct.unpack(">H", report_file.read(2))[0]
        gameKeyCount = struct.unpack(">H", report_file.read(2))[0]
        playerKeyCount = struct.unpack(">H", report_file.read(2))[0]
        teamKeyCount = struct.unpack(">H", report_file.read(2))[0]
        reserved = struct.unpack(">H", report_file.read(2))[0]

        rosterSectionLength = struct.unpack(">I", report_file.read(4))[0]
        authSectionLength = struct.unpack(">I", report_file.read(4))[0]
        resultsSectionLength = struct.unpack(">I", report_file.read(4))[0]
        gameSectionLength = struct.unpack(">I", report_file.read(4))[0]
        playerSectionLength = struct.unpack(">I", report_file.read(4))[0]
        teamSectionLength = struct.unpack(">I", report_file.read(4))[0]

        roster = self.ParseRosterData(report_file, playerCount)        
        result["roster"] = roster

        auth_data = self.ParseAuthData(report_file, playerCount)
        result["auth_data"] = auth_data

        result_section = self.ParseResultsSection(report_file, playerCount, teamCount)
        result["result_section"] = result_section

        game_data = self.ParseSectionData(report_file, gameKeyCount)

        result["game_keys"] = game_data

        index = 0
        player_data = []
        while index < playerCount:
            num_keys = struct.unpack(">H", report_file.read(2))[0]
            player_section_data = self.ParseSectionData(report_file, num_keys)
            player_data.append(player_section_data)
            index += 1

        result["player_keys"] = player_data

        index = 0
        team_data = []
        while index < teamCount:
            num_keys = struct.unpack(">H", report_file.read(2))[0]
            team_section_data = self.ParseSectionData(report_file, num_keys)
            team_data.append(team_section_data)
            index += 1
        result["team_keys"] = team_data

        return result