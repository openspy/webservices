from hooks.SaintsRow2Hooks import SaintsRow2Hooks
class HookResolver():
    def GetResolverForGameId(self, gameid):
        if gameid == 2110:
            return SaintsRow2Hooks()
        return None