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

mongoConnection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
storageDatabase = mongoConnection["CompetitionService"]
storageManager = StorageManager(storageDatabase)

createSessionHandler = CreateSessionHandler()
setReportIntentionHandler = SetReportIntentionHandler()
submitReportHandler = SubmitReportHandler()
createMatchlessSessionHandler = CreateMatchlessSessionHandler()
checkProfileOnBanListHandler = CheckProfileOnBanListHandler()

def handle_get(environ, start_response):
    start_response('404 NOT FOUND', [])

def handle_post(environ, start_response):
        ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
        ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
        ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
        ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
        try:
            if "HTTP_SOAPACTION" not in environ:
                start_response('400 BAD REQUEST', [])
                return None
            content_length = int(environ['CONTENT_LENGTH']) # <--- Gets the size of data
            request_type = environ['HTTP_SOAPACTION']

            result = None
            request_body = environ['wsgi.input'].read(content_length) # <--- Gets the data itself
            if request_type == "\"http://gamespy.net/competition/SubmitReport\"":
                fake_file = BytesIO(request_body)
                result = submitReportHandler.Handle(fake_file, storageManager)
            else:
                
                request_body = request_body.decode('utf8')

                tree = ET.ElementTree(ET.fromstring(request_body))
                        
                result = None

                if request_type == "\"http://gamespy.net/competition/CreateSession\"":
                    result = createSessionHandler.Handle(tree, storageManager)
                elif request_type == "\"http://gamespy.net/competition/CreateMatchlessSession\"":
                    result = createMatchlessSessionHandler.Handle(tree, storageManager)
                elif request_type == "\"http://gamespy.net/competition/SetReportIntention\"":
                    result = setReportIntentionHandler.Handle(tree, storageManager)
                elif request_type == "\"http://gamespy.net/competition/CheckProfileOnBanList\"": #AtlasDataServices
                    result = checkProfileOnBanListHandler.Handle(tree, storageManager)
                else:
                    print("unhandled request type: {}\n".format(request_type))

            if result == None:
                start_response('400 BAD REQUEST', [('Content-Type','application/xml')])
            else:
                start_response('200 OK', [('Content-Type','application/xml')])

            if result != None:
                return result
        except:
            traceback.print_exc()
            start_response('500 INTERNAL SERVER ERROR', [])
    
def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'GET':
        handle_get(environ, start_response)
    elif environ['REQUEST_METHOD'] == 'POST':
        result = handle_post(environ, start_response)
        if result != None:
            yield result