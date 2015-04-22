# -*- coding: utf-8 -*-
from live_libs.utils import LIVEINFO, Jsonify
from live_models.LiveModel import LiveModel
from datetime import datetime, timedelta
from time import mktime
import logging
logger = logging.getLogger('appserver')

def getLiveList(request):
	cdate = request.GET.get("cdate", datetime.now().strftime("%Y-%m-%d"))
	result = liveListHelper(cdate)
	return Jsonify(result)

def liveListHelper(cdate):
	(year, month, day) = cdate.split("-")
	ddate = datetime(year=int(year), month=int(month),  day=int(day))
	todayList = LiveModel().get_live_list(cdate)
	nextdate = ddate + timedelta(1)
	nextList = LiveModel().get_live_list(nextdate.strftime("%Y-%m-%d"))
	result = []
	for item in todayList:
		currentInfo = {}
		currentUrl = item[LIVEINFO.URL]
		if not currentUrl:
			startTime = item[LIVEINFO.CTIME]
			currentTime = mktime(datetime.now().timetuple())
			if float(currentTime) > float(startTime) + 5.0:
				continue			   							#直播时间已过，未匹配到URL， 不拉取
			else:
				currentInfo["url"] = None
				currentInfo["state"] = False					#直播时间未过， 未匹配到URL， 拉取且客户端抹灰
		else:
			currentInfo["url"] = currentUrl
			currentInfop["state"] = item[LIVEINFO.STATE]	#True: 正在直播, False: 直播结束
		currentInfo["p"] = 0
		currentInfo["lid"] = 0
		currentInfo["start"] = item[LIVEINFO.CTIME]
		currentInfo["origin"] = item[LIVEINFO.URL]
		currentInfo["start"] = item[LIVEINFO.CTIME]
		currentInfo["name"] = item[LIVEINFO.NAME]
		currentInfo["title"] = item[LIVEINFO.TITLE]
		result.append(currentInfo)
	for item in nextList:
		currentInfo = {}
		currentInfo["url"] = item[LIVEINFO.URL]
		currentInfo["state"] = False
		currentInfo["p"] = 1
		currentInfo["lid"] = 0
		currentInfo["start"] = item[LIVEINFO.CTIME]
		currentInfo["origin"] = item[LIVEINFO.URL]
		currentInfo["start"] = item[LIVEINFO.CTIME]
		currentInfo["name"] = item[LIVEINFO.NAME]
		currentInfo["title"] = item[LIVEINFO.TITLE]
		currentInfo["state"] = True
		result.append(currentInfo)
	return result