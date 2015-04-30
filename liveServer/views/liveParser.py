# -*- coding: utf-8 -*-
import re, urllib2
from BeautifulSoup import BeautifulSoup
from live_libs.utils import Jsonify
from live_models.LiveModel import LiveModel
from datetime import datetime
import logging
logger = logging.getLogger('appserver')

# testUrl = "http://v.pptv.com/show/QxRz8VmicL23QTrY.html"

def get_client_ip(request):
    	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    	if x_forwarded_for:
        	ip = x_forwarded_for.split(',')[-1].strip()
    	else:
        	ip = request.META.get('REMOTE_ADDR')
    	return ip

def parseUrl(request):
	try:
		step = request.POST.get("step", 3)
		step = int(step)
		logger.debug("#LIVE#: "+str(get_client_ip(request))+" REQUESTED IN STEP "+str(step))
		vid = request.POST.get("vid", None)
		sid = request.POST.get("sid", None)
		if step == 0:
			url = request.POST.get("url", None)
			result = LiveModel().query_backup(sid, vid)
			logger.debug("#LIVE#: "+str(get_client_ip(request))+" REQUESTED WITH URL "+ str(url))
			try:
				nextState = result["nextState"]
				if nextState == 1:	
					if url:
						newUrl = firstStepHelper(url)
						if newUrl:
							result = {"status":True, "newUrl": newUrl, "newState": 1}
							logger.debug("#LIVE#: "+str(get_client_ip(request))+" RESPONSE WITH URL "+ str(newUrl))
						else:
							result = {"status":False, "newState": 0, "error": "903 URL parsing failed"}
					else:
						result = {"status":False, "newState": 0, "error": "902 URL not catched"}
					return Jsonify(result)
				elif nextState == 3:
					return Jsonify({"status":True, "newState": 3, "newUrl":result["url"]})
				else:
					return Jsonify({"status":True, "newState": 4})
			except Exception, e:
				logger.error(e)
				return Jsonify({"status":False, "newState": 4})
		elif step == 1:
			curFile = request.FILES.get("file", None)
			data=""
			for chunk in curFile.chunks():
				data+=chunk
			logger.debug("#LIVE#: "+str(get_client_ip(request))+" FILE CATCHED ")
			pattern = re.compile(r"http:\/\/.*")
			matcher = pattern.search(data)
			if matcher:
				newUrl = matcher.group()
				logger.debug("#LIVE#: "+str(get_client_ip(request))+" RESPONSE WITH URL "+newUrl)
				LiveModel().update_backup(newUrl, "BACKUPED", sid, vid)
				return Jsonify({"status":True, "newState":2, "newUrl":newUrl})
			else:
				LiveModel().update_backup("", "STOPPED", sid, vid)
				logger.error("#LIVE# VIDEO FILE CANNOT PARSE FOR "+str((sid, vid)))
				return Jsonify({"status":False, "newState":4, "error":"904 M3U8 FILE ERROR"})
		elif step == 2:
			LiveModel().update_backup("", "STOPPED", sid, vid)
			LiveModel().finish_live(vid)
			logger.error("#LIVE# VIDEO CANNOT PLAYED FOR "+str((sid, vid)))
			return Jsonify({"status":True, "newState":4})
		elif step == 3:
			logger.debug("#LIVE# VIDEO BACKUP OVERDUE FOR "+str((sid, vid)))
			url = request.GET.get("url", None)
			if url:
				newUrl = firstStepHelper(url)
				if newUrl:
					result = {"status":True, "newUrl": newUrl, "newState": 1}
					LiveModel().update_backup("", u"UNUSED", sid, vid)
					logger.debug("#LIVE#: "+str(get_client_ip(request))+" RESPONSE WITH URL "+ str(newUrl))
				else:
					result = {"status":False, "newState": 0, "error": "903 URL parsing failed"}
			else:
				result = {"status":False, "newState": 0, "error": "902 URL not catched"}
			return Jsonify(result)
		else:
			return Jsonify({"status":False, "error":"905 UNDETERMINED STATE"})
	except Exception, e:
		logger.error(e)
		logger.error("906 SERVER ERROR")
		return Jsonify({"status":False, "error":"906 SERVER ERROR"})

def firstStepHelper(testUrl):
	request = urllib2.Request(testUrl, headers={
				"user-agent": "Mozilla/5.0 (iPad; CPU OS 8_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12B410 Safari/600.1.4",
				})
	while(True):
		try:
			webPage = urllib2.urlopen(request, timeout=3)
			break
		except Exception, e:
			logger.debug("time out for url into m3u8")
			logger.debug(str(testUrl))
			sleep(1)				
			continue
	pageContent = webPage.read()
	pageContent=pageContent.replace(" ", "").replace("\t", "").replace("\n", "")
	#DEBUG
	fp = open("webpage.txt", "w")
	fp.write(pageContent)
	fp.close()
	#http://web-play.pptv.com/web-m3u8-300617.m3u8?type=m3u8.web.pad;playback=0;kk=;o=leader.pptv.com;rcc_id=0
	#regex = r"<scripttype=\"text/javascript\">varwebcfg={.*};</script>"
	regex = r"varwebcfg={.*\"tags\":\[.*\]}};"
	pattern = re.compile(regex)
	matcher = pattern.search(pageContent)
	if matcher:
		soup = BeautifulSoup(matcher.group())
		webcfg = matcher.group().replace(" ", "").replace("\t", "").replace("\n", "")
		idPattern = re.compile(r"\"id\":[0-9]*")
		idValue = idPattern.search(webcfg).group()
		idValue = idValue.split(":")[1]
		kkPattern = re.compile(r"\"ctx\":\"[A-Za-z0-9%]*%3D[A-Za-z0-9-]*\"")
		kkValue = kkPattern.search(webcfg).group()
		kkValueGroup=kkValue.split("3D")
		kkValue = kkValueGroup[len(kkValueGroup)-1].strip("\"")
		m3u8Url = "http://web-play.pptv.com/web-m3u8-"+idValue+".m3u8?type=m3u8.web.pad&playback=0&kk="+kkValue+"&o=v.pptv.com&rcc_id=0"
	else:
		regex = r"videoPlayer\.play\(\'([0-9]*)\'"
		pattern = re.compile(regex)
		matcher = pattern.findall(pageContent)
		if matcher:
			idValue = matcher[0]
			m3u8Url = "http://web-play.pptv.com/web-m3u8-"+idValue+".m3u8?type=m3u8.web.pad&playback=0&kk=&o=leader.pptv.com&rcc_id=0"
			
		else:
			logger.debug("NOT MATCHED")
			m3u8Url = None
	return m3u8Url
