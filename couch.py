#!/usr/bin/env python
from __future__ import print_function

from couchbase.bucket import Bucket
import couchbase.exceptions as E
import json
import os

cb = Bucket('couchbase://115.146.85.104/default')

print (cb.server_nodes)

def write_to_couch():
	for line in open('data.txt', 'r'):
		data = json.loads(line)
		id = (data['id'])
		try:
			cb.insert(str(id), json.loads(line))
		except Exception, e:
			print (e)
			continue
	os.remove('data.txt')
	
	#id+=1
	#data.append(json.load(line))

#data = json.loads(json_data)
#size = len(data)
#print ('Length',size)
#cb.upsert(str(++id), data)