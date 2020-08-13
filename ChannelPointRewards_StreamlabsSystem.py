# -*- coding: utf-8 -*-

#---------------------------
#   Import Libraries
#---------------------------
import clr, codecs, json, os, re, sys, threading, datetime, math, random, System
random = random.WichmannHill()

# Include the assembly with the name AnkhBotR2
clr.AddReference([asbly for asbly in System.AppDomain.CurrentDomain.GetAssemblies() if "AnkhBotR2" in str(asbly)][0])
import AnkhBotR2

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(__file__) + "\Rewards")
import BanWord, Countdown, Alert

clr.AddReference("IronPython.Modules.dll")
clr.AddReference("System.Windows.Forms")
clr.AddReferenceToFileAndPath(os.path.join(os.path.dirname(os.path.realpath(__file__)) + "\References", r"TwitchLib.PubSub.dll"))
from TwitchLib.PubSub import TwitchPubSub
from System.Windows.Forms import SendKeys

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
ReadMe = os.path.join(os.path.dirname(__file__), "README.md")
EventReceiver = None
ThreadQueue = []
CurrentThread = None
PlayNextAt = datetime.datetime.now()

RewardCount = 10

#Rewards
BanWordReward = None
CountdownReward = None
AlertReward = None

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

            for i in range(1, RewardCount + 1):
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
                setattr(self, "ResetCommand" + str(i), "!reset" + str(i))
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

                setattr(self, "BlacklistDuration" + str(i), 3600)
                setattr(self, "FixedWord" + str(i), "")
                setattr(self, "RedeemMessage" + str(i), "{username} has decreed that {word} shall not be used for {hours} hours!")
                setattr(self, "ExpirationMessage" + str(i), "{word} is now unlocked!")
                setattr(self, "TriggerMessage" + str(i), "{username} Said: {msg}")
                setattr(self, "CensorPhrase" + str(i), "[REDACTED]")

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

    global BanWordReward
    BanWordReward = BanWord.BanWord(ScriptName, Parent, ScriptSettings.EnableDebug)

    global CountdownReward
    CountdownReward = Countdown.Countdown(ScriptName, Parent, ScriptSettings.EnableDebug)

    global AlertReward
    AlertReward = Alert.Alert(ScriptName, Parent, ScriptSettings.EnableDebug)

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):

    for i in range(1, RewardCount + 1):
        rewardType = getattr(ScriptSettings, "RewardType" + str(i))

        if "Ban Word" in rewardType:
            BanWordReward.RefreshList(getattr(ScriptSettings, "ExpirationMessage" + str(i)))

        if data.IsChatMessage() and data.IsFromTwitch():
            if Parent.HasPermission(data.User,"Moderator","") and "Countdown Overlay" in rewardType:
                CountdownReward.ResetCommand( 
                    i,
                    data,
                    getattr(ScriptSettings, "ResetCommand" + str(i)),
                    getattr(ScriptSettings, "CountdownLength" + str(i)),
                    getattr(ScriptSettings, "CountdownTitle" + str(i)),
                    getattr(ScriptSettings, "RedeemedSFXPath" + str(i)),
                    getattr(ScriptSettings, "RedeemedSFXVolume" + str(i)),
                    getattr(ScriptSettings, "FinishedSFXPath" + str(i)),
                    getattr(ScriptSettings, "FinishedSFXVolume" + str(i)))

            if "Ban Word" in rewardType:
                BanWordReward.ParseForBannedWords(
                    data, 
                    getattr(ScriptSettings, "CensorPhrase" + str(i)),
                    getattr(ScriptSettings, "TriggerMessage" + str(i)))

    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    global PlayNextAt
    global CurrentThread
    if CurrentThread is not None and CurrentThread["thread"].isAlive() == False:
        PlayNextAt = datetime.datetime.now() + datetime.timedelta(0, CurrentThread["delay"])
        CurrentThread = None
        Parent.Log(ScriptName, str(PlayNextAt))

    if PlayNextAt > datetime.datetime.now():
        return

    if CurrentThread is None and len(ThreadQueue) > 0:
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Starting new thread. " + str(PlayNextAt))
        CurrentThread = ThreadQueue.pop(0)
        CurrentThread["thread"].start()
        
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
        Init()

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
    BanWordReward.Save()
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
        BanWordReward.Save()
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
    StopEventReceiver()
    StartEventReceiver()

#---------------------------
#   EventReceiverConnected (Twitch pubsub event callback for on connected event. Needs a valid UserID and AccessToken to function properly.)
#---------------------------
def EventReceiverConnected(sender, e):
    oauth = AnkhBotR2.Managers.GlobalManager.Instance.VMLocator.StreamerLogin.Token.replace("oauth:", "")

    headers = { "Authorization": 'OAuth ' + oauth }
    data = json.loads(Parent.GetRequest("https://id.twitch.tv/oauth2/validate", headers))

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, str(data))

    userid = json.loads(data["response"])['user_id']

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Event receiver connected, sending topics for channel id: " + str(userid))

    EventReceiver.ListenToRewards(userid)
    EventReceiver.SendTopics(oauth)
    return

