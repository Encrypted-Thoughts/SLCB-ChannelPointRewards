# -*- coding: utf-8 -*-

#---------------------------
#   Import Libraries
#---------------------------
import clr, codecs, json, os, re, sys, threading, datetime

clr.AddReference("IronPython.Modules.dll")
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)) + "\References", r"TwitchLib.PubSub.dll"))
from TwitchLib.PubSub import TwitchPubSub

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Channel Point Rewards"
Website = "https://www.twitch.tv/EncryptedThoughts"
Description = "Listens to Twitch API's pubsub events and triggers various different types of events as rewards."
Creator = "EncryptedThoughts"
Version = "2.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
RefreshTokenFile = os.path.join(os.path.dirname(__file__), "tokens.json")
ReadMe = os.path.join(os.path.dirname(__file__), "README.txt")
EventReceiver = None
ThreadQueue = []
CurrentThread = None
PlayNextAt = datetime.datetime.now()
TokenExpiration = None
LastTokenCheck = None # Used to make sure the bot doesn't spam trying to reconnect if there's a problem
RefreshToken = None
AccessToken = None
UserID = None

InvalidRefreshToken = False

#---------------------------------------
# Classes
#---------------------------------------
class Settings(object):
    def __init__(self, SettingsFile=None):
        if SettingsFile and os.path.isfile(SettingsFile):
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        else:
            self.EnableDebug = False
            self.AHKExePath = ""
            self.TwitchClientId = ""
            self.TwitchClientSecret = ""
            self.TwitchRedirectUrl = ""
            self.TwitchAuthCode = ""

            for i in range(1, 2):
                setattr(self, "RewardName" + str(i), "")
                setattr(self, "RewardType" + str(i), "Immediate")
                setattr(self, "RewardActivationType" + str(i), "Immediate")

                setattr(self, "AlertMediaPath" + str(i), "")
                setattr(self, "AlertText" + str(i), "")
                setattr(self, "AlertSFXPath" + str(i), "")
                setattr(self, "AlertSFXVolume" + str(i), 100)
                setattr(self, "AlertSFXDelay" + str(i), 10)

                setattr(self, "CountdownTitle" + str(i), "")
                setattr(self, "CountdownLength" + str(i), 60)
                setattr(self, "ResetCommand" + str(i), "!reset1")
                setattr(self, "RedeemedSFXPath" + str(i), "")
                setattr(self, "RedeemedSFXVolume" + str(i), 100)
                setattr(self, "RedeemedSFXDelay" + str(i), 10)
                setattr(self, "FinishedSFXPath" + str(i), "")
                setattr(self, "FinishedSFXVolume" + str(i), 100)

                setattr(self, "TimeoutType" + str(i), "Fixed")
                setattr(self, "TimeoutFixedUser" + str(i), "")
                setattr(self, "TimeoutDuration" + str(i), 1)

                setattr(self, "UseRewardCost" + str(i), True)
                setattr(self, "CurrencyAmount" + str(i), 0)

                setattr(self, "AHKPath" + str(i), "")
                setattr(self, "AHKArguments" + str(i), None)
                setattr(self, "AHKDelay" + str(i), 10)

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")
        return

    def Save(self, SettingsFile):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)
    ScriptSettings.Save(SettingsFile)

    global RefreshToken
    global AccessToken
    global TokenExpiration
    if os.path.isfile(RefreshTokenFile):
        with open(RefreshTokenFile) as f:
            content = f.readlines()
        if len(content) > 0:
            data = json.loads(content[0])
            RefreshToken = data["refresh_token"]
            AccessToken = data["access_token"]
            TokenExpiration = datetime.datetime.strptime(data["expiration"], "%Y-%m-%d %H:%M:%S.%f")

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):

    if data.IsChatMessage() and Parent.HasPermission(data.User,"Moderator",""):
        for i in range(1, 2):
            resetCommand = getattr(ScriptSettings, "ResetCommand" + str(i))
            rewardType = getattr(ScriptSettings, "RewardType" + str(i))
            if "Countdown Overlay" in rewardType and resetCommand.lower() in data.Message.lower():
                if ScriptSettings.EnableDebug:
                    Parent.Log(ScriptName, "Resetting countdown")
                length = getattr(ScriptSettings, "CountdownLength" + str(i))
                type = "reset"
                if data.GetParamCount() > 1:
                    length = int(data.GetParam(1))
                    type = "add"
                payload = {
                    "title": getattr(ScriptSettings, "CountdownTitle" + str(i)),
                    "interval": length,
                    "type": type,
                    "redeemedSFXPath": getattr(ScriptSettings, "RedeemedSFXPath" + str(i)),
                    "redeemedSFXVolume": getattr(ScriptSettings, "RedeemedSFXVolume" + str(i))/100.0,
                    "finishedSFXPath": getattr(ScriptSettings, "FinishedSFXPath" + str(i)),
                    "finishedSFXVolume": getattr(ScriptSettings, "FinishedSFXVolume" + str(i))/100.0
                }
                Parent.BroadcastWsEvent("EVENT_RESET_" + str(i),json.dumps(payload, encoding='utf-8-sig'))

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    if LastTokenCheck is None:
        return

    if (EventReceiver is None or TokenExpiration < datetime.datetime.now()) and LastTokenCheck + datetime.timedelta(seconds=60) < datetime.datetime.now(): 
        RestartEventReceiver()
        return

    global PlayNextAt
    if PlayNextAt > datetime.datetime.now():
        return

    global CurrentThread
    if CurrentThread and CurrentThread.isAlive() == False:
        CurrentThread = None

    if CurrentThread == None and len(ThreadQueue) > 0:
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Starting new thread. " + str(PlayNextAt))
        CurrentThread = ThreadQueue.pop(0)
        CurrentThread.start()
        
    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString

