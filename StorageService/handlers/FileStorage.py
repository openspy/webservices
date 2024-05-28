import cgi
from hooks.HookResolver import HookResolver

from urllib.parse import urlparse, parse_qs

class FileUploadHandler():
    def returnFileError(self, environ, start_response):
        start_response('400 BAD REQUEST', [('Sake-File-Result', 0)])
    def Handle(self, environ, start_response, storageManager):
        ctype, pdict = cgi.parse_header(environ['CONTENT_TYPE'])
        query_data = parse_qs(environ['QUERY_STRING'])

        if ctype == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            fields = cgi.parse_multipart(environ['wsgi.input'], pdict)
            
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
                self.returnFileError(environ, start_response)
                return
            hookResolver = HookResolver()
            resolver = hookResolver.GetResolverForGameId(gameid)

            success = False
            file_id = storageManager.UploadFile(gameid, profileid, file_name, file_raw_data)

            headers = []
            status = '400 BAD REQUEST'
            if file_id != 0:
                success = True
                status = '200 OK'
                headers.append(('Sake-File-Id',str(file_id)))
                if resolver != None:
                    resolver.OnUploadFile(file_id, profileid, file_name, file_raw_data, storageManager)

            headers.append(('Sake-File-Result', "1" if success else "0"))
            start_response(status, headers)


class FileDownloadHandler():
    def returnFileError(self, environ, start_response):
        start_response('400 BAD REQUEST', [])
    def Handle(self, environ, start_response, storageManager):
        query_data = parse_qs(environ['QUERY_STRING'])

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
            self.returnFileError(environ, start_response)
            return

        file_data = storageManager.DownloadFile(gameid, profileid, fileid)
        if file_data != None:
            headers = [
                ("Content-type", "application/octet-stream"),
                ("Content-Disposition", "attachment; filename=\"{}\"".format(file_data["name"])),
                ("Content-Length", "{}".format(len(file_data["data"])))
            ]
            start_response('200 OK', headers)
            return file_data["data"]
        else:
            start_response('404 NOT FOUND', [])

        

        