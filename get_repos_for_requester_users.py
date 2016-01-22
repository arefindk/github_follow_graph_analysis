from github import Github
from pymongo import MongoClient
import time
import datetime
import csv
from collections import defaultdict,Counter
from random import shuffle
from bson.objectid import ObjectId

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
merged_pull = db.merged_pull
users = db.users
deleted = db.deleted_users
requester = db.requester

## Reading the comma separated github token file
filename = "github_tokens.dat"
openfile = open(filename, 'rt')
token_file = csv.reader(openfile)
token_file.next() # skipping the first line which is an headerline
tokens = list()
for line in token_file:
	tokens.append(line[1])
openfile.close()

shuffle(tokens)

## Initializing github api
tokensUsed = 0
tokenIndex = 0
git  = Github(tokens[tokenIndex])

## Find the un-traversed users in the requester database
findDoc = {"traversed":False}

## This result contains all of the unique requester in the databaase
results = requester.find(findDoc)

## Now for each requester we are creating a profile for that github user with his name, profile creation time, number of repos, the language the user has most repos in, and for each repo with their languages
requesterInserted = 0
for result in results:
	currentUser = result["login"]
	id = result["_id"]
	print "traversing ", currentUser

	## Updating all the requester documents with traversed:true so that in future they do not have to be traversed again
	findDoc = {"_id":ObjectId(str(id))}
	updateDoc = {"$set":{"traversed":True}}
	res = db.requester.update(findDoc,updateDoc)
	
	resultExists = users.find_one({"login":currentUser})
	if not resultExists:
		isDeletedUser = deleted.find_one({"login":currentUser})
		if not isDeletedUser:
			#print "he is not found in db, so inserting"
			## Here I am taking care of the api limit
			currentLimit = git.get_rate_limit()
			remaining = currentLimit.rate.remaining
			print "rate remaining ", remaining
			while remaining < 10:
				#print "tokensUsed ", tokensUsed
				tokenIndex = (tokensUsed % len(tokens))
				#print "tokenIndex ", tokenIndex
				git = Github(tokens[tokenIndex])
				currentLimit = git.get_rate_limit()
				remaining = currentLimit.rate.remaining
				print "rate remaining ", remaining
				tokensUsed += 1
			## Try catch block for the users to avoid the exception github.GithubException.UnknownObjectException: 404 {u'documentation_url': u'https://developer.github.com/v3', u'message': u'Not Found'}
			try:
				currentUserFromGithubAPI = git.get_user(currentUser)

				doc = {}
				doc["login"] = currentUser

				doc["created_at"] = currentUserFromGithubAPI.created_at
				doc["id"] = currentUserFromGithubAPI.id
				doc["name"] = currentUserFromGithubAPI.name
				doc["type"] = currentUserFromGithubAPI.type
				doc["html_url"] = currentUserFromGithubAPI.html_url
				doc["followers_url"] = currentUserFromGithubAPI.followers_url
				doc["following_url"] = currentUserFromGithubAPI.following_url
				doc["company"] = currentUserFromGithubAPI.company
				doc["location"] = currentUserFromGithubAPI.location
				doc["email"] = currentUserFromGithubAPI.email
				doc["followers"] = currentUserFromGithubAPI.followers
				doc["following"] = currentUserFromGithubAPI.following
				doc["public_repos"] = currentUserFromGithubAPI.public_repos
				doc["public_gists"] = currentUserFromGithubAPI.public_gists

				repoLanguages = list()
				repoCount = 0
				repos = list()
				## If a user does not have a repo then loop wont even enter in this segment, so repoCount will be 0
				for repo in currentUserFromGithubAPI.get_repos():
					singleRepoDoc = {}
					singleRepoDoc["name"] = repo.name
					singleRepoDoc["created_at"] = repo.created_at
					singleRepoDoc["updated_at"] = repo.updated_at
					singleRepoDoc["language"] = repo.language
					singleRepoDoc["forks_count"] = repo.forks_count
					singleRepoDoc["stargazers_count"] = repo.stargazers_count
					singleRepoDoc["watchers_count"] = repo.watchers_count
					singleRepoDoc["size"] = repo.size
					#print "singleRepoDoc ",singleRepoDoc
					repoLanguages.append(repo.language)
					repoCount += 1
					repos.append(singleRepoDoc)
				## Calculating the most used language by the user	
				if repoLanguages:
					d = defaultdict(int)
					for language in repoLanguages:
						d[language] += 1

					all_langs = list()
					for current_lang, current_lang_count in d.iteritems():
						lang = dict()
						lang['lang'] = current_lang
						lang['count'] = current_lang_count
						lang['portion'] = current_lang_count / float(repoCount)
						all_langs.append(lang)

					res = Counter(d).most_common(2)
					currentUserNativeLanguage = res[0][0]
					reposInNativeLaguage  = d[currentUserNativeLanguage]
					portionInNativeLanguage = reposInNativeLaguage / float(repoCount)
					## If in any case the most common language of the user is None then we are taking the second most common language it used
					if not currentUserNativeLanguage:
						if len(res) > 1:
							currentUserNativeLanguage = res[1][0]
							reposInNativeLaguage  = d[currentUserNativeLanguage]
							portionInNativeLanguage = reposInNativeLaguage / float(repoCount)
				else:
					currentUserNativeLanguage = None
					reposInNativeLaguage = 0
					portionInNativeLanguage = 0
					all_langs = None
				doc["native_language"] = currentUserNativeLanguage
				doc["native_language_repo_count"] = reposInNativeLaguage
				doc["native_language_portion"] = portionInNativeLanguage
				doc["repo_count"] = repoCount
				doc["repos"] = repos
				doc["repo_count_all_langs"] = all_langs
				#print doc
				current_mongo_insert_id = users.insert_one(doc).inserted_id
				requesterInserted += 1
				print requesterInserted, " ",current_mongo_insert_id
			except:
				print "User not found ", currentUser
				deletedUserDoc = dict()
				deletedUserDoc["login"] = currentUser
				deletedUserDoc["isFollowee"] = True
				deletedUserInsertedID = deleted.insert_one(deletedUserDoc).inserted_id
				print "Inserted new deleted user ", currentUser, " with _id ", deletedUserInsertedID
		else:
			print "The user ", currentUser , " was already deleted and in mongodb"