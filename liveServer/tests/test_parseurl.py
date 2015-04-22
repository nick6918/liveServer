import urllib2, base64,sys
import urllib,geohash
import json,sys,struct

url = "http://127.0.0.1:8000/live/parseurl"
files = open("/Users/weifanding/Downloads/webM3u8.m3u8", "r")

postContent = {
				"sid" : 1001, 
				"vid" : 1,
				"url" : "http://v.pptv.com/show/QxRz8VmicL23QTrY.html",
				"step": 1,
}
postData = urllib.urlencode(postContent)
request = urllib2.Request(url, postData)
request.get_method = lambda: 'POST'
 
# url = "http://127.0.0.1:8000/live/parseurl?sid=1001&vid=1&step=0&url=http://v.pptv.com/show/QxRz8VmicL23QTrY.html"
# request = urllib2.Request(url)

request.add_header('User-Agent', 'AMAP SDK iOS Search 2.2.1')
request.add_header('Content-Type', 'application/x-www-form-urlencoded')
result = urllib2.urlopen(request)
contents = result.read()
fp=open("testResult.html", "w+")
fp.write(contents)
fp.close()
print contents