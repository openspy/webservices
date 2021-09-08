import requests
class OpenSpyAuth():
    def __init__(self, api_url, api_key, auth_token_expire):
        self.api_url = api_url
        self.api_key = api_key
        self.auth_token_expire = auth_token_expire
    def TestPreAuth(self, authtoken, challenge):
         headers = {"APIKey": self.api_key}
         r = requests.post(self.api_url + '/v1/Auth/TestPreAuth', json = {'token': authtoken, 'challenge': challenge}, headers = headers)
         response = r.json()
         return response

    def GenerateAuthToken(self, profileid):
         headers = {"APIKey": self.api_key}
         request = {
             "profile": {"id": profileid},
             "expiresIn": self.auth_token_expire
         }
         r = requests.post(self.api_url + '/v1/Presence/Auth/GenAuthTicket', json = request, headers = headers)
         response = r.json()
         return response

    def UniqueNickLogin(self, uniquenick, namespaceid, partnercode, password):
        try:
            headers = {"APIKey": self.api_key}

            params = {
                "profileLookup": {
                    "uniquenick": uniquenick,
                    "namespaceid": namespaceid,
                    "partnercode": partnercode
                },
                "password": password
            }
            r = requests.post(self.api_url + '/v1/Auth/Login', json = params, headers = headers)
            response = r.json()
            return response
        except:
            return None

    def NickLogin(self, nick, email, namespaceid, partnercode, password):
         headers = {"APIKey": self.api_key}

         params = {
             "profileLookup": {
                 "nick": nick,
                 "namespaceid": namespaceid,
                 "partnercode": partnercode,
                 "user": {"email": email}
             },
             "password": password
         }
         r = requests.post(self.api_url + '/v1/Auth/Login', json = params, headers = headers)
         response = r.json()
         return response
