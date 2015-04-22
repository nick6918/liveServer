import logging
from django.db import connection
from datetime import datetime, timedelta
logger = logging.getLogger('appserver')

class LiveModel(object):

	def __init__(self):
		super(LiveModel, self).__init__()  
		self.cursor = connection.cursor()

	def query_backup(self, sid, vid):
		exe_string = "SELECT backUrl, backState FROM live_backup WHERE vid=%s and sid=%s"
		self.cursor.execute(exe_string, (vid , sid))
		items = self.cursor.fetchone()
		if items:
			if items[1] == "UNUSED":
				return {"nextState":1}
			elif  items[1] == "STOPPED":
				return {"nextState": 4}
			else:
				return {"nextState": 3, "url":items[0]}
		else:
			exe_string = "INSERT INTO live_backup(vid, sid) VALUES(%s, %s)"
			self.cursor.execute(exe_string, (vid, sid))
			return {"nextState":1}

	def update_backup(self, backUrl, state, sid, vid):
		exe_string = "UPDATE live_backup Set backUrl=%s, backState=%s WHERE vid=%s and sid=%s"
		self.cursor.execute(exe_string, (backUrl,  state, vid , sid))
		return True

	def get_live_list(self, dtime):
		exe_string = "SELECT ld.name, ld.title, ld.ctime, ld.dtime, ld.datetime, ml.url, ml.state, ld.vid, ld.pic FROM live_daylist as ld LEFT JOIN m3u8live as ml on ld.vid=ml.vid WHERE ld.datetime = %s"
		if isinstance(dtime, datetime):
			self.cursor.execute(exe_string, (dtime.now().strftime("%Y-%m-%d")))
		else:
			self.cursor.execute(exe_string, (dtime, ))
		itemList = self.cursor.fetchall()
		return itemList










