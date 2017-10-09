from time import timezone

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
from  Project.models import Auction
from Projectweb import settings


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class CreateBid(forms.Form):
    title = forms.CharField(max_length=200,label='Title of the auction ')
    details = forms.CharField(widget=forms.Textarea(), required=False, label="The description of the auction ")
    bid = forms.DecimalField(max_digits=10,decimal_places=2,label="Starting bid (€) ")
    bid_res = forms.DateField(input_formats=['%Y-%M-%D '],label="Time for the bid to be active (minimum is set to 72h)")





class confBid(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    #b_title = forms.CharField(widget=forms.HiddenInput())



