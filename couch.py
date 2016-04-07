#!/usr/bin/env python
from __future__ import print_function

from couchbase.bucket import Bucket
import couchbase.exceptions as E
import json
import os

cb = Bucket('couchbase://115.146.85.104/melbourne_tweets')

print (cb.server_nodes)


def write_to_couch():
	count = 0
	error_count = 0
	for line in open('data.txt', 'r'):
		data = json.loads(line)
		id = (data['id'])
		try:
			cb.insert(str(id), json.loads(line))
			count += 1
		except Exception, e:
			error_count += 1
			#print (e)
			continue
	os.remove('data.txt')
	print("Wrote ",count," tweets to couch")
	print(error_count,"errors")
	
	#id+=1
	#data.append(json.load(line))

#data = json.loads(json_data)
#size = len(data)
#print ('Length',size)
#cb.upsert(str(++id), data)