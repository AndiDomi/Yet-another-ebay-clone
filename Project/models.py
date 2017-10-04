from django.db import models

# Create your models here.
from django.utils import timezone


class Auction(models.Model):
    title = models.ForeignKey('auth.User')
    details = models.CharField(max_length=200)
    bid = models.TextField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title