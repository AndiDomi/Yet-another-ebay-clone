import datetime

import django
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,related_name="author")
    details = models.TextField(null=True)
    bid_res = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(null=True)
    active = models.IntegerField()
    banned = models.BooleanField(default=False)
    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['timestamp']

class Bids(models.Model):
    bid = models.DecimalField(primary_key=True,max_digits=10,decimal_places=1)
    auction = models.ForeignKey(Auction.id)
    bid_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,related_name="bid_by")