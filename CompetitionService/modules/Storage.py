from modules.Exceptions import InvalidReportException
from bson import ObjectId
from datetime import datetime
class StorageManager():
    def __init__(self, dbCtx):
        self.dbCtx = dbCtx
    def CreateSession(self, profileid, gameid, platformid, matchless):
        collection = self.dbCtx["sessions"]

        db_record = {"gameid": gameid, "profileid": profileid, "platformid": platformid, "matchless": matchless, "created_at": datetime.now(), "reports": []}

        res = collection.insert_one(db_record)
        return str(res.inserted_id)
    def SetReportIntention(self, csid, profileid, gameid, authoritative):
        collection = self.dbCtx["session_intentions"]
        
        db_record = {"gameid": gameid, "profileid": profileid, "session_id": ObjectId(csid), "authoritative": authoritative, "created_at": datetime.now()}
        res = collection.insert_one(db_record)
        return str(res.inserted_id)
    def SubmitReport(self, csid, profileid, gameid, authoritative, report_data, ccid):
        collection = self.dbCtx["sessions"]

        report_submit_data = {
            "ccid": ccid,
            "authoritative": authoritative,
            "report": report_data,
            "created_at": datetime.now()
        }
        
        update_statement = {"$push": {"reports": report_submit_data}}

        match = {"_id": ObjectId(csid)}
        result = collection.update_one(match, update_statement)
        if result.matched_count == 0:
            raise InvalidReportException()
        return True