# github_follow_graph_analysis

Create a database in mongodb named `github_follow`

Now import the github_follow_follow file into the follow database using the import json command of mongodb : `mongoimport -d github_follow -c follow github_follow_follow.json`

To create both of the list of `payload` and `actor` in mongodb, you have to run the  `createUserDB.py` first.