from py_bing_search import PyBingImageSearch as pbis 
import urllib


def bing_search(keywords=["fire accident"],limit=2000):
	API_KEY = '1TWo2MkjPvqVDrJj0ssZTXAt1wJJfRX7GXoCmpnZ2XY'
	search_query = (' ').join(keywords)
	bi = pbis(API_KEY, search_query)
	search_results = bi.search(limit=limit, format='json')

	images = []
	i = 0
	for image in search_results:
		url = image.media_url
		title = image.title
		source_url = image.source_url
		print url[-3:]
		if(url[-3:]=='jpg'):
			urllib.urlretrieve(url, str(i)+".jpg")
			i +=1
			print "saved",str(i)
		elif(url[-3:]=='png'):
			urllib.urlretrieve(url, str(i)+".png")
			i +=1
			print "saved",str(i)

bing_search()
