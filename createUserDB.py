from github import Github
from pymongo import MongoClient
import time
import datetime
import csv
from collections import defaultdict,Counter
from random import shuffle

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
follow = db.follow
payloads = db.payloads
actors = db.actors

## Aggregate by unique payloads
pipelineUniqueFolloweeeLogin = [{"$group":{"_id":"$payload_target_login","cnt":{"$sum":1}}},	{"$sort":{"cnt":-1}}]

## This result contains all of the unique followees in the databaase
results = follow.aggregate(pipelineUniqueFolloweeeLogin, allowDiskUse=True)

## Now inserting them to the payload database for traversing them later
payloadsInserted = 0
for payload in results:
	currentUser = payload["_id"]
	print "traversing ", currentUser, " with documents ", payload["cnt"]
	payloadDoc = {"login":currentUser, "cnt":payload["cnt"],"traversed":False}
	db.payloads.insert(payloadDoc)
	payloadsInserted +=1
	print "Inserted Payloads ", payloadsInserted

## Aggregate by unique actors
pipelineUniqueFollowerLogin = [{"$group":{"_id":"$actor_attributes_login","cnt":{"$sum":1}}},{"$sort":{"cnt":-1}}]


results = follow.aggregate(pipelineUniqueFollowerLogin, allowDiskUse=True)

## Now inserting them to the actor database for traversing them later
actorsInserted = 0
for actor in results:
	currentUser = actor["_id"]
	print "traversing ", currentUser, " with documents ", actor["cnt"]
	actorDoc = {"login":currentUser, "cnt":actor["cnt"],"traversed":False}
	db.actors.insert(actorDoc)
	actorsInserted += 1
	print "Inserted actors ", actorsInserted
