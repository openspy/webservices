import cgi
from modules.Exceptions import SAKEException 
from hooks.HookResolver import HookResolver

from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

class FileUploadHandler():
    def returnFileError(self, httpHandler):
        httpHandler.send_response(HTTPStatus.BAD_REQUEST)
        httpHandler.send_header('Sake-File-Result', 0)
    def Handle(self, httpHandler, storageManager):
        ctype, pdict = cgi.parse_header(httpHandler.headers['Content-Type'])
        query_data = parse_qs(urlparse(httpHandler.path).query)

        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            fields = cgi.parse_multipart(httpHandler.rfile, pdict)
            
            file_name = None
            for field in fields:
                if field != "boundary":
                    file_name = field
            
            file_raw_data = fields[file_name][0]

            gameid = query_data.get('gameid', None)
            profileid = query_data.get('pid', None)

            if gameid != None:
                gameid = int(gameid[0])
            if profileid != None:
                profileid = int(profileid[0])

            if gameid == None or profileid == None:
                self.returnFileError(httpHandler)
                return
            hookResolver = HookResolver()
            resolver = hookResolver.GetResolverForGameId(gameid)

            success = False
            file_id = storageManager.UploadFile(gameid, profileid, file_name, file_raw_data)
            if file_id != 0:
                success = True
                httpHandler.send_response(HTTPStatus.OK)
                httpHandler.send_header('Sake-File-Id',str(file_id))
                if resolver != None:
                    resolver.OnUploadFile(file_id, profileid, file_name, file_raw_data, storageManager)
            else:
                httpHandler.send_response(HTTPStatus.BAD_REQUEST)

            httpHandler.send_header('Sake-File-Result', 1 if success else 0)
            httpHandler.end_headers()


class FileDownloadHandler():
    def returnFileError(self, httpHandler):
        httpHandler.send_response(HTTPStatus.BAD_REQUEST)
    def Handle(self, httpHandler, storageManager):
        query_data = parse_qs(urlparse(httpHandler.path).query)


        gameid = query_data.get('gameid', None)
        profileid = query_data.get('pid', None)
        fileid = query_data.get('fileid', None)

        if gameid != None:
            gameid = int(gameid[0])
        if profileid != None:
            profileid = int(profileid[0])
        if fileid != None:
            fileid = int(fileid[0])

        if gameid == None or profileid == None or fileid == None:
            self.returnFileError(httpHandler)
            return

        file_data = storageManager.DownloadFile(gameid, profileid, fileid)
        if file_data != None:
            httpHandler.send_response(HTTPStatus.OK)
            httpHandler.send_header("Content-type", "application/octet-stream")
            httpHandler.send_header("Content-Disposition", "attachment; filename=\"{}\"".format(file_data["name"]))
            httpHandler.send_header("Content-Length", "{}".format(len(file_data["data"])))
            httpHandler.end_headers()
            httpHandler.wfile.write(file_data["data"])
        else:
            httpHandler.send_response(HTTPStatus.NOT_FOUND)
            httpHandler.end_headers()

        

        