# -*- coding: utf-8 -*-

import codecs, json, os, re, math, datetime

class BanWord(object):

    BlacklistFile = os.path.join(os.path.dirname(__file__), "blacklist.json")
    Blacklist = []

    def __init__(self, ScriptName, Parent, EnableDebug = False):
        self.Parent = Parent
        self.ScriptName = ScriptName
        self.EnableDebug = EnableDebug

        if os.path.isfile(self.BlacklistFile):
            with open(self.BlacklistFile) as f:
                content = f.readlines()
            for item in content:
                data = item.split(",")
                word = data[0]
                time = datetime.datetime.strptime(data[1], "%Y-%m-%d %H:%M:%S.%f")
                self.Blacklist.append((word, time))

    def RefreshList(self, expirationMessage):
        updatedList = []
        changed = False
        for item in self.Blacklist:
            if item[1] < datetime.datetime.now():
                if expirationMessage and expirationMessage.strip() != "":
                    self.Parent.SendStreamMessage(expirationMessage.replace("{word}", item[0]))
                changed = True
            else:
                updatedList.append(item)

        if changed:
            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, "Blacklist changed.")
            self.Blacklist = updatedList
            self.Save()

    def ParseForBannedWords(self, data, censorPhrase, triggerMsg):
        searchRegex = "\\b("
        for item in self.Blacklist:
                searchRegex += re.escape(item[0]) + "|"
        if searchRegex == "\\b(":
            return
        searchRegex = searchRegex[:-1] + ")\\b"

        message = data.Message
        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, "Regex search string: " + searchRegex)
            self.Parent.Log(self.ScriptName, data.RawData)
        matches = re.findall(searchRegex, message, re.IGNORECASE)

        if len(matches) == 0:
            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, "No match found in message.")
            return 

        id = re.search(";id=([^,;]+);", data.RawData)

        if id is None:
            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, "No id found in message.")
            return

        for item in matches:
            message = message.replace(item, censorPhrase)

        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, "Ids Found: " + id.group(1) + "Match Count: " + str(len(matches)))

        self.Parent.SendStreamMessage("/delete " + id.group(1))

        if triggerMsg and triggerMsg.strip() != "":
            self.Parent.SendStreamMessage(triggerMsg.replace("{username}", data.UserName).replace("{msg}", message))


    #---------------------------
    #   AddWord (Adds a word to the list of words to be blacklisted from chat.)
    #---------------------------
    def AddWord(self, username, userMessage, duration, fixedWord, redeemMessage):
        word = userMessage
        if fixedWord and fixedWord.strip() != "":
            word = fixedWord

        item = (word.strip(), datetime.datetime.now() + datetime.timedelta(0, duration))
        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, str(item))
        self.Blacklist.append(item)
        self.Save()

        message = redeemMessage.replace("{username}", username)
        message = message.replace("{word}", word)
        message = message.replace("{seconds}", str(duration))
        message = message.replace("{minutes}", str(math.trunc(duration/60.0)))
        message = message.replace("{hours}", str(math.trunc(duration/3600.0)))
        message = message.replace("{days}", str(math.trunc(duration/86400.0)))

        if message and message.strip() != "":
            self.Parent.SendStreamMessage(message)

    #---------------------------
    #   Save (Saves list of banned words to file for use on script restart and reload)
    #---------------------------
    def Save(self):
        with open(self.BlacklistFile, 'w') as f:
            for item in self.Blacklist:
                f.write(str(item[0]) + "," + str(item[1]) + "\n")