"""Projectweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from Project.views import *
admin.autodiscover()



urlpatterns = [

    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^$', archive, name='home'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', register, name='register'),
    url(r'^add/$', Createbid.as_view(), name="add_bid"),
    url(r'^savebid/$', savebid),
    url(r'^editbid/(\d+)/$', editbid),
    url(r'^search/', search),
    url(r'^apisearch/', api_search),
    url(r'^updatebid/(\d+)/$', updatebid),
    url(r'^makebid/(\d+)/$', makebid),
    url(r'^banbid/(\d+)/$', bann_auction),
    url(r'^editprofile/(\d+)/$', changelanguage,name='editprofile'),
    url(r'^editP/$', editP,name='editprofile'),
    url(r'^editL/$', editL,name='editL'),
    url(r'^showDetails/(\d+)/$', showBidDetails,name='showDetails'),

]

