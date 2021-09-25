import http.server
import socketserver
from http import HTTPStatus
import xml.etree.ElementTree as ET
from collections import OrderedDict
import binascii
import hashlib
import struct, os
import pymongo
from handlers.CreateSession import CreateSessionHandler
from handlers.CreateMatchlessSession import CreateMatchlessSessionHandler
from handlers.SetReportIntention import SetReportIntentionHandler
from handlers.SubmitReport import SubmitReportHandler
from handlers.CheckProfileOnBanList import CheckProfileOnBanListHandler

from modules.Storage import StorageManager

from io import BytesIO
import traceback
import rsa

class Handler(http.server.SimpleHTTPRequestHandler):
    mongoConnection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
    storageDatabase = mongoConnection["CompetitionService"]
    storageManager = StorageManager(storageDatabase)

    createSessionHandler = CreateSessionHandler()
    setReportIntentionHandler = SetReportIntentionHandler()
    submitReportHandler = SubmitReportHandler()
    createMatchlessSessionHandler = CreateMatchlessSessionHandler()
    checkProfileOnBanListHandler = CheckProfileOnBanListHandler()

    def do_GET(self):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()


    def do_POST(self):
        ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
        ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
        try:
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            request_type = self.headers['SOAPAction']

            result = None
            request_body = self.rfile.read(content_length) # <--- Gets the data itself
            if request_type == "\"http://gamespy.net/competition/SubmitReport\"":
                fake_file = BytesIO(request_body)
                result = self.submitReportHandler.Handle(self, fake_file, self.storageManager)
            else:
                
                request_body = request_body.decode('utf8')

                tree = ET.ElementTree(ET.fromstring(request_body))
                        
                result = None

                if request_type == "\"http://gamespy.net/competition/CreateSession\"":
                    result = self.createSessionHandler.Handle(self, tree, self.storageManager)
                elif request_type == "\"http://gamespy.net/competition/CreateMatchlessSession\"":
                    result = self.createMatchlessSessionHandler.Handle(self, tree, self.storageManager)
                elif request_type == "\"http://gamespy.net/competition/SetReportIntention\"":
                    result = self.setReportIntentionHandler.Handle(self, tree, self.storageManager)
                elif request_type == "\"http://gamespy.net/competition/CheckProfileOnBanList\"": #AtlasDataServices
                    result = self.checkProfileOnBanListHandler.Handle(self, tree, self.storageManager)
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
        except:
            traceback.print_exc()
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.end_headers()


httpd = socketserver.TCPServer(('', int(os.environ.get('PORT'))), Handler)
httpd.serve_forever()
