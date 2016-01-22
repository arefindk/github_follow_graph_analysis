import networkx as nx
from pymongo import MongoClient

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
merged_pull = db.merged_pull

cursor = merged_pull.find()

G = nx.MultiDiGraph()
count = 0

for doc in cursor:
	if "payload_pull_request_merged_by_login" not in doc:
		continue
	else:
		approver = str(doc["payload_pull_request_merged_by_login"])
	if "payload_pull_request_head_user_login" not in doc:
		continue
	else:	
		requester = str(doc["payload_pull_request_head_user_login"])
	timestamp = str(doc["payload_pull_request_merged_at"])
	if "payload_pull_request_base_repo_language" in doc:
		language = str(doc["payload_pull_request_base_repo_language"])
	else:
		language = "null"
	## We are avoiding self loops in the data:
	if requester==approver:
		continue
	else:
		G.add_edge(requester,approver,timestamp=timestamp,language=language)
	count += 1
	if count%10000 == 0:
		print count
		print approver, requester, timestamp, language

print "Nodes ",G.number_of_nodes()," Edges ", G.number_of_edges()

nx.write_graphml(G, "merged_pull_multi_noselfloop_digraph_timestamp_lang.graphml")
