#!/usr/bin/python
# -*- coding: utf-8 -*-

import ch
import time
import collections
import re
import urllib2
import random
import urllib
import json
import requests
import fvbotauth

ggpoSelectedList = ["Breakers Revenge","Garou","Jojo's Bizarre Adventure","Karnovs Revenge", \
                      "King of Fighters 2002","King of Fighters 98","Last Blade 2","Marvel Super Heroes", \
                      "Marvel Super Heroes vs Street Fighter","Real Bout Fatal Fury 2", \
                      "Street Fighter Alpha 2","Street Fighter Alpha 3","Street Fighter 3: 3RD Strike", \
                      "Super Street Fighter II X: GRAND MASTER CHALLENGE","Vampire Savior", \
                      "X-Men vs Street Fighter"]
                      
imgRegex = "(?P<url>(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:jpg|gif|png))(?:\?([^#]*))?(?:#(.*))?)"

class FVBot(ch.RoomManager):

  def onConnect(self, room):
    print("Connected to "+room.name)
    self.savedMsgs = collections.deque(["Howdy"], 5)
    self.userQue = collections.deque(["FVBot"], 5)
    self.dotaShameList = None
    self.activeUsers = []
    self.msgSetTime = time.time()
    self.actionTime = None
    self.setNameColor("E90")
    self.setFontColor("E90")
    random.seed()

  def onReconnect(self, room):
    print("Reconnected to "+room.name)

  def onDisconnect(self, room):
    print("Disconnected from "+room.name)

  def onMessage(self, room, user, message):
    # Use with PsyfrBot framework? :3
    self.safePrint(user.name + ': ' + message.body)
    #print(message.body.encode("utf-8"))
    #if self.actionTime:
    #    self.safePrint("{0}".format(time.time() - self.actionTime))
    
    self.CheckActiveUsers(user)

    if (not self.actionTime) or (time.time() - self.actionTime > 1):
        #self.safePrint("inside if")
        msgPrint = False
    
        matchObj = re.match(imgRegex, message.body)
        
        if message.body.startswith("!callout"):
          room.message(self.CalloutMsg(user, message))
          msgPrint = True
        elif message.body.startswith("!waterhistory"):
          finalMsg = ""
          for msg in zip(self.savedMsgs, self.userQue):
            finalMsg = u"{0}'{1}' (by {2}) || ".format(finalMsg, msg[0], msg[1]) 
          room.message(finalMsg)
          msgPrint = True
        elif message.body.startswith("!waterset"):
          msg = message.body.replace("!waterset", "")
          msg = msg.strip()
          if msg == "" or len(msg) > 150 or msg.startswith("!"):
            room.message(u"Stop being a cunt {0}".format(user.name))
            msgPrint = True
          else:
            self.savedMsgs.appendleft(msg)
            self.userQue.appendleft(user.name)
            self.msgSetTime = time.time()
            room.message(u"Message is now {0}".format(self.savedMsgs[0]))
            msgPrint = True
        elif message.body.startswith("!water"):
          timeNow = time.time() - self.msgSetTime
          room.message(u"{0} (Set {1} ago by {2})".format(
                                        self.savedMsgs[0], 
                                        time.strftime("%Hh%Mm%Ss", time.gmtime(timeNow)),
                                        self.userQue[0]))
          msgPrint = True
        elif message.body.startswith("!ggpo"):
          game = self.SelectGGPOGame(message)
          room.message(u"{0}".format(game))
          msgPrint = True
        elif matchObj:
          imgUrl = self.GetImgUrl(matchObj.group("url"))
          if imgUrl:
            if self.DetermineImgSize(imgUrl):
              try:
                shortImgUrl = self.ShortenImgUrl(matchObj.group("url"))
                room.message(u"Alt img link: {0}".format(shortImgUrl))
                msgPrint = True
              except urllib2.URLError, e:
                self.safePrint(e.reason)
              except urllib2.HTTPError, e:
                self.safePrint(u"onMessage (matchobj): HTTPError: {0}".format(e.code))
              except ValueError, e:
                self.safePrint(u"onMessage (matchObj): ValueError on Img URL")
          
        if msgPrint:
            self.actionTime = time.time()
        

  def onFloodBan(self, room):
    print("You are flood banned in "+room.name)

  def onPMMessage(self, pm, user, body):
    self.safePrint('PM: ' + user.name + ': ' + body)
    pm.message(user, body) # echo
    
  def make_unicode(self, input):
    if type(input) != unicode:
        input =  input.decode('utf-8')
        return input
    else:
        return input
        
  def CalloutMsg(self, user, message):
     msg = message.body.replace("!callout", "")
     msg = msg.strip()
     if len(self.activeUsers) > 1:
         if len(msg) > 150:
           return u"Stop {0}".format(user.name)
         else:
           max = len(self.activeUsers)-1
           rand = random.randint(0, max)
           while(self.activeUsers[rand][0] == user.name):
             rand = random.randint(0, max)
           self.safePrint(msg)
           if msg.startswith("!ggpo"):
             msg = self.SelectGGPOGame(msg)
           return u"{0} calls out {1} in {2} FT5".format(user.name, self.activeUsers[rand][0], msg)
     else:
        return u"No one to callout!"
       
  def CheckActiveUsers(self, user):
      seen = False
      for index, activeUser in enumerate(self.activeUsers):
        if (user.name == activeUser[0]):
          self.activeUsers[index][1] = time.time()
          seen = True
        if time.time() - activeUser[1] > 1800:   #30 mins
          del self.activeUsers[index]
        
      if (not seen) and (user.name != "fvbot"):
        self.activeUsers.append([user.name, time.time()])
      
      #msg = ""
      #for activeUser in self.activeUsers:
       # msg = "{0}[{1},{2}],".format(msg, activeUser[0], time.time() - activeUser[1])
        
      #self.safePrint(msg)
      
  def ShortenImgUrl(self, url):
    singleUrl = url.split(" ")[0]
    self.safePrint(singleUrl)
    apiStr = "http://tinyurl.com/api-create.php?url={0}".format(singleUrl)
    try:
      return urllib2.urlopen(apiStr).read()
    except:
      raise
      
    
  def GetImgUrl(self, urlString):
    splitString = urlString.split(" ")
    url = None
    for item in splitString:
      if re.match(imgRegex, item):
        url = item
        break
    #self.safePrint(url)
    return url
    
  def DetermineImgSize(self, url):
    try:
      file = urllib2.urlopen(url)
      codeStr = str(file.getcode())
      if codeStr == "200":
      
        infoDict = file.info().items()
        size = None
        for key,value in infoDict:
          if key == "content-length":
            size = int(value)
            break
        
        #self.safePrint(size)
        if size and size > 999999: #more than 1mb
          return True
        else:
          return False
          
      else:
        return False
    except urllib2.URLError, e:
      self.safePrint(e.reason)
      return False
    except urllib2.HTTPError, e:
      self.safePrint(u"DetermineImgSize: HTTPError: {0}".format(e.code))
      return False
    except ValueError, e:
      self.safePrint(u"ValueError on Img URL")
      return False
    
  def SelectGGPOGame(self, message):
    rand = random.randint(0, len(ggpoSelectedList)-1)
    return ggpoSelectedList[rand]
    
    
    
          

if __name__ == "__main__":
  FVBot.easy_start(["fv-se"], fvbotauth.FVBOT_USER, fvbotauth.FVBOT_PASS, True)
  #FVBot.easy_start(["sfcii-hdr-ce"], fvbotauth.FVBOT_USER, fvbotauth.FVBOT_PASS, True)
