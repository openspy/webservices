import http.server
import socketserver
from http import HTTPStatus
import xml.etree.ElementTree as ET
from collections import OrderedDict
import binascii
import hashlib
import struct, os
from handlers.CreateRecord import CreateRecordHandler
from handlers.UpdateRecord import UpdateRecordHandler
from handlers.GetRecordLimit import GetRecordLimitHandler
from handlers.RateRecord import RateRecordHandler
from handlers.GetSpecificRecords import GetSpecificRecordsHandler
from handlers.GetMyRecords import GetMyRecordsHandler
from handlers.SearchForRecords import SearchForRecordsHandler
from handlers.DeleteRecord import DeleteRecordHandler
from handlers.GetRandomRecords import GetRandomRecordsHandler
from modules.Storage import StorageManager
import pymongo
import redis


class Handler(http.server.SimpleHTTPRequestHandler):
    mongoConnection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
    storageDatabase = mongoConnection["StorageService"]
    loginTicketCache = redis.from_url(os.environ.get('REDIS_URL'), db=3)

    createRecordHandler = CreateRecordHandler()
    updateRecordHandler = UpdateRecordHandler()
    getRecordLimitHandler = GetRecordLimitHandler()
    rateRecordHandler = RateRecordHandler()
    getSpecificRecordsHandler = GetSpecificRecordsHandler()
    getMyRecordsHandler = GetMyRecordsHandler()
    searchForRecordsHandler = SearchForRecordsHandler()
    deleteRecordHandler = DeleteRecordHandler()
    getRandomRecordsHandler = GetRandomRecordsHandler()

    storageManager = StorageManager(storageDatabase, loginTicketCache)

    def do_GET(self):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        request_body = self.rfile.read(content_length) # <--- Gets the data itself

        request_body = request_body.decode('utf8').replace("<s1", "<ns1").replace("</s1", "</ns1") #weird ps3 fix

        ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
        ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
        tree = ET.ElementTree(ET.fromstring(request_body))
        

        request_type = self.headers['SOAPAction']
        print("request_type: {}\n".format(request_type))

                
        result = None

        if request_type == "\"http://gamespy.net/sake/CreateRecord\"":
            result = self.createRecordHandler.Handle(self, tree, self.storageManager)
        elif request_type == "\"http://gamespy.net/sake/UpdateRecord\"":
            result = self.updateRecordHandler.Handle(self, tree, self.storageManager)
        elif request_type == "\"http://gamespy.net/sake/GetRecordLimit\"":
            result = self.getRecordLimitHandler.Handle(self, tree)
        elif request_type == "\"http://gamespy.net/sake/RateRecord\"":
            result = self.rateRecordHandler.Handle(self, tree)
        elif request_type == "\"http://gamespy.net/sake/GetSpecificRecords\"":
            result = self.getSpecificRecordsHandler.Handle(self, tree, self.storageManager)
        elif request_type == "\"http://gamespy.net/sake/GetMyRecords\"":
            result = self.getMyRecordsHandler.Handle(self, tree, self.storageManager)
        elif request_type == "\"http://gamespy.net/sake/SearchForRecords\"":
            result = self.searchForRecordsHandler.Handle(self, tree)
        elif request_type == "\"http://gamespy.net/sake/DeleteRecord\"":
            result = self.deleteRecordHandler.Handle(self, tree, self.storageManager)
        elif request_type == "\"http://gamespy.net/sake/GetRandomRecords\"":
            result = self.getRandomRecordsHandler.Handle(self, tree)
        else:
            print("unhandled request type: {}\n".format(request_type))
            



        if result == None:
            self.send_response(HTTPStatus.BAD_REQUEST)
        else:
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type','application/xml')
        self.end_headers()

        if result != None:
            self.wfile.write(result)
        



httpd = socketserver.TCPServer(('', int(os.environ.get('PORT'))), Handler)
httpd.serve_forever()
