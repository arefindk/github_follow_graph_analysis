from github import Github
from pymongo import MongoClient
import time
import datetime
import csv
from collections import defaultdict,Counter

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
follow = db.follow
users = db.users

## Reading the comma separated token file
filename = "github_tokens_followers.dat"
openfile = open(filename, 'rt')
token_file = csv.reader(openfile)
token_file.next() # skipping the first line which is an headerline
tokens = list()
for line in token_file:
	tokens.append(line[1])
openfile.close()

## creating a file where we will keep track of all deleted followers
filename = "deleted_followers.txt"
deletedFollowersFile = open (filename, 'a')
## creating a file where we will keep track of all deleted followees
filename = "deleted_followees.txt"
deletedFolloweesFile = open (filename, 'a')

## Initializing github api
tokensUsed = 0
tokenIndex = 0
git  = Github(tokens[tokenIndex])

## Aggregate by the unique follower
pipelineUniqueFollowerLogin = [{"$group":{"_id":{"login":"$actor_attributes_login","follow_id":"$_id"},"cnt":{"$sum":1}}},{"$sort":{"cnt":-1}}]


results = follow.aggregate(pipelineUniqueFollowerLogin, allowDiskUse=True)

## Now for each follower we are creating a profile for that github user with his name, profile creation time, number of repos, the language the user has most repos in, and for each repo with their languages
followersInserted = 0
for result in results:
	currentUser = result["_id"]["login"]
	print "traversing ", currentUser, result["_id"]["follow_id"]
	resultExists = users.find_one({"login":currentUser})
	if not resultExists:
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
			doc["follow_id"] = result["_id"]["follow_id"]

			
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
				res = Counter(d).most_common(2)
				currentUserNativeLanguage = res[0][0]
				## If in any case the most common language of the user is None then we are taking the second most common language it used
				if not currentUserNativeLanguage:
					if len(res) > 1:
						currentUserNativeLanguage = res[1][0]
						print "currentUser ", currentUser, " res ",res
			else:
				currentUserNativeLanguage = None
			doc["native_language"] = currentUserNativeLanguage
			doc["repo_count"] = repoCount
			doc["repos"] = repos
			#print doc
			current_mongo_insert_id = users.insert_one(doc).inserted_id
			followeesInserted += 1
			print followersInserted, " ",current_mongo_insert_id
		except:
			print "User not found ", currentUser
			deletedFollowersFile.write(str(currentUser)+"\n")

deletedFollowersFile.close()