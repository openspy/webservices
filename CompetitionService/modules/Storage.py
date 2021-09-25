from modules.Exceptions import InvalidReportException
from bson import ObjectId
class StorageManager():
    def __init__(self, dbCtx):
        self.dbCtx = dbCtx
    def CreateSession(self, profileid, gameid, platformid, matchless):
        collection = self.dbCtx["sessions"]

        db_record = {"gameid": gameid, "profileid": profileid, "platformid": platformid, "matchless": matchless, "reports": []}

        res = collection.insert_one(db_record)
        return str(res.inserted_id)
    def SetReportIntention(self, csid, profileid, gameid, authoritative):
        collection = self.dbCtx["session_intentions"]
        
        db_record = {"gameid": gameid, "profileid": profileid, "session_id": ObjectId(csid), "authoritative": authoritative}
        res = collection.insert_one(db_record)
        return str(res.inserted_id)
    def SubmitReport(self, csid, profileid, gameid, authoritative, report_data, ccid):
        collection = self.dbCtx["sessions"]

        report_submit_data = {
            "ccid": ccid,
            "authoritative": authoritative,
            "report": report_data
        }
        
        update_statement = {"$push": {"reports": report_submit_data}}

        match = {"_id": ObjectId(csid)}
        result = collection.update_one(match, update_statement)
        if result.matched_count == 0:
            raise InvalidReportException()
        return True