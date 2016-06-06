from couchbase.bucket import Bucket, View
from py2neo import Graph, Node
from elasticsearch import Elasticsearch
import json

def putingraph(topic, s):
	cb = Bucket('couchbase://115.146.85.104/melbourne_tweets')
	graph = graph = Graph("http://neo4j:CouchAdmin@115.146.86.24:7474/db/data/") #Graph("http://115.146.86.24:7474/db/data/")
	cypher = graph.cypher

	es = Elasticsearch([{'host': '115.146.88.249', 'port': 9200}])

	#topic = sys.argv[1]
	#if len(sys.argv) > 2:
	if s>0:
		size = s
	else:
		size = 100
	dic = es.search(index="melbourne", body={"query": {"match": {'doc.text':topic}},"_source": ["doc.text"], "size":size})

	c = 0

	file = open('newtweetids.txt', 'a')



	#for result in View(cb, "dev_shi", "test",include_docs=True,streaming=True):
	for i in dic['hits']['hits']:
		try:
			result = cb.get(i['_id'])
			key_list = []
			hash = result.value["entities"]["hashtags"]
			mentions = result.value["entities"]["user_mentions"]
			user = result.value["user"]["name"]
			print hash, mentions, user
			positive = 0
			negative = 0
			if result.value["sentiment_score"]["polarity"] > 0:
				positive = 1
			else:
				negative = 1
			n = cypher.execute("MERGE (a:UserName {name:{mtname}}) ON CREATE SET a.count = 1, a.pos = {pos}, a.neg = {neg} ON MATCH SET a.count = a.count + 1, a.pos = a.pos + {pos}, a.neg = a.neg + {neg} RETURN a",mtname=user, pos=positive, neg=negative)	
			top = cypher.execute("MERGE (a:Topic {name:{topname}}) ON CREATE SET a.count = 1, a.pos = {pos}, a.neg = {neg} ON MATCH SET a.count = a.count + 1, a.pos = a.pos + {pos}, a.neg = a.neg + {neg} RETURN a",topname=topic, pos=positive, neg=negative)
			r = cypher.execute("MATCH (a:Topic)-[rel:TweetedBy]-(b:UserName) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=topic, n2=user, rel="TweetedBy")
			if not r:
				r = cypher.execute("MATCH (a:Topic),(b:UserName) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=topic, n2=user, rel="TweetedBy")
			c += 1
			print result.key, c
			#if result.key not in key_list
			key_list.append(result.key)
			l = len(hash)
			m = len(mentions)
			if l>0:
				tags = []
				for x in xrange(0,l):
					#print "x",x
					tagname = hash[x]["text"]
					tags.append(tagname)
					n = cypher.execute("MERGE (a:HashTag {name:{tname}}) ON CREATE SET a.count = 1, a.pos = {pos}, a.neg = {neg} ON MATCH SET a.count = a.count + 1, a.pos = a.pos + {pos}, a.neg = a.neg + {neg} RETURN a",tname=tagname, pos=positive, neg=negative)

					r = cypher.execute("MATCH (a:Topic)-[rel:HasTags]-(b:HashTag) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=topic, n2=tagname, rel="HasTags")
					if not r:
						r = cypher.execute("MATCH (a:Topic),(b:HashTag) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=topic, n2=tagname, rel="HasTags")

					r = cypher.execute("MATCH (a:HashTag)-[rel:TweetedBy]-(b:UserName) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=tagname, n2=user, rel="TweetedBy")
					if not r:
						r = cypher.execute("MATCH (a:HashTag),(b:UserName) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=tagname, n2=user, rel="TweetedBy")
			
					if m>0:
						ments = []
						for x in xrange(0,l):
							#print "x",x
							mname = mentions[x]["name"]
							ments.append(mname)
							n = cypher.execute("MERGE (a:UserName {name:{mtname}}) ON CREATE SET a.count = 1, a.pos = {pos}, a.neg = {neg} ON MATCH SET a.count = a.count + 1, a.pos = a.pos + {pos}, a.neg = a.neg + {neg} RETURN a",mtname=mname, pos=positive, neg=negative)
							r = cypher.execute("MATCH (a:HashTag)-[rel:Mentions]-(b:UserName) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=tagname, n2=mname, rel="Mentions")
							if not r:
								r = cypher.execute("MATCH (a:HashTag),(b:UserName) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=tagname, n2=mname, rel="Mentions")
								
				if len(tags) > 1:
					for t in xrange(0,len(tags)-1):
						for z in xrange(t+1,len(tags)):
							r = cypher.execute("MATCH (a:HashTag)-[rel:inSameTweet]-(b:HashTag) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=tags[t], n2=tags[z], rel="inSameTweet")
							if not r:
								r = cypher.execute("MATCH (a:HashTag),(b:HashTag) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:inSameTweet {count:1}]->(b)) RETURN r", n1=tags[t], n2=tags[z], rel="inSameTweet")
								#r = cypher.execute("MATCH (a:HashTag)-[rel:inSameTweet]-(b:HashTag) WHERE a.name = {n1} AND b.name = {n2} ON CREATE SET rel.count = 1 ON MATCH SET rel.count = rel.count + 1 RETURN rel", n1=tags[t], n2=tags[z], rel="inSameTweet")
				if m>0:
					#ments = []
					for x in ments:
						#print "x",x
						mname = mentions[x]["name"]
						#ments.append(mname)
						#n = cypher.execute("MERGE (a:UserName {name:{mtname}}) ON CREATE SET a.count = 1, a.pos = {pos}, a.neg = {neg} ON MATCH SET a.count = a.count + 1, a.pos = a.pos + {pos}, a.neg = a.neg + {neg} RETURN a",mtname=mname, pos=positive, neg=negative)
						r = cypher.execute("MATCH (a:Topic)-[rel:Mentions]-(b:UserName) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=topic, n2=mname, rel="Mentions")
						if not r:
							r = cypher.execute("MATCH (a:Topic),(b:UserName) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=topic, n2=mname, rel="Mentions")
						r = cypher.execute("MATCH (a:UserName)-[rel:Mentions]-(b:UserName) WHERE a.name = {n1} AND b.name = {n2} SET rel.count = rel.count + 1 RETURN rel", n1=user, n2=mname, rel="Mentions")
						if not r:
							r = cypher.execute("MATCH (a:Topic),(b:UserName) WHERE a.name = {n1} AND b.name = {n2} CREATE ((a)-[r:Mentions {count:1}]->(b)) RETURN r", n1=user, n2=mname, rel="Mentions")
				
			#for item in key_list:
	  		print>>file, result.key					
		except Exception, e:
			print e
			continue
	return c

	#with open('tweetids.txt', 'a') as file:
	#	for item in key_list:
	#  		print>>file, item

def cleargraph():
	graph = graph = Graph("http://neo4j:CouchAdmin@115.146.86.24:7474/db/data/")
	graph.delete_all()


			