#---------------------------
#   [Optional] Reload Settings (Called when a user clicks the Save Settings button in the Chatbot UI)
#---------------------------
def ReloadSettings(jsonData):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Saving settings.")

    try:
        ScriptSettings.__dict__ = json.loads(jsonData)
        ScriptSettings.Save(SettingsFile)

        threading.Thread(target=RestartEventReceiver).start()

        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Settings saved successfully")
    except Exception as e:
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, str(e))

    return

#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    StopEventReceiver()
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    if state:
        if EventReceiver is None:
            threading.Thread(target=RestartEventReceiver).start()
    else:
        StopEventReceiver()

    return

#---------------------------
#   StartEventReceiver (Start twitch pubsub event receiver)
#---------------------------
def StartEventReceiver():
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Starting receiver")

    global EventReceiver
    EventReceiver = TwitchPubSub()
    EventReceiver.OnPubSubServiceConnected += EventReceiverConnected
    EventReceiver.OnRewardRedeemed += EventReceiverRewardRedeemed

    EventReceiver.Connect()

#---------------------------
#   StopEventReceiver (Stop twitch pubsub event receiver)
#---------------------------
def StopEventReceiver():
    global EventReceiver
    try:
        if EventReceiver:
            EventReceiver.Disconnect()
            if ScriptSettings.EnableDebug:
                Parent.Log(ScriptName, "Event receiver disconnected")
        EventReceiver = None

    except:
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Event receiver already disconnected")

#---------------------------
#   RestartEventReceiver (Restart event receiver cleanly)
#---------------------------
def RestartEventReceiver():
    RefreshTokens()
    if InvalidRefreshToken is False:
        if UserID is None:
            GetUserID()
        StopEventReceiver()
        StartEventReceiver()

#---------------------------
#   EventReceiverConnected (Twitch pubsub event callback for on connected event. Needs a valid UserID and AccessToken to function properly.)
#---------------------------
def EventReceiverConnected(sender, e):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Event receiver connected, sending topics for channel id: " + str(UserID))

    EventReceiver.ListenToRewards(UserID)
    EventReceiver.SendTopics(AccessToken)
    return

