import csv
import json
from collections import defaultdict

import matplotlib.pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph

TWEETS_COUNT = 200000
MIN_REPLIES = 1
ADD_ALL = False

G = nx.DiGraph()
f = open('_avocado_2.csv', 'r')
reader = csv.DictReader(f)
count = 0
users = []
parsed_data = []
for line in reader:
    if 'avocado' not in line['text<gx:text>']:
        continue
    count += 1
    if count == TWEETS_COUNT:
        break
    user = line['author_id<gx:category>']
    if user:
        if user not in users:
            users.append(user)
            parsed_data.append(
                (
                    user,
                    {
                        'tweet_id': line['id<gx:category>'],
                        'author_handler': line['author_handler<gx:category>'],
                        'author_id': line['author_id<gx:category>'],
                        'author_name': line['author_name<gx:category>'],
                        'favorites': line['favorites<gx:number>'],
                        'language': line['lang<gx:categoryy>'],
                        'group': line['lang<gx:categoryy>'],
                        'quotes': line['quotes<gx:number>'],
                        'replies': line['replies<gx:number>'],
                        'retweets': line['retweets<gx:number>'],
                        'user_followers_count': line['user_followers_count<gx:number>'],
                        'user_following_count': line['user_following_count<gx:number>'],
                    }
                )
            )
        # G.add_edge(user, line['author_id<gx:category>'])

link_count = defaultdict(int)
f.close()
f = open('_avocado_2.csv', 'r')
reader = csv.DictReader(open('_avocado_2.csv', 'r'))
links = []
for line in reader:
    if 'avocado' not in line['text<gx:text>']:
        continue
    count += 1
    if count == TWEETS_COUNT:
        break
    user = line['author_id<gx:category>']
    rp_user = line['rp_user_id<gx:category>']
    if user and user in users and rp_user and rp_user in users:
        link_count[user] += 1
        link_count[rp_user] += 1
        links.append((user, rp_user))

# G.add_nodes_from(parsed_data)

for node in parsed_data:
    if link_count[node[0]] > MIN_REPLIES or ADD_ALL:
        G.add_nodes_from([node])

for link in links:
    if link_count[link[0]] > MIN_REPLIES or ADD_ALL:
        G.add_edge(link[0], link[1])

degree = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G)
closeness = nx.closeness_centrality(G)

nx.write_graphml(G, 'test.graphml')
graph_data = json_graph.node_link_data(G)
for index, node in enumerate(graph_data['nodes']):
    nid = graph_data['nodes'][index]['id']
    graph_data['nodes'][index]['degree'] = degree[nid]
    graph_data['nodes'][index]['betweenness'] = betweenness[nid]
    graph_data['nodes'][index]['closeness'] = closeness[nid]

json.dump(graph_data, open("data.json", "w"), ensure_ascii=False, indent=4)
