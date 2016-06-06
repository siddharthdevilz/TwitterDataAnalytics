# Twitter Data Analytics

### Source Code
```
https://github.com/siddharthdevilz/TwitterDataAnalytics/tree/develop
```

### Project Working Video
```
https://www.dropbox.com/s/9zg753wkhrc6z3b/ProjectWorkingVideo.mov?dl=0
```

### Instances
```sh
Instance0 - 115.146.88.249
Instance1 - 115.146.85.104
Instance2 - 115.146.86.24
Instance3 - 115.146.86.26
```

### Couchbase Server
```
Username : Admin
Password : CouchAdmin

http://115.146.85.104:8091
http://115.146.86.26:8091
http://130.56.248.130:8091
```

### Neo4j Server
```
Username : neo4j
Password : CouchAdmin
http://115.146.86.24:7474
```

### ElasticSearch Server
```
Username : Administrator
Password : password
http://115.146.88.249:9200/
```

### Web UI Address
```
http://115.146.88.249:5000/
```

### How to use the system ?
1. Navigate to the basic Web UI at http://115.146.88.249:5000/
2. Enter first topic (keyword), tweets limit (default:100) and click search, usually maximum 500 any more slows down the graph UI
3. The tweets related to this topic are selected via elasticsearch and the tweet data populates the graph
4. Repeat step 2 for one or more topics whose relation is being investigated
5. Navigate to the graph UI at http://115.146.86.24:7474 (User:neo4j, pass:CouchAdmin)
6. To view all the nodes and relations currently present execute the query "match (n) return n"
7. Depending on the number of nodes present, it might take a while. The relationship between the topic, users and hashtags is depicted here
8. Various queries can now be executed on this graph set to explore the relationship between the existing entities
e.g. to reduce the relations above to second degree and third degree only, we can execute the query
```
Match (a:Topic {name:"Topic1 name"})-[r*2..3]-(c:Topic {name:"Topic2 name"}) return a,r,c 
```
e.g. to get the users who have tweeted about both topics
```
Match (a:UserName)-[]-(b) where (a)-[]-(b:Topic {name:"Topic1 name"}) and (a)-[]-(b:Topic {name:"Topic2 name"}) return * 
```
e.g. to get the hashtags common between the two topics
```
Match (a:HashTag)-[]-(b) where (a)-[]-(b:Topic {name:"Topic1 name"}) and (a)-[]-(b:Topic {name:"Topic2 name"}) return * 
```
