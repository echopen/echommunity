#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------
# (c) kelu124
# cc-by-sa/4.0/
# -------------------------
# Examining slack log files
# Creates channel-wise jsons
# Creates a main MainJSON.json file for all information
# -------------------------

import re	
import subprocess
import os
from os import walk
import json

MainJSON = []

# List of keywords
Hardware = ["pcb","fpga","electronic","cpld","stm32","arduino","kicad","tgc","adc","hardware"]
Software = ["android","java","code","python","script","merge","software",'app',"gpu", "machine learning","neural"]
Legal = ["patent", "agreement", "cla","licence","license","legal","copyright"] 
Medical = ["doctor", "patient",'médecin',"medical"]
Design = ["design", "user"] 
Community = ["graph", "community", "communication", "event", "contribution", "contributor", "wiki","documentation","presentation","contributeur","gitbook"]


def getChannelLogs(mypath):
	# getChannelLogs("./logs/")
	f = []
	for (dirpath, dirnames, filenames) in walk(mypath):
	    f.extend(filenames)
	    good = [x for x in f if (("C" in x) and ".log" in x)]
	    break
	return good

def GetUserList(list):
	f = open("./logs/"+list,'r')
	text = f.read().split("\n")
	f.close()
	return text

def OpenLog(logfile):
	f = open("./logs/"+logfile,'r')
	text = f.read()
	f.close()
	return text

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

# Initiate user list
Users = GetUserList("users.log")
# Get logs
Files = getChannelLogs("./logs/")
# Process each log
for ChannelID in Files:
	Log = OpenLog(ChannelID)
	ChannelID = ChannelID.split(".")[0]
	ChannelData = [] 
	for User in Users:
		CountSoft = 0
		CountHard = 0
		CountLegal = 0
		CountMedical = 0
		CountDesign = 0
		CountCommunity = 0
		for line in Log.split("\n"):
		    if User in line.split(":")[0]:
			for hard in Hardware:
				CountHard += line.lower().count(hard)
			for soft in Software:
				CountSoft += line.lower().count(soft)
			for legal in Legal:
				CountLegal += line.lower().count(legal)
			for medical in Medical:
				CountMedical += line.lower().count(medical)
			for design in Design:
				CountDesign += line.lower().count(design)
			for community  in Community:
				CountCommunity += line.lower().count(community)
			if "(reactions: " in line:
				reacted = find_between( line, "(reactions: ", ")" ).split(",")
				for reac in reacted:
					reactions = {'user': User, 'channel': ChannelID, 'reactions' : reac, "ts" : line.split(">")[0]}
					ChannelData.append(reactions)
					MainJSON.append(reactions)
					print reactions
			if "<@" in line:
				m = re.findall ( '<@(.*?)>', line, re.DOTALL)
				for mentions in m:
				    if not (User == mentions):
					mentions = mentions
					mentionsJSON = {'user': User, 'channel': ChannelID, 'mentions' : mentions, "ts" : line.split(">")[0]}
					ChannelData.append(mentionsJSON)
					MainJSON.append(mentionsJSON)
					print mentionsJSON

		entry = {'user': User, 'channel': ChannelID, 'info' : {'posts': str(Log.count(User)), 'software': str(CountSoft), 'hardware': str(CountHard), 'legal': str(CountLegal), 'medical': str(CountMedical), 'design': str(CountDesign), 'community': str(CountCommunity)}}

		if (CountSoft+CountHard+CountLegal+CountMedical+CountCommunity+CountDesign):
			#ChannelData.append(entry)
			MainJSON.append(entry)
		#print User+": "+str(Log.count(User))
	



	#dumping channel-wise json
	#json_data = json.dumps(ChannelData, sort_keys=True, indent=4)
	#f = open("logs/"+ChannelID.split(".")[0]+".json","w+")
	#f.write(json_data)
	#f.close()

# Dumping main json
json_data = json.dumps(MainJSON, sort_keys=True, indent=4)
f = open("logs/MainJSON.json","w+")
f.write(json_data)
f.close()
