import http.server
import socketserver
from http import HTTPStatus
import xml.etree.ElementTree as ET
from collections import OrderedDict
import binascii
import hashlib
import struct, os
import pymongo
import redis
from handlers.CreateSession import CreateSessionHandler
from handlers.CreateMatchlessSession import CreateMatchlessSessionHandler
from handlers.SetReportIntention import SetReportIntentionHandler
from handlers.SubmitReport import SubmitReportHandler
from handlers.CheckProfileOnBanList import CheckProfileOnBanListHandler

class Handler(http.server.SimpleHTTPRequestHandler):
    mongoConnection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
    storageDatabase = mongoConnection["CompetitionService"]
    loginTicketCache = redis.from_url(os.environ.get('REDIS_URL'), db=3)

    createSessionHandler = CreateSessionHandler()
    setReportIntentionHandler = SetReportIntentionHandler()
    submitReportHandler = SubmitReportHandler()
    createMatchlessSessionHandler = CreateMatchlessSessionHandler()
    checkProfileOnBanListHandler = CheckProfileOnBanListHandler()

    def do_GET(self):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()


    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        request_body = self.rfile.read(content_length) # <--- Gets the data itself

        request_type = self.headers['SOAPAction']

        result = None

        if request_type == "\"http://gamespy.net/competition/SubmitReport\"":
            result = self.submitReportHandler.Handle(self, request_body)
        else:
            request_body = request_body.decode('utf8')

            ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
            ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
            ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
            ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
            tree = ET.ElementTree(ET.fromstring(request_body))
                    
            result = None

            if request_type == "\"http://gamespy.net/competition/CreateSession\"":
                result = self.createSessionHandler.Handle(self, tree)
            elif request_type == "\"http://gamespy.net/competition/CreateMatchlessSession\"":
                result = self.createMatchlessSessionHandler.Handle(self, tree)
            elif request_type == "\"http://gamespy.net/competition/SetReportIntention\"":
                result = self.setReportIntentionHandler.Handle(self, tree)
            elif request_type == "\"http://gamespy.net/competition/CheckProfileOnBanList\"": #AtlasDataServices
                result = self.checkProfileOnBanListHandler.Handle(self, tree)
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
