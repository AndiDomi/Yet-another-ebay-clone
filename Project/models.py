import datetime

import django
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import MinValueValidator

class Auction(models.Model):
    id = models.AutoField(primary_key=True,unique=True)
    title = models.CharField(max_length=200, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,related_name="author")
    details = models.TextField(null=True)
    bid_res = models.DateTimeField(null=True)
    timestamp = models.DateTimeField(null=True)
    active = models.IntegerField()
    banned = models.BooleanField(default=False)
    last_bider = models.TextField(null=True)
    last_bid = models.DecimalField(max_digits=10,decimal_places=2,null=True,default=0.01,validators=[MinValueValidator(0.01)])
    version = models.DecimalField(decimal_places=1, default=0.1, max_digits=10)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['timestamp']

class Bids(models.Model):
    id = models.AutoField(primary_key=True,unique=True)
    bid = models.DecimalField(max_digits=100,decimal_places=2,null=True,default=0.01,validators=[MinValueValidator(0.01)])
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bid_by = models.ForeignKey(User, null=True, blank=True)

class User_profile(models.Model):
    user = models.OneToOneField(User)
    language= models.CharField(max_length=3,default="en")