#---------------------------
#   EventReceiverRewardRedeemed (Twitch pubsub event callback for a detected redeemed channel point reward.)
#---------------------------
def EventReceiverRewardRedeemed(sender, e):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Event triggered: " + str(e.TimeStamp) + " ChannelId: " + str(e.ChannelId) + " Login: " + str(e.Login) + " DisplayName: " + str(e.DisplayName) + " Message: " + str(e.Message) + " RewardId: " + str(e.RewardId) + " RewardTitle: " + str(e.RewardTitle) + " RewardPrompt: " + str(e.RewardPrompt) + " RewardCost: " + str(e.RewardCost) + " Status: " + str(e.Status))

    for i in range(1, 2):
        Parent.Log(ScriptName, str(i))
        if e.RewardTitle == getattr(ScriptSettings, "RewardName" + str(i)):
            rewardType = getattr(ScriptSettings, "RewardType" + str(i))
            activationType = getattr(ScriptSettings, "RewardActivationType" + str(i))
            if (activationType == "Immediate" and "FULFILLED" in e.Status) or (activationType == r"On Reward Queue Accept/Reject" and "ACTION_TAKEN" in e.Status):
                if "Alert - Gif and/or SFX" in rewardType:
                    ThreadQueue.append(threading.Thread(target=AlertRewardWorker,args=(
                        i, 
                        getattr(ScriptSettings, "AlertMediaPath" + str(i)), 
                        getattr(ScriptSettings, "AlertSFXPath" + str(i)), 
                        getattr(ScriptSettings, "AlertSFXVolume" + str(i)), 
                        getattr(ScriptSettings, "AlertSFXDelay" + str(i)),
                        getattr(ScriptSettings, "AlertText" + str(i)),
                        )))
                elif "Countdown Overlay" in rewardType:
                    ThreadQueue.append(threading.Thread(target=CountdownRewardWorker,args=(
                        i, 
                        getattr(ScriptSettings, "CountdownTitle" + str(i)), 
                        getattr(ScriptSettings, "CountdownLength" + str(i)),
                        getattr(ScriptSettings, "RedeemedSFXPath" + str(i)), 
                        getattr(ScriptSettings, "RedeemedSFXVolume" + str(i)), 
                        getattr(ScriptSettings, "RedeemedSFXDelay" + str(i)), 
                        getattr(ScriptSettings, "FinishedSFXPath" + str(i)), 
                        getattr(ScriptSettings, "FinishedSFXVolume" + str(i)), 
                        )))
                elif "Timeout User" in rewardType:
                    timeoutType = getattr(ScriptSettings, "TimeoutType" + str(i))
                    duration = getattr(ScriptSettings, "TimeoutDuration" + str(i))

                    user = ""
                    if timeoutType == "Fixed":
                        user = getattr(ScriptSettings, "TimeoutFixedUser" + str(i))
                    elif timeoutType == "Reward Redeemer":
                        user = e.Login
                    elif timeoutType == "Reward Message":
                        user = e.Message

                    TimeoutRewardWorker(user, duration)
                elif "Convert Channel Points to Currency" in rewardType:
                    amount = 0
                    useRewardCost = bool(getattr(ScriptSettings, "UseRewardCost" + str(i)))
                    if useRewardCost == True:
                        amount = long(e.RewardCost)
                    else:
                        amount = long(getattr(ScriptSettings, "CurrencyAmount" + str(i)))

                    ConvertToCurrencyRewardWorker(e.Login, e.DisplayName, amount)
                elif "AutoHotkey" in rewardType:
                    ThreadQueue.append(threading.Thread(target=AutoHotkeyRewardWorker,args=(
                        getattr(ScriptSettings, "AHKDelay" + str(i)), 
                        getattr(ScriptSettings, "AHKPath" + str(i)), 
                        getattr(ScriptSettings, "AHKArguments" + str(i)),
                        )))
    return

#---------------------------
#   AlertRewardWorker (Worker function for Alert Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def AlertRewardWorker(number, mediapath, sfxpath, volume, delay, text):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, mediapath + " " + sfxpath + " " + str(volume) + " " + str(delay))

    Parent.PlaySound(sfxpath, volume/100.0)
    global PlayNextAt
    PlayNextAt = datetime.datetime.now() + datetime.timedelta(0, delay)

    payload = { 
        "path": mediapath,
        "text": text 
    }

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, str(payload))
    
    Parent.BroadcastWsEvent('EVENT_ALERT_' + str(number) + '_REDEEMED', json.dumps(payload, encoding='utf-8-sig'))

#---------------------------
#   CountdownRewardWorker (Worker function for Countdown Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def CountdownRewardWorker(number, title, seconds, path, volume, delay, finishedpath, finishedvolume):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, path + " " + str(volume/100.0) + " " + str(delay))

    global PlayNextAt
    PlayNextAt = datetime.datetime.now() + datetime.timedelta(0, delay)

    payload = { 
        "title": title,
        "seconds": seconds, 
        "redeemedSFXPath": path,
        "redeemedSFXVolume": volume/100.0,
        "finishedSFXPath": finishedpath,
        "finishedSFXVolume": finishedvolume/100.0
    }

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, str(payload))
    
    Parent.BroadcastWsEvent('EVENT_COUNTDOWN_' + str(number) + '_REDEEMED', json.dumps(payload, encoding='utf-8-sig'))

#---------------------------
#   TimeoutRewardWorker (Worker function for Timeout/Ban Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def TimeoutRewardWorker(username, duration):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, username + " " + str(duration))

    Parent.SendStreamMessage("/timeout " + username + " " + str(duration))

#---------------------------
#   ConvertToCurrencyRewardWorker (Worker function for Alert Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def ConvertToCurrencyRewardWorker(user, username, amount):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, user + " " + username + " " + str(amount))

    Parent.AddPoints(user, username, amount)

