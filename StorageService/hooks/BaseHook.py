class BaseHook():
    gameid = None
    def GetGameId(self):
        return self.gameid
    def OnUploadFile(self, file_id, auth_info, storageManager):
        pass