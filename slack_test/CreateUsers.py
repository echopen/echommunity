#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -------------------------
# (c) kelu124
# cc-by-sa/4.0/
# -------------------------
# Examining slack log files
# Creates the users stats
# -------------------------

import re	
import subprocess
import os
from os import walk
import json 
from pprint import pprint
import operator
from operator import itemgetter

Header = UserPage = "[Home](https://kelu124.github.io/echommunity/)\n\n"

def getChannelLogs(mypath):
	f = []
	for (dirpath, dirnames, filenames) in walk(mypath):
	    f.extend(filenames)
	    good = [x for x in f if (("C" in x) and ".json" in x)]
	    break
	return good

def GetPeople():
	People = []
	usernames = {}
	with open("./logs/users.log") as users:  
		for user in users:
			WhoIs = user.strip().split(";")
			People.append(WhoIs[0])
			usernames[WhoIs[0]] = WhoIs[1]
	return People,usernames

def CreatePage(PeopleID,usernames,PeopleJSON):
	k = 0
	UserPage = Header
	UserPage += "# Some info on __"+usernames[PeopleID]+"__ (_@"+PeopleID+"_)\n\n\n"
	UserPage += "## Topics of interest\n\n"
	UserPage += "### Posts: \n\nNumber of posts: "+str(PeopleJSON["posts"]["posts"])
	UserPage += "\n\n### Topics:\n\n"

	PPLPost = sorted(PeopleJSON["posts"].items(), key=operator.itemgetter(1))
	if len(PPLPost):
		PPLPost.reverse()

	for post in PPLPost:
	    if post[1]:
		UserPage += "* __"+post[0]+"__: " + str(post[1])+" posts\n"

	UserPage += "\n## Key interactions \n\n"

	PPLReaction = sorted(PeopleJSON["reactions"].items(), key=operator.itemgetter(1))

	if len(PPLReaction):
		PPLReaction.reverse()

	for ppl in PPLReaction:
		UserPage += "* [@"+usernames[ppl[0]]+"](./"+ppl[0]+".md): " + str(ppl[1])+" reactions\n"	

	f = open("../gh-pages/"+PeopleID+".md","w+")
	f.write(UserPage)
	f.close()


	return k


##
#
##

PPList, usernames = GetPeople()

MainJSON = {"MainData":{}}
HighScorePostsJSON = []


for PeopleID in PPList:
	TopicsNames = []
	PeopleJSON = {"id":usernames[PeopleID],"reactions":{},"posts":{}}

	for ppl in PPList:
		PeopleJSON["reactions"][ppl]=0
		


	PeopleJSON["posts"]["hardware"]=0	
	PeopleJSON["posts"]["software"]=0
	PeopleJSON["posts"]["legal"]=0
	PeopleJSON["posts"]["medical"]=0
	PeopleJSON["posts"]["design"]=0
	PeopleJSON["posts"]["community"]=0
	PeopleJSON["posts"]["posts"]=0

	AllLogs = getChannelLogs("./logs/")
	
	for JsonFile in AllLogs:
		with open('./logs/'+JsonFile) as data_file:    
		    data = json.load(data_file)
		if PeopleID in data["users"]:
			for mention in data['mentions']:
				if PeopleID == mention["user_id"]:
					PeopleJSON["reactions"][mention["mentioned_user_id"]] += 1

			for reaction in data['reactions']:
				if PeopleID == reaction["user_id"]:
					PeopleJSON["reactions"][reaction["mentioned_user_id"]] += 1

			for UserID in data['users_info']:
			    for i in UserID:
				if (i == PeopleID):
					for subject in UserID[i]:
					    if (int(UserID[i][subject])):
						#print JsonFile+" - "+UserID[i][subject]+" "+subject+" -- "+i
					    	PeopleJSON["posts"][subject] += int(UserID[i][subject])
	Vector = [PeopleID]
	for subject in UserID[i]:
		Vector.append(int(PeopleJSON["posts"][subject]))
		TopicsNames.append(str(subject))
	HighScorePostsJSON.append(Vector)
	#print HighScorePostsJSON

	for ppl in PPList:
		if not PeopleJSON["reactions"][ppl]:
			del PeopleJSON["reactions"][ppl]

	MainJSON["MainData"][PeopleID] = PeopleJSON

	CreatePage(PeopleID,usernames,PeopleJSON)

#print HighScorePostsJSON



MainPage = Header
MainPage += "# What is it?\n This page shows the different spokepersons for the different themes of the project.\n"

for i in range(len(TopicsNames)):
	Post =  sorted(HighScorePostsJSON,key=itemgetter(i+1))
	Post.reverse()
	MainPage += "\n### "+TopicsNames[i]+"\n\n"
	for j in range(5):
		MainPage += "* [@"+usernames[Post[j][0]]+"](./"+Post[j][0]+".md): " + str(Post[j][i+1])+" posts\n"

print MainPage

f = open("../gh-pages/README.md","w+")
f.write(MainPage)
f.close()


json_data = json.dumps(MainJSON, sort_keys=True, indent=4)
f = open("logs/MainUsers.jason","w+")
f.write(json_data)
f.close()