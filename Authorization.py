# -*- coding: utf-8 -*-

import codecs, json, os, re, math, datetime

class TwitchAuth(object):

    RefreshTokenFile = os.path.join(os.path.dirname(__file__), "tokens.json")
    TokenExpiration = None
    LastTokenCheck = None # Used to make sure the bot doesn't spam trying to reconnect if there's a problem
    RefreshToken = None
    AccessToken = None
    ExpirationOffset = 300

    def __init__(self, ScriptName, Parent, TwitchClientId, TwitchClientSecret, TwitchRedirectUrl, TwitchAuthCode, EnableDebug = False):
        self.Parent = Parent
        self.ScriptName = ScriptName
        self.EnableDebug = EnableDebug
        self.TwitchClientId = TwitchClientId
        self.TwitchClientSecret = TwitchClientSecret
        self.TwitchRedirectUrl = TwitchRedirectUrl
        self.TwitchAuthCode = TwitchAuthCode

        if os.path.isfile(self.RefreshTokenFile):
            with open(self.RefreshTokenFile) as f:
                content = f.readlines()
            if len(content) > 0:
                data = json.loads(content[0])
                self.RefreshToken = data["refresh_token"]
                self.AccessToken = data["access_token"]
                self.TokenExpiration = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d %H:%M:%S.%f")

    def CheckToken(self):
        tokenExpired = self.TokenExpiration < datetime.datetime.now()
        doCheck = self.LastTokenCheck is None or (self.LastTokenCheck + datetime.timedelta(seconds=60)) < datetime.datetime.now()
        if tokenExpired and doCheck: 
            self.Parent.Log(self.ScriptName, "Token expired. " + str(self.LastTokenCheck))
            return True
        else:
            return False

    def GetAccessToken(self):
        if self.AccessToken is None:
            self.RefreshTokens()
        return self.AccessToken

    #---------------------------
    #   RefreshTokens (Called when a new access token needs to be retrieved.)
    #---------------------------
    def RefreshTokens(self):
        result = None
        try:
            if self.RefreshToken:
                content = {
                    "client_id": self.TwitchClientId,
                    "client_secret": self.TwitchClientSecret,
	                "grant_type": "refresh_token",
	                "refresh_token": str(self.RefreshToken)
                }

                result = json.loads(json.loads(self.Parent.PostRequest("https://api.et-twitch-auth.com/",{}, content, True))["response"])
                if self.EnableDebug:
                    self.Parent.Log(self.ScriptName, str(content))
            else:
                if self.TwitchAuthCode == "":
                    self.LastTokenCheck = datetime.datetime.now()
                    self.TokenExpiration = datetime.datetime.now()
                    self.Parent.Log(ScriptName, "Access code cannot be retrieved please enter a valid authorization code.")
                    return False

                content = {
                    "client_id": self.TwitchClientId,
                    "client_secret": self.TwitchClientSecret,
                    'grant_type': 'authorization_code',
                    'code': self.TwitchAuthCode
                }

                result = json.loads(json.loads(self.Parent.PostRequest("https://api.et-twitch-auth.com/",{}, content, True))["response"])
                if self.EnableDebug:
                    self.Parent.Log(self.ScriptName, str(content))

            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, str(result))

            self.RefreshToken = result["refresh_token"]
            self.AccessToken = result["access_token"]
            self.TokenExpiration = datetime.datetime.now() + datetime.timedelta(seconds=int(result["expires_in"]) - self.ExpirationOffset)

            self.LastTokenCheck = datetime.datetime.now()
            self.SaveTokens()
        except Exception as e:
            self.LastTokenCheck = datetime.datetime.now()
            self.TokenExpiration = datetime.datetime.now()
            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, "Exception: " + str(e.message))
            return False

        return True

    #---------------------------
    #   SaveTokens (Saves tokens and expiration time to a json file in script bin for use on script restart and reload.)
    #---------------------------
    def SaveTokens(self):
        data = {
            "refresh_token": self.RefreshToken,
            "access_token": self.AccessToken,
            "expiration": str(self.TokenExpiration)
        }

        with open(self.RefreshTokenFile, 'w') as f:
            f.write(json.dumps(data))

    #---------------------------
    #   DeleteSavedTokens (Attached to settings button to allow user to easily delete the tokens.json file and clear out RefreshToken currently in memory so that a new authorization code can be entered and used.)
    #---------------------------
    def DeleteSavedTokens(self):
        if os.path.exists(self.RefreshTokenFile):
            os.remove(self.RefreshTokenFile)
        self.RefreshToken = None

    #---------------------------
    #   GetUserID (Calls twitch's api with current channel user name to get the user id and sets global UserID variable.)
    #---------------------------
    def GetUserID(self):
        headers = { 
            "Client-ID": self.TwitchClientId,
            "Authorization": "Bearer " + self.AccessToken
        }
        result = json.loads(self.Parent.GetRequest("https://api.twitch.tv/helix/users?login=" + self.Parent.GetChannelName(), headers))
        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, "headers: " + str(headers))
            self.Parent.Log(self.ScriptName, "result: " + str(result))
        user = json.loads(result["response"])
        return user["data"][0]["id"]

def GetToken(self):
    if self.TwitchRedirectUrl == "" or self.TwitchClientId == "":
        return

    redirectUrl = self.TwitchRedirectUrl
    if redirectUrl[-1:] != "/":
        redirectUrl += "/"

    os.startfile("https://id.twitch.tv/oauth2/authorize?response_type=code&client_id=" + self.TwitchClientId + "&redirect_uri=" + redirectUrl + "&scope=channel:read:redemptions&force_verify=true")