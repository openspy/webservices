import base64
import xml.etree.ElementTree as ET

from modules.Exceptions import RecordNotFoundException, TableNotFoundException 
from modules.Tokenizer.TokenParser import TokenParser
from modules.Tokenizer.MongoTokenConverter import MongoTokenConverter
from modules.Tokenizer.RPNConverter import RPNConverter
from modules.Tokenizer.SortByParse import MongoSortFactory

class StorageManager():
    def __init__(self, dbCtx, loginTicketCache):
        self.dbCtx = dbCtx
        self.loginTicketCache = loginTicketCache

    #login ticket stuff
    def GetProfileIdFromLoginTicket(self, loginTicket):
        if not self.loginTicketCache.exists(loginTicket):
            return None
        pid = self.loginTicketCache.hget(loginTicket, "profileid")
        return int(pid)
        
    #Mongo stuff
    def GetRecordCollectionName(self, gameid, tableid):
        return "records_{}_{}".format(gameid, tableid)
    def CollectionExists(self, db, gameid, tableid):
        return self.GetRecordCollectionName(gameid, tableid) in db.list_collection_names()
    def GenerateRecordId(self, db, collection_name):
        incrementor_collection = db["incrementors"]
        match = {"tablename": collection_name}
        incrementor_collection.update(match, {"$inc": {"recordid": 1}}, upsert = True)
        result = incrementor_collection.find_one(match)
        return result["recordid"]
    def Create(self, auth_info, tableId, records):
        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        recordId = self.GenerateRecordId(self.dbCtx, collection_name)
        collection = self.dbCtx[collection_name]

        db_record = {"gameid": auth_info["gameid"], "ownerid": auth_info["profileId"], "tableid": tableId, "recordid": recordId, "data": records}

        match = {"gameid": auth_info["gameid"], "ownerid": auth_info["profileId"], "tableid": tableId}

        collection.insert_one(db_record)

        return recordId

    def Update(self, auth_info, tableId, recordId, records):
        if not self.CollectionExists(self.dbCtx, auth_info["gameid"], tableId):
            raise TableNotFoundException()

        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        collection = self.dbCtx[collection_name]

        update_statement = {"$set": {"data": records}}

        match = {"gameid": auth_info["gameid"], "ownerid": auth_info["profileId"], "tableid": tableId, "recordid": recordId}
        result = collection.update_one(match, update_statement)
        if result.matched_count == 0:
            raise RecordNotFoundException()

    def Delete(self, auth_info, tableId, recordId):
        if not self.CollectionExists(self.dbCtx, auth_info["gameid"], tableId):
            raise TableNotFoundException()

        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        collection = self.dbCtx[collection_name]

        match = {"gameid": auth_info["gameid"], "ownerid": auth_info["profileId"], "tableid": tableId, "recordid": recordId}
        result = collection.delete_one(match)
        if result.deleted_count == 0:
            raise RecordNotFoundException()
        return result.deleted_count > 0
    def FindAllRecordsByProfileid(self, auth_info, tableId):
        if not self.CollectionExists(self.dbCtx, auth_info["gameid"], tableId):
            raise TableNotFoundException()

        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        collection = self.dbCtx[collection_name]

        match = {"gameid": auth_info["gameid"], "ownerid": auth_info["profileId"], "tableid": tableId}
        results = collection.find(match)

        output = []
        for item in results:
            output.append(item)
        return output
    def FindAllRecordsByIDs(self, auth_info, tableId, recordIds):
        if not self.CollectionExists(self.dbCtx, auth_info["gameid"], tableId):
            raise TableNotFoundException()

        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        collection = self.dbCtx[collection_name]

        match = {"gameid": auth_info["gameid"], "tableid": tableId, "recordid": {"$in": recordIds}}
        results = collection.find(match)
        output = []
        for item in results:
            output.append(item)
        return output
    def ConvertFilter(self, filterString):
        parser = TokenParser()
        result = parser.ParseTokens(filterString)

        rpnConverter = RPNConverter()
        result = rpnConverter.Convert(result)

        mongoConverter = MongoTokenConverter()

        return mongoConverter.ConvertTokenList(result).GetMongoDocument()

    def SearchRecords(self, auth_info, tableId, fields, filterString, sortString, queryOffset, maxRows):
        if not self.CollectionExists(self.dbCtx, auth_info["gameid"], tableId):
            raise TableNotFoundException()

        pipeline = []

        if filterString != None:
            match_contents = self.ConvertFilter(filterString)
            match_entry = {"$match": match_contents}
            pipeline.append(match_entry)
        if sortString != None:
            sortFactory = MongoSortFactory()
            sort_data = sortFactory.Sort(sortString)
            sort_entry = {"$sort": sort_data}
            pipeline.append(sort_entry)

        if queryOffset != None:
            skip_entry = {"$skip": queryOffset}
            pipeline.append(skip_entry)

        if maxRows != None:
            skip_entry = {"$limit": maxRows}
            pipeline.append(skip_entry)
            

        collection_name = self.GetRecordCollectionName(auth_info["gameid"], tableId)
        collection = self.dbCtx[collection_name]

        results = collection.aggregate(pipeline)
        output = []
        for item in results:
            output.append(item)
        return output

    def UploadFile(self, gameid, profileid, file_name, file_data):
        
        collection_name = "files_{}".format(gameid)
        collection = self.dbCtx[collection_name]

        match = {"gameid": gameid, "profileid": profileid, "name": file_name}

        base46_data = base64.b64encode(file_data)
        base64_string = base46_data.decode('ascii')
        
        file_result = collection.find_one(match, sort=[('fileid', -1)])
        if file_result == None:
            file_id = self.GenerateRecordId(self.dbCtx, collection_name)
            file_data = {"gameid": gameid, "profileid": profileid, "name": file_name, "fileid": file_id, "data": base64_string}
            collection.insert_one(file_data)
        else:
            match = {"_id": file_result["_id"]}
            update_statement = {"$set": {"data": base64_string}}
            file_id = file_result["fileid"]

            result = collection.update_one(match, update_statement)
            if result.matched_count == 0:
                raise RecordNotFoundException()

        return file_id
    def DownloadFile(self, gameid, profileid, fileid):
        collection_name = "files_{}".format(gameid)
        collection = self.dbCtx[collection_name]

        match = {"gameid": gameid, "profileid": profileid, "fileid": fileid}
        file_result = collection.find_one(match)
        if file_result == None:
            return file_result

        result_data = {"name": file_result["name"], "data": base64.b64decode(file_result["data"])}
        return result_data
