from django.conf.urls import patterns, include, url
from views import liveParser, liveList

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'liveServer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r"^live/parseurl$", liveParser.parseUrl),
    url(r"^live/getlivelist$", liveList.getLiveList)
)
