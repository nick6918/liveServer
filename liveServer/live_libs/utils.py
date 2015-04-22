import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

class Jsonify(HttpResponse):
	"""docstring for jsonify"""
	def __init__(self,content='',*arg, **kw):
		super(Jsonify, self).__init__(content,*arg, **kw)
		self.content = json.dumps(content,indent=4,sort_keys=True,cls=DjangoJSONEncoder,ensure_ascii=False)
		self['Content-Type']='application/json; charset=utf-8'
		self['Vary']= 'Accept-Encoding'
		self['Content-Length'] = len(self.content)

class LIVEINFO:
	NAME = 0
	TITLE = 1
	CTIME = 2
	DTIME = 3
	DATETIME = 4
	URL = 5
	STATE = 6
	VID = 7
	PICTURE = 8
	def __init__(self):
        	pass