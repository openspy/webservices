from hooks.BaseHook import BaseHook
class SaintsRow2Hooks(BaseHook):
    def __init__(self):
        pass
    def OnUploadFile(self, file_id, profileid, file_name, file_raw_data, storageManager):
        table_name = "user_file_storage"

        set_data = {
            "filename": {"value": "MPStorage", "type": "ascii"},
            "file_id": {"value": file_id, "type": "int"}
        }

        auth_info = {"gameid": self.gameid, "profileId": profileid}

        records = storageManager.FindAllRecordsByProfileid(auth_info, table_name)

        recordid = None
        if len(records) >= 1:
            recordid = records[0]["recordid"]
        
        if recordid != None:
            storageManager.Update(auth_info, table_name, recordid, set_data)
        else:
            storageManager.Create(auth_info, table_name, set_data)