#---------------------------
#   EventReceiverRewardRedeemed (Twitch pubsub event callback for a detected redeemed channel point reward.)
#---------------------------
def EventReceiverRewardRedeemed(sender, e):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Event triggered: " + str(e.TimeStamp) + " ChannelId: " + str(e.ChannelId) + " Login: " + str(e.Login) + " DisplayName: " + str(e.DisplayName) + " Message: " + str(e.Message) + " RewardId: " + str(e.RewardId) + " RewardTitle: " + str(e.RewardTitle) + " RewardPrompt: " + str(e.RewardPrompt) + " RewardCost: " + str(e.RewardCost) + " Status: " + str(e.Status))

    for i in range(1, RewardCount + 1):
        #Parent.Log(ScriptName, str(i))
        if e.RewardTitle == getattr(ScriptSettings, "RewardName" + str(i)):
            rewardType = getattr(ScriptSettings, "RewardType" + str(i))
            activationType = getattr(ScriptSettings, "RewardActivationType" + str(i))
            if (activationType == "Immediate" and "FULFILLED" in e.Status) or (activationType == r"On Reward Queue Accept/Reject" and "ACTION_TAKEN" in e.Status):
                if "Alert - Gif and/or SFX" in rewardType:
                    ThreadQueue.append({
                            "thread": threading.Thread(target=AlertReward.ActivateAlert,args=(
                                i, 
                                getattr(ScriptSettings, "AlertMediaPath" + str(i)), 
                                getattr(ScriptSettings, "AlertSFXPath" + str(i)), 
                                getattr(ScriptSettings, "AlertSFXVolume" + str(i)), 
                                getattr(ScriptSettings, "AlertText" + str(i))
                            )),
                            "delay": getattr(ScriptSettings, "AlertSFXDelay" + str(i))
                        })
                elif "Countdown Overlay" in rewardType:
                    ThreadQueue.append({
                            "thread": threading.Thread(target=CountdownReward.ActivateCountdown,args=(
                                i, 
                                getattr(ScriptSettings, "CountdownTitle" + str(i)), 
                                getattr(ScriptSettings, "CountdownLength" + str(i)),
                                getattr(ScriptSettings, "RedeemedSFXPath" + str(i)), 
                                getattr(ScriptSettings, "RedeemedSFXVolume" + str(i)), 
                                getattr(ScriptSettings, "FinishedSFXPath" + str(i)), 
                                getattr(ScriptSettings, "FinishedSFXVolume" + str(i))
                            )),
                            "delay": getattr(ScriptSettings, "RedeemedSFXDelay" + str(i))
                        })
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

                    if Parent.HasPermission(user, "Moderator", "") == False:
                        Parent.SendStreamMessage("/timeout " + user + " " + str(duration))
                elif "Convert Channel Points to Currency" in rewardType:
                    amount = 0
                    useRewardCost = bool(getattr(ScriptSettings, "UseRewardCost" + str(i)))
                    if useRewardCost == True:
                        amount = long(e.RewardCost)
                    else:
                        amount = long(getattr(ScriptSettings, "CurrencyAmount" + str(i)))

                    Parent.AddPoints(e.Login, e.DisplayName, amount)
                elif "AutoHotkey" in rewardType:
                    params = getattr(ScriptSettings, "AHKArguments" + str(i))
                    params = params.replace("{username}", str(e.DisplayName))
                    params = params.replace("{message}", str(e.Message))
                    params = params.replace("{rewardtitle}", str(e.RewardTitle))
                    params = params.replace("{rewardcost}", str(e.RewardCost))
                    params = params.replace("{timestamp}", str(e.TimeStamp))
                    ThreadQueue.append({
                        "thread": threading.Thread(target=AutoHotkeyRewardWorker,args=(
                            getattr(ScriptSettings, "AHKPath" + str(i)), 
                            params,
                        )),
                        "delay": getattr(ScriptSettings, "AHKDelay" + str(i))
                    })
                elif "Ban Word" in rewardType:
                    Parent.Log(ScriptName, "Ban Word")
                    ThreadQueue.append({
                        "thread": threading.Thread(target=BanWordReward.AddWord,args=(
                            e.DisplayName, 
                            e.Message, 
                            getattr(ScriptSettings, "BlacklistDuration" + str(i)),
                            getattr(ScriptSettings, "FixedWord" + str(i)),
                            getattr(ScriptSettings, "RedeemMessage" + str(i)),
                        )),
                        "delay": 0
                    })
    return

#---------------------------
#   AutoHotkeyRewardWorker (Worker function for AutoHotkey Rewards to be spun off into its own thread to complete without blocking the rest of script execution.)
#---------------------------
def AutoHotkeyRewardWorker(script, args):
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, ScriptSettings.AHKExePath + " " + script + " " + args)

    os.system('"' + ScriptSettings.AHKExePath + '" "' + script + '" ' + args)

#---------------------------
#   OpenReadme (Attached to settings button to open the readme file in the script bin.)
#---------------------------
def OpenReadme():
    os.startfile(ReadMe)

#---------------------------
#   PageDown (Pages down to the bottom of settings.)
#---------------------------
def PageDown():
    for i in range(1, RewardCount + 3):
        SendKeys.SendWait("{PGDN}")

#---------------------------
#   PageDown (Pages down to the bottom of settings.)
#---------------------------
def PageUp():
    for i in range(1, RewardCount + 3):
        SendKeys.SendWait("{PGUP}")