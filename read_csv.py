import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import csv

filename = "github_timeline_follow.csv"

openfile = open(filename, 'rt')
follow_file = csv.reader(openfile)
follow_file.next() # skipping the first line which is an headerline

G = nx.DiGraph()
count = 0

for line in follow_file:
	follower = line[1]
	followee = line[5]
	G.add_edge(follower,followee)
	count += 1
	# print line[1], " follows ", line[5]
	if count%10000 == 0:
		print count

nx.write_graphml(G, "follow.graphml", encoding='utf-8', prettyprint=True)
