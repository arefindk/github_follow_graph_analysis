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
merged_pull = db.merged_pull
approvers = db.approvers
requesters = db.requesters

## Aggregate by unique approvers
pipelineUniqueApproverLogin = [{"$group":{"_id":"$payload_pull_request_merged_by_login","cnt":{"$sum":1}}},	{"$sort":{"cnt":-1}}]

## This result contains all of the unique approvers in the databaase
results = merged_pull.aggregate(pipelineUniqueApproverLogin, allowDiskUse=True)

## Now inserting them to the payload database for traversing them later
approversInserted = 0
for approver in results:
	currentUser = approver["_id"]
	print "traversing ", currentUser, " with documents ", approver["cnt"]
	approverDoc = {"login":currentUser, "cnt":approver["cnt"],"traversed":False}
	db.approvers.insert(approverDoc)
	approversInserted +=1
	print "Inserted Approvers ", approversInserted

## Aggregate by unique requesters
pipelineUniqueRequesterLogin = [{"$group":{"_id":"$payload_pull_request_head_user_login","cnt":{"$sum":1}}},{"$sort":{"cnt":-1}}]


results = merged_pull.aggregate(pipelineUniqueRequesterLogin, allowDiskUse=True)

## Now inserting them to the requester database for traversing them later
requestersInserted = 0
for requester in results:
	currentUser = requester["_id"]
	print "traversing ", currentUser, " with documents ", requester["cnt"]
	requesterDoc = {"login":currentUser, "cnt":requester["cnt"],"traversed":False}
	db.requester.insert(requesterDoc)
	requestersInserted += 1
	print "Inserted requesters ", requestersInserted
