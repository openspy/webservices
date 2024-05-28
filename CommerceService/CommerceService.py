import xml.etree.ElementTree as ET
import traceback

from handlers.GetStoreAvailability import GetStoreAvailabilityHandler
from handlers.GetPurchaseHistory import GetPurchaseHistoryHandler

getStoreAvailabilityHandler = GetStoreAvailabilityHandler()
getPurchaseHistoryHandler = GetPurchaseHistoryHandler()

def handle_get(environ, start_response):
    start_response('404 NOT FOUND', [])

def handle_post(environ, start_response):
    try:

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

        if request_type == "\"http://gamespy.net/commerce/2009/02/CatalogService/GetStoreAvailability\"":
            result = getStoreAvailabilityHandler.Handle(tree)
        elif request_type == "\"http://gamespy.net/commerce/2009/02/PurchaseService/GetPurchaseHistory\"":
            result = getPurchaseHistoryHandler.Handle(tree)
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
    if environ['REQUEST_METHOD'] == 'GET':
        handle_get(environ, start_response)
    elif environ['REQUEST_METHOD'] == 'POST':
        result = handle_post(environ, start_response)
        if result != None:
            yield result