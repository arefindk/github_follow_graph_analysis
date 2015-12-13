## Read the previous networkx graph. We wiill add the language attributes to the nodes and we will also trim this graph to a smaller one by remving the nodes who does not have a native_language
filename = "/Users/arefindk/development/github_follow_graph_analysis/follow.graphml"
G = nx.read_graphml(filename)

## Load mongodb
client = MongoClient("mongodb://localhost:27017/")
db = client.github_follow
users = db.users


## Some lists
removedNodes = list()
allNodes = G.nodes()

## Getting language attribute of the user
for node in allNodes:
    ## Finding a user with specific login name from the network
    findDoc = {"login":node}
    result = users.find_one(findDoc)

    if not resultExists:
        removedNodes.append(node)
    else:
        print result['native_language']

# nx.write_graphml(G, "follow.graphml", encoding='utf-8', prettyprint=True)