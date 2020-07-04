# -*- coding: utf-8 -*-

import json, os, random

class Countdown(object):
    def __init__(self, ScriptName, Parent, EnableDebug = False):
        self.Parent = Parent
        self.ScriptName = ScriptName
        self.EnableDebug = EnableDebug

    def ResetCommand(self, number, data, resetCommand, countdownLength, title, redeemedPath, redeemedVolume, finishedPath, finishedVolume):
        if resetCommand.lower() in data.Message.lower():
            if self.EnableDebug:
                self.Parent.Log(self.ScriptName, "Resetting countdown")
            length = countdownLength
            type = "reset"
            if data.GetParamCount() > 1:
                length = int(data.GetParam(1))
                type = "add"
            payload = {
                "title": title,
                "interval": length,
                "type": type,
                "redeemedSFXPath": redeemedPath,
                "redeemedSFXVolume": redeemedVolume/100.0,
                "finishedSFXPath": finishedPath,
                "finishedSFXVolume": finishedVolume/100.0
            }
            self.Parent.BroadcastWsEvent("EVENT_RESET_" + str(number),json.dumps(payload, encoding='utf-8-sig'))

    def ActivateCountdown(self, number, title, seconds, redeemedPath, redeemedVolume, finishedpath, finishedvolume):
        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, redeemedPath + " " + str(redeemedVolume/100.0))

        sfxfile1 = redeemedPath
        if os.path.isdir(redeemedPath):
            sfxfile1 = redeemedPath + "\\" + random.choice(os.listdir(redeemedPath))

        sfxfile2 = finishedpath
        if os.path.isdir(finishedpath):
            sfxfile2 = finishedpath + "\\" + random.choice(os.listdir(finishedpath))

        payload = { 
            "title": title,
            "seconds": seconds, 
            "redeemedSFXPath": sfxfile1,
            "redeemedSFXVolume": redeemedVolume/100.0,
            "finishedSFXPath": sfxfile2,
            "finishedSFXVolume": finishedvolume/100.0
        }

        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, str(payload))
    
        self.Parent.BroadcastWsEvent('EVENT_COUNTDOWN_' + str(number) + '_REDEEMED', json.dumps(payload, encoding='utf-8-sig'))
