import requests
class OpenSpyAuth():
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
    def TestPreAuth(self, authtoken, challenge):
        try:
            headers = {"APIKey": self.api_key}

            r = requests.post(self.api_url + '/v1/Auth/TestPreAuth', json = {'token': authtoken, 'challenge': challenge}, headers = headers)
            response = r.json()
            return response
        except:
            return None

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
        try:
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
        except:
            return None