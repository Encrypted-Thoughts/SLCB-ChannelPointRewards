# -*- coding: utf-8 -*-

import json, os, random

class Alert(object):
    def __init__(self, ScriptName, Parent, EnableDebug = False):
        self.Parent = Parent
        self.ScriptName = ScriptName
        self.EnableDebug = EnableDebug

    def ActivateAlert(self, number, mediapath, sfxpath, volume, text):
        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, mediapath + " " + sfxpath + " " + str(volume))

        sfxfile = sfxpath
        if os.path.isdir(sfxpath):
            sfxfile = sfxpath + "\\" + random.choice(os.listdir(sfxpath))

        mediafile = mediapath
        if os.path.isdir(mediapath):
            mediafile = mediapath + "\\" + random.choice(os.listdir(mediapath))

        self.Parent.PlaySound(sfxfile, volume/100.0)

        payload = { 
            "path": mediafile,
            "text": text 
        }

        if self.EnableDebug:
            self.Parent.Log(self.ScriptName, str(payload))
    
        self.Parent.BroadcastWsEvent('EVENT_ALERT_' + str(number) + '_REDEEMED', json.dumps(payload, encoding='utf-8-sig'))
