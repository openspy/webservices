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
from handlers.FileStorage import FileUploadHandler, FileDownloadHandler
from modules.Storage import StorageManager
import pymongo
import redis
import traceback

mongoConnection = pymongo.MongoClient(os.environ.get('MONGODB_URI'))
storageDatabase = mongoConnection["StorageService"]
loginTicketCachePool = redis.ConnectionPool.from_url(os.environ.get('REDIS_URL'), db=3)

createRecordHandler = CreateRecordHandler()
updateRecordHandler = UpdateRecordHandler()
getRecordLimitHandler = GetRecordLimitHandler()
rateRecordHandler = RateRecordHandler()
getSpecificRecordsHandler = GetSpecificRecordsHandler()
getMyRecordsHandler = GetMyRecordsHandler()
searchForRecordsHandler = SearchForRecordsHandler()
deleteRecordHandler = DeleteRecordHandler()
getRandomRecordsHandler = GetRandomRecordsHandler()

fileUploadHandler = FileUploadHandler()
fileDownloadHandler = FileDownloadHandler()



def handle_SakeFileServer(environ, start_response):
    try:
        loginTicketCache = redis.Redis(connection_pool=loginTicketCachePool)
        storageManager = StorageManager(storageDatabase, loginTicketCache)
        if environ['PATH_INFO'] == "/SakeFileServer/upload.aspx":
            return fileUploadHandler.Handle(environ, start_response, storageManager)
        elif environ['PATH_INFO'] == "/SakeFileServer/download.aspx":
            return fileDownloadHandler.Handle(environ, start_response, storageManager)
    except:
        traceback.print_exc()
        start_response('500 INTERNAL SERVER ERROR', [])
    return None

def handle_get(environ, start_response):
    if environ['PATH_INFO'] == "/SakeFileServer/download.aspx":
        return handle_SakeFileServer(environ, start_response)
    else:
        start_response('404 NOT FOUND', [])
        return None
        

def handle_post(environ, start_response):
    try:
        loginTicketCache = redis.Redis(connection_pool=loginTicketCachePool)
        storageManager = StorageManager(storageDatabase, loginTicketCache)
        if environ['PATH_INFO'] == "/SakeFileServer/upload.aspx":
            return handle_SakeFileServer(environ, start_response)
        else:
            if "HTTP_SOAPACTION" not in environ:
                start_response('400 BAD REQUEST', [])
                return None
            content_length = int(environ['CONTENT_LENGTH']) # <--- Gets the size of data
            request_body = environ['wsgi.input'].read(content_length) # <--- Gets the data itself

            request_body = request_body.decode('utf8').replace("<s1", "<ns1").replace("</s1", "</ns1") #weird ps3 fix

            ET.register_namespace('SOAP-ENV',"http://schemas.xmlsoap.org/soap/envelope/")
            ET.register_namespace('SOAP-ENC',"http://schemas.xmlsoap.org/soap/encoding/")
            ET.register_namespace('xsi',"http://www.w3.org/2001/XMLSchema-instance")
            ET.register_namespace('xsd',"http://www.w3.org/2001/XMLSchema")
            tree = ET.ElementTree(ET.fromstring(request_body))
            

            request_type = environ['HTTP_SOAPACTION']

                    
            result = None

            if request_type == "\"http://gamespy.net/sake/CreateRecord\"":
                result = createRecordHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/UpdateRecord\"":
                result = updateRecordHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/GetRecordLimit\"":
                result = getRecordLimitHandler.Handle(tree)
            elif request_type == "\"http://gamespy.net/sake/RateRecord\"":
                result = rateRecordHandler.Handle(tree)
            elif request_type == "\"http://gamespy.net/sake/GetSpecificRecords\"":
                result = getSpecificRecordsHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/GetMyRecords\"":
                result = getMyRecordsHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/SearchForRecords\"":
                result = searchForRecordsHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/DeleteRecord\"":
                result = deleteRecordHandler.Handle(tree, storageManager)
            elif request_type == "\"http://gamespy.net/sake/GetRandomRecords\"":
                result = getRandomRecordsHandler.Handle(tree)
            else:
                print("unhandled request type: {}\n".format(request_type))
                


            headers = []
            status = '400 BAD REQUEST'
            if result != None:
                status = '200 OK'
                headers.append(('Content-Type','application/xml'))
                headers.append(('Content-Length',str(len(result))))

            start_response(status, headers)
            return result
    except:  
        traceback.print_exc()
        start_response('500 INTERNAL SERVER ERROR', [])
        return None

def application(environ, start_response):
    result = None
    if environ['REQUEST_METHOD'] == 'GET':
        result = handle_get(environ, start_response)
    elif environ['REQUEST_METHOD'] == 'POST':
        result = handle_post(environ, start_response)
    if result != None:
        yield result