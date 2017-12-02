import requests
import dateparser
import datetime
import json

levels = ["red","orange","green"]
url = "https://api.sigimera.org/v1/crises?auth_token=CPwDES_d8W9bTyLQRCzm&level="

def is_recent_event(time):
	time = time.replace('T',' ')
	time = time.replace('Z','')
	d = dateparser.parse(time)
	print d
	delta = datetime.datetime.now()-d
	if(delta.days<3):
		print delta.days
		print "Recent disaster found"
		return True
	return False

def top_disasters():

	results = []
	mySession = requests.Session()

	for level in levels:
		headers={'User-Agent': 'Mozilla/5.0'}
		#res = requests.get(url+level,headers=headers)
		res = mySession.get(url + level, headers=headers)
		if res.status_code==200:
			res = json.loads(str(res.content))
			print "Success"
			for disaster in res:
				dic = {}
				countries = [k.lower() for k in disaster["gn_parentCountry"]]
				if('india' in countries):
					disaster_type = "unknown"
					types = [k.lower() for k in disaster["dc_subject"]]
					if("earthquake" in types):
						disaster_type = "earthquake"
					if("flood" in types):
						disaster_type = "flood"
					if("cyclone" in types):
						disaster_type = "cyclone"
					dic = {
						"level" : disaster["crisis_alertLevel"],
						"time"  : disaster["created_at"],
						"title" : disaster["dc_title"],
						"coordinates" : disaster["foaf_based_near"],
						"countries" : disaster["gn_parentCountry"],
						"type" : disaster_type,
						"is_recent" : is_recent_event(disaster["created_at"])
					}
					results.append(dic)
		else:
			print "Error",str(res.status_code)
	return results

print top_disasters()

