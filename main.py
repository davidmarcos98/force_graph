import csv
import json
from collections import defaultdict
from random import choice, randint

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
rts = defaultdict(int)
parsed_data = []
for line in reader:
    count += 1
    if count == TWEETS_COUNT:
        break
    user = line['author_id<gx:category>']
    if user:
        if user not in users:
            users.append(user)
            rts[user] == line['retweets<gx:number>'] + line['quotes<gx:number>']
            parsed_data.append(
                (
                    user,
                    {
                        'tweet_id': line['id<gx:category>'],
                        'author_handler': line['author_handler<gx:category>'],
                        'author_id': line['author_id<gx:category>'],
                        'author_name': line['author_name<gx:category>'],
                        'retweets': line['retweets<gx:number>'],
                    }
                )
            )

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
    kind = line['tpe<gx:category>']
    if user and user in users and rp_user and rp_user in users and user != rp_user and (rp_user, user, kind) not in links and (user, rp_user, kind) not in links:
        link_count[user] += 1
        link_count[rp_user] += 1
        links.append((user, rp_user, kind))

valid_nodes = []
for link in links:
    if (link_count[link[0]] > MIN_REPLIES or link_count[link[1]] > MIN_REPLIES or ADD_ALL) and link[0] != link[1]:
        valid_nodes.append(link[0])
        valid_nodes.append(link[1])

json.dump(link_count, open("output/count.json", "w"), ensure_ascii=False, indent=4)
json.dump(parsed_data, open("output/parsed_data.json", "w"), ensure_ascii=False, indent=4)
json.dump(links, open("output/links.json", "w"), ensure_ascii=False, indent=4)
json.dump(valid_nodes, open("output/valid_nodes.json", "w"), ensure_ascii=False, indent=4)
valid_tweets = []
for node in parsed_data:
    if node[0] in valid_nodes:
        if int(node[1]['retweets']) > 0:
            valid_tweets.append(node[1]['tweet_id'])
            try:
                retweets = json.load(open(f"output/retweets_{node[1]['tweet_id']}.json", 'r'))
                for retweet in retweets:
                    if retweet:
                        G.add_nodes_from([(
                            retweet,
                            {
                                'author_handler': retweet.replace("@", ""),
                            }
                        )])
                        links.append((node[0], retweet, "retweet"))
            except:
                pass
        G.add_nodes_from([node])

json.dump(valid_tweets, open("output/valid_tweets.json", "w"), ensure_ascii=False, indent=4)
for link in links:
    # if (link_count[link[0]] > MIN_REPLIES or link_count[link[0]] > MIN_REPLIES) or ADD_ALL:
    if link[0] in valid_nodes:
         G.add_edge(link[0], link[1], **{'kind': link[2]})

print("Calculating centralities...")
# Done before adding retweets which are "empty" nodes
degree = nx.degree_centrality(G)
betweenness = nx.betweenness_centrality(G)
closeness = nx.closeness_centrality(G)

# add_retweet_nodes()
def add_retweet_nodes():
    for user, value in rts.items():
        value = randint(0, 5)
        if value:
            print(user, value)
            for i in range(value):
                G.add_edge(user, f"{user}_{i}", **{'kind': 'retweet'})


print("Exporting graph...")
# nx.write_graphml(G, 'test.graphml')
graph_data = json_graph.node_link_data(G)
for index, node in enumerate(graph_data['nodes']):
    node_id = graph_data['nodes'][index]['id']
    graph_data['nodes'][index]['degree'] = degree.get(node_id, 0)
    graph_data['nodes'][index]['betweenness'] = betweenness.get(node_id, 0)
    graph_data['nodes'][index]['closeness'] = closeness.get(node_id, 0)

json.dump(graph_data, open("data.json", "w"), ensure_ascii=False)
