import struct
class DIMEFile():
    idString = None
    mimeType = None
    binaryData = None
    def __init__(self, idString, mimeType, binaryData):
        self.idString = idString
        self.mimeType = mimeType
        self.binaryData = binaryData
class DIMEParser():
    def Parse(self, dime_buffer):
        dime_files = []
        while dime_buffer.readable():
            try:
                dime_files.append(self.ParseDIMEEntry(dime_buffer))
            except struct.error:
                break
        return dime_files

    def ParseDIMEEntry(self, dime_file):
        VersionAndFlags = struct.unpack("b", dime_file.read(1))[0]

        is_first = VersionAndFlags & (1<<2)
        VersionAndFlags = VersionAndFlags & ~(1<<2)

        is_last = VersionAndFlags & (1<<1)
        VersionAndFlags = VersionAndFlags & ~(1<<1)

        is_chunked = VersionAndFlags & (1<<0)
        VersionAndFlags = VersionAndFlags & ~(1<<0)

        version = (VersionAndFlags) >> 3

        typeT = struct.unpack("B", dime_file.read(1))[0]
        optionsLength = struct.unpack(">H", dime_file.read(2))[0]
        idLength = struct.unpack(">H", dime_file.read(2))[0]
        typeLength = struct.unpack(">H", dime_file.read(2))[0]
        dataLength = struct.unpack(">I", dime_file.read(4))[0]

        offset = 12

        idString = dime_file.read(idLength).decode('utf-8')
        offset += idLength
        dime_file.read(4-offset%4)
        offset += (4-offset%4)

        contentType = dime_file.read(typeLength).decode('utf-8')
        offset += typeLength
        dime_file.read(4-offset%4)
        offset += (4-offset%4)

        otherData = dime_file.read(dataLength)
        offset += dataLength
        dime_file.read(4-offset%4)
        offset += (4-offset%4)
        return DIMEFile(idString, contentType, otherData)
