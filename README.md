# github_follow_graph_analysis

### Install Mongodb on Ubuntu
- Go to this [webpage](https://docs.mongodb.org/manual/installation/) or if you are using ubuntu 14.04 then use the following commands on your own risk.
- `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927`
- `echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list`
- `sudo apt-get update`
- `sudo apt-get install -y mongodb-org`

### Install python modules
- Install the `pygithub` and `pymongo` using pip or something else.

### Setting up the initial mongodb database:
- Create a database in mongodb named `github_follow`

- Now import the github_follow_follow file into the follow database using the import json command of mongodb : `mongoimport -d github_follow -c follow github_follow_follow.json`

- Similarly import the github_merged_pull_network.json file into mongodb using the impor t command `mongoimport -d github_follow -c merged_pull github_merged_pull_network.json
`

### Now running the crawlers:
- To create all the list of `payloads`, `actors`, `approvers` and `requesters` in mongodb, you have to run the  `createUserDB.py` and `create_merged_pull_users.py` first.

- You should first create a index in your database. in the mongo shell you can create an index using this command e.g. `db.users.createIndex( { login: 1 } )`