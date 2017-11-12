from django.contrib import admin

# Register your models here.
from Project.models import *
admin.site.register(Auction)
admin.site.register(Bids)
admin.site.register(User_profile)