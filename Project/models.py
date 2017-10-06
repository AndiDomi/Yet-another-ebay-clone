import datetime

import django
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,related_name="author")
    details = models.TextField(null=True)
    bid = models.DecimalField(max_digits=10,decimal_places=1,null=True)
    bid_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,related_name="bid_by")
    bid_res = models.IntegerField(default=1,null=True)
    timestamp = models.DateTimeField(default=django.utils.timezone.now ,null=True)


    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['timestamp']