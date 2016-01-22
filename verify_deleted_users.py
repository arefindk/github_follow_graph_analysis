import networkx as nx
from pymongo import MongoClient
from github import Github
import csv
from random import shuffle
from bson.objectid import ObjectId
from collections import defaultdict,Counter

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
users = db.users
deleted_users = db.deleted_users

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


cursor = deleted_users.find({"verified":{"$exists":False}})
new_users_found = 0

for doc in cursor:
	deleted_user = doc["login"]
	deleted_user_oid = doc["_id"]
	findDoc = {"_id":ObjectId(str(deleted_user_oid))}
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
		currentUserFromGithubAPI = git.get_user(deleted_user)
		doc = {}
		doc["login"] = deleted_user

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
		new_users_found += 1
		print "New User's name is ",deleted_user," ",new_users_found, " ",current_mongo_insert_id
		deleted_users.delete_one(findDoc)
		print "Current deleted user was actually available and now its transferred to users db"
	except:
		updateDoc = {"$set":{"verified":True}}
		res = db.deleted_users.update(findDoc,updateDoc)
		print "User is really deleted", deleted_user, res