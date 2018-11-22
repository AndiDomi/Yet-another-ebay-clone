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
    url(r'^login/$', login_user, name='login'),
    url(r'^$', list_auctions, name='home'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', register_user, name='register'),
    url(r'^add_auction/$', add_auction.as_view(), name="add_bid"),
    url(r'^savebid/$', save_auction),
    url(r'^edit_auction/(\d+)/$', edit_auction),
    url(r'^search/$', search),
    url(r'^edit_auction_details/(\d+)/$', edit_auction_details),
    url(r'^makebid/$',bid),
    url(r'^ban_auction/(\d+)/$', bann_auction),
    url(r'^edit_profile/(\d+)/$', changelanguage,name='editprofile'),
    url(r'^editP/$', editP,name='editprofile'),
    url(r'^edit_language/$', editL,name='editL'),
    url(r'^showDetails/(\d+)/$', show_auction_details, name='showDetails'),
    url(r'^randomize/$', create_n_users),
    url(r'^auctionapi/$', create_auction_api),
    url(r'^bidapi/$', bid_api),
]

