# github_follow_graph_analysis

### Install Mongodb on Ubuntu
- Go to this [webpage](https://docs.mongodb.org/v3.0/installation/) or use the following commands on your own risk.
- `sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10`
- `echo "deb http://repo.mongodb.org/apt/ubuntu precise/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list`
- `sudo apt-get update`
- `sudo apt-get install -y mongodb-org`

### Install python modules
- Install the `pygithub` and `pymongo` using pip or something else.

### Setting up the initial mongodb database:
- Create a database in mongodb named `github_follow`

- Now import the github_follow_follow file into the follow database using the import json command of mongodb : `mongoimport -d github_follow -c follow github_follow_follow.json`

- To create both of the list of `payload` and `actor` in mongodb, you have to run the  `createUserDB.py` first.