#---------------------------
#   AutoHotkeyRewardWorker (Worker function for AutoHotkey Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def AutoHotkeyRewardWorker(delay, script, args = None):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, script + " " + str(delay) + " " + str(args))

    if args is None:
        os.startfile(script)
    else:
        AHK = os.path.join(ScriptSettings.AHKPath, "AutoHotkey.exe")
        args.insert(0,script)
        os.spawnv(os.P_NOWAIT, AHK, args)

    global PlayNextAt
    PlayNextAt = datetime.datetime.now() + datetime.timedelta(0, delay)


#---------------------------
#   RefreshTokens (Called when a new access token needs to be retrieved.)
#---------------------------
def RefreshTokens():
    global RefreshToken
    global AccessToken
    global TokenExpiration
    global LastTokenCheck
    global InvalidRefreshToken
    global InvalidAuthCode

    InvalidRefreshToken = False

    result = None

    try:
        if RefreshToken:
            content = {
                "client_id": ScriptSettings.TwitchClientId,
                "client_secret": ScriptSettings.TwitchClientSecret,
	            "grant_type": "refresh_token",
	            "refresh_token": str(RefreshToken)
            }

            result = json.loads(json.loads(Parent.PostRequest("https://api.et-twitch-auth.com/",{}, content, True))["response"])
            if ScriptSettings.EnableDebug:
                Parent.Log(ScriptName, str(content))
        else:
            if ScriptSettings.TwitchAuthCode == "":
                LastTokenCheck = datetime.datetime.now()
                TokenExpiration = datetime.datetime.now()
                Parent.Log(ScriptName, "Access code cannot be retrieved please enter a valid authorization code.")
                InvalidRefreshToken = True
                return

            content = {
                "client_id": ScriptSettings.TwitchClientId,
                "client_secret": ScriptSettings.TwitchClientSecret,
                'grant_type': 'authorization_code',
                'code': ScriptSettings.TwitchAuthCode
            }

            result = json.loads(json.loads(Parent.PostRequest("https://api.et-twitch-auth.com/",{}, content, True))["response"])
            if ScriptSettings.EnableDebug:
                Parent.Log(ScriptName, str(content))

        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, str(result))

        RefreshToken = result["refresh_token"]
        AccessToken = result["access_token"]
        TokenExpiration = datetime.datetime.now() + datetime.timedelta(seconds=int(result["expires_in"]) - 300)

        LastTokenCheck = datetime.datetime.now()
        SaveTokens()
    except Exception as e:
        LastTokenCheck = datetime.datetime.now()
        TokenExpiration = datetime.datetime.now()
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Exception: " + str(e.message))
        InvalidRefreshToken = True

#---------------------------
#   GetUserID (Calls twitch's api with current channel user name to get the user id and sets global UserID variable.)
#---------------------------
def GetUserID():
    headers = { 
        "Client-ID": ScriptSettings.TwitchClientId,
        "Authorization": "Bearer " + AccessToken
    }
    result = json.loads(Parent.GetRequest("https://api.twitch.tv/helix/users?login=" + Parent.GetChannelName(), headers))
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "headers: " + str(headers))
        Parent.Log(ScriptName, "result: " + str(result))
    user = json.loads(result["response"])
    global UserID
    UserID = user["data"][0]["id"]

#---------------------------
#   SaveTokens (Saves tokens and expiration time to a json file in script bin for use on script restart and reload.)
#---------------------------
def SaveTokens():
    data = {
        "refresh_token": RefreshToken,
        "access_token": AccessToken,
        "expiration": str(TokenExpiration)
    }

    with open(RefreshTokenFile, 'w') as f:
        f.write(json.dumps(data))

#---------------------------
#   OpenReadme (Attached to settings button to open the readme file in the script bin.)
#---------------------------
def OpenReadme():
    os.startfile(ReadMe)

#---------------------------
#   GetToken (Attached to settings button to open a page in browser to get an authorization code.)
#---------------------------
def GetToken():
    if ScriptSettings.TwitchRedirectUrl == "" or ScriptSettings.TwitchClientId == "":
        return

    redirectUrl = ScriptSettings.TwitchRedirectUrl
    if redirectUrl[-1:] != "/":
        redirectUrl += "/"

    os.startfile("https://id.twitch.tv/oauth2/authorize?response_type=code&client_id=" + ScriptSettings.TwitchClientId + "&redirect_uri=" + redirectUrl + "&scope=channel:read:redemptions&force_verify=true")

#---------------------------
#   DeleteSavedTokens (Attached to settings button to allow user to easily delete the tokens.json file and clear out RefreshToken currently in memory so that a new authorization code can be entered and used.)
#---------------------------
def DeleteSavedTokens():
    global RefreshToken
    if os.path.exists(RefreshTokenFile):
        os.remove(RefreshTokenFile)
    RefreshToken = None