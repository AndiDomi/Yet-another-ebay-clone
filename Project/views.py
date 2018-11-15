import decimal
import random

import requests
from django.core import serializers
import math
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views import View
# Create your views here.
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from Project.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse

from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib import messages
from Project.models import Auction
from Project.models import Bids
from Project.models import User_profile
from datetime import datetime, timedelta, date, time
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import translation
from django.core.mail import send_mail
import json

from django.contrib.auth.signals import user_logged_in


# function that runs when we log in
# in this case it just changes the language to the user prefered one
def on_login_do(sender, user, request, **kwargs):
    print('we are in login')
    if request.user.is_superuser:
        language = 'en'
    else:
        language = user.user_profile.language
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language


# when user logs in funciton
user_logged_in.connect(on_login_do)


# TODO: check if the bid is active in all the views that are called

def register(request):
    print('we are in register')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            userprofile = User_profile.objects.create(user=new_user, language='en')
            userprofile.save()
            messages.add_message(request, messages.INFO, "New User is created. Please Login")

            return HttpResponseRedirect(reverse("home"))
        else:
            form = SignUpForm(request.POST)
    else:
        form = SignUpForm()

    return render(request, "register.html", {'form': form})


@method_decorator(login_required, name="dispatch")
class Createbid(View):
    def get(self, request):
        print('we are in create bid get')
        global time_min
        time_min = datetime.now() + timedelta(hours=72)
        print(datetime.now())
        time_min = time_min.strftime('%Y-%m-%dT%H:%M')
        print(time_min)
        return render(request, 'createbid.html', {'time': time_min})

    def post(self, request):
        print('we are in create bid post')
        form = CreateBid(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            bid_t = cd['title']
            bid_details = cd['details']
            bid_bid = cd['bid']
            bid_res = cd['bid_res']
            if bid_res < time_min:
                bid_res = time_min
            print("cd bid", bid_res)
            form = confBid()
            return render(request, 'wizardtest.html', {'form': form,
                                                       "b_title": bid_t,
                                                       "b_details": bid_details,
                                                       "b_bid": bid_bid,
                                                       "b_res": bid_res})
        else:
            messages.add_message(request, messages.ERROR, )
            return render(request, 'createbid.html', {'form': form, })


def savebid(request):
    option = request.POST.get('option', '')
    print('we are in save bid')
    if option == 'Yes':
        b_title = request.POST.get('b_title', '')
        b_details = request.POST.get('b_details', '')
        b_bid = request.POST.get('b_bid', )
        if float(b_bid) < 0.01:
            b_bid = str(float(b_bid) + 0.01)
        b_res = request.POST.get('b_res', )
        bid_user = User.objects.get(username=request.user.username)
        bid_user = str(bid_user)
        auction_save = Auction.objects.create(title=b_title, details=b_details, bid_res=b_res, timestamp=datetime.now(),
                                              author=request.user, active=1, last_bid=b_bid, last_bider=bid_user)
        auction_save.save()

        bids_save = Bids.objects.create(
            bid=b_bid,
            auction=auction_save,
            bid_by=User.objects.get(username=request.user.username)
        )
        print(b_bid)
        bids_save.save()
        messages.add_message(request, messages.INFO, "New auction has been created!")

        sendMailAuthor(request.user, auction_save)

        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))


## todo: add api
def archive(request):
    print('we are in achieve')
    dollar = exhange_rate()
    # if superuser
    if request.user.is_superuser:
        auction = Auction.objects.order_by('-timestamp')
        print('superuser' + str(request.user))
        return render(request, "bidlist.html", {'auction': auction,
                                                'authuser': str(request.user), 'dollar': dollar})


    # if normal user
    elif request.user.is_authenticated():
        auction = Auction.objects.filter(banned=False).order_by('-timestamp')
        print('user ' + str(request.user))
        return render(request, "bidlist.html", {'auction': auction,
                                                'authuser': str(request.user), 'dollar': dollar})

    # if guest
    else:
        auction = Auction.objects.filter(banned=False).order_by('-timestamp')

        print('guest' + str(request.user))
        return render(request, "bidlist.html", {'auction': auction, 'dollar': dollar,
                                                'guest': 'Your are not loged in, please log in to bid!'})


def exhange_rate():
    r = requests.get(
        'http://data.fixer.io/api/latest?access_key=d46d2d7ac1dfe0569dd3989e34356db8&symbols=USD&format=1', )
    dollar = json.loads(r.text)
    dollar = dollar["rates"]["USD"]
    return dollar


## TODO: add concurrency
def editbid(request, offset):
    print('we are in edit bid')
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    else:
        auction = get_object_or_404(Auction, id=offset)
        bid = get_object_or_404(Bids, auction=offset)
        print(type(auction.last_bider))
        return render(request, "editbid.html",
                      {'author': auction.author,
                       "title": auction.title,
                       "id": auction.id,
                       "bid_details": auction.details,
                       "bid_res": auction.bid_res,
                       "bid_by": bid.bid_by,
                       "version": auction.version
                       })


## todo: add concurrncy
def updatebid(request, offset):
    print('we are in update')
    print(offset)
    auction = Auction.objects.get(id=offset)
    print(auction.id)
    if request.method == "POST":
        details = request.POST["details"]
        print(details)
        auction.details = details
        print(auction.version)
        auction.version += auction.version
        auction.save()
        messages.add_message(request, messages.INFO, "Bid updated")
    return HttpResponseRedirect(reverse("home"))


## todo: add concurrency
## todo: add api
def makebid(request, offset):

    auction = Auction.objects.get(id=offset)
    if request.method == "POST":
        bidmade = request.POST["bid"].strip()
        request_version = request.POST["version"]
        if float(request_version) >= float(auction.version):
            if float(bidmade) > auction.last_bid + decimal.Decimal('0.01'):
                auction.last_bid = bidmade
                auction.last_bider = request.user.username
                auction.version = auction.version + auction.version
                auction.save()
                bids_save = Bids.objects.create(
                    bid=bidmade,
                    auction=auction,
                    bid_by=User.objects.get(username=request.user.username)
                )
                bids_save.save()
                messages.add_message(request, messages.INFO, "Bid made!")
                sendMailAll('A new bid was made!', offset)
                return HttpResponseRedirect(reverse("home"))
            else:
                messages.add_message(request, messages.INFO,
                                     "We are sorry but the bid you made is less than the previews one, please try again!")
                return redirect("/showDetails/" + str(auction.id)+'/')
        else:
            messages.add_message(request, messages.INFO,
                                 "We are sorry but the auction was updated while you tried to bid, please try again!")
            return redirect("/showDetails/" + str(auction.id) + "/")
    else:
        return HttpResponseRedirect(reverse("home"))


# in here we search for different auctions
# search is done only by title to keep things a bit simplier
def search(request):
    print('we are in search')
    dollar = exhange_rate()
    if request.method == "GET":
        searchText = request.GET["id"]

        if request.user.is_superuser:
            print("is superuser")
            auction = Auction.objects.filter(title__contains=searchText)

            return render(request, "bidlist.html", {'auction': auction,
                                                    'authuser': request.user,'dollar':dollar})

        elif request.user.is_authenticated():
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            return render(request, "bidlist.html", {'auction': auction,
                                                    'authuser': request.user,'dollar':dollar})

        else:
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            return render(request, "bidlist.html", {'auction': auction,
                                                    'guest': 'Your are not loged in, please log in to bid!','dollar':dollar})


## todo: Concurrency?
def bann_auction(request, id):
    print('we are in ban')
    if request.method == "GET":
        auction_to_bann = Auction.objects.get(pk=id)
        auction_to_bann.banned = True
        auction_to_bann.save()
        messages.add_message(request, messages.INFO, "Auction banned!")
    return HttpResponseRedirect(reverse("home"))


## done
def changelanguage(request, iduser):
    print('we are in change language')
    try:
        user = User.objects.get(id=iduser)
        if request.GET['password']:
            user.set_password(request.GET['password'])
            user.save()
            print(user.password)
        if request.GET['email']:
            user.email = request.GET['email']
            user.save()
    except User.DoesNotExist:
        messages.add_message(request, messages.INFO, "User doesnt exist, stop hacking my page!")

    messages.add_message(request, messages.INFO, "Changes to profile made!")

    return HttpResponseRedirect(reverse("home"))


def editP(request):
    return render(request, "editprofile.html")


# function to select langauge and save it
def editL(request):
    print('we are in edit language')
    if request.POST['dropdown']:
        # get the language from the request
        language = request.POST['dropdown']

        # if user is active, save it in database
        if request.user.is_authenticated():
            save_language_user = User_profile.objects.get(user=request.user)
            save_language_user.language = language
            save_language_user.save()
            # then select the prefered lengauge
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language

        else:
            # if not active just change the leanguage
            if language == 'en':
                translation.activate('en')
                request.session[translation.LANGUAGE_SESSION_KEY] = 'en'
            if language == 'al':
                translation.activate('al')
                request.session[translation.LANGUAGE_SESSION_KEY] = 'al'

        messages.add_message(request, messages.INFO, "Changes to language made!")

        return HttpResponseRedirect(reverse("home"))
    else:
        messages.add_message(request, messages.INFO, "No clear input defined please try again")
        return HttpResponseRedirect(reverse("home"))


# to check if the bids are active
def isBidActive(bid2):
    print('we are in is bid active')
    for a in bid2:
        a2 = datetime.now()
        b2 = a.bid_res
        if str(b2) < str(a2):
            a.active = 0
            a.save()


# send emails to the one who are partecipating in this auction
def sendMailAll(what_happened, auction):
    send_spam_to = []
    for p in User.objects.raw(
                    'SELECT Project_bids.bid_by_id as id from Project_bids WHERE Project_bids.auction_id=' + str(
                    auction)):
        print(User.objects.get(username=p).email)
        send_spam_to.append(User.objects.get(username=p).email)
    send_mail('subject', what_happened, 'noreply@parsifal.co', send_spam_to)


def sendMailAuthor(user, auction):
    user2 = User.objects.get(username=user)
    print(user2)
    sent_TO = str(user2.email)
    print(sent_TO)
    email_message = " Hello " + str(user2) + '! You just created an auction with Title : "' + str(auction.title) + \
                    '" with Detail: "' + str(auction.details) + '" bid resoultion time: ' + str(
        auction.bid_res) + " and minimum bid of " + str(auction.last_bid + ""
                                                                           ' please, go here http://127.0.0.1:8000/showDetails/' + str(
        auction.id) + '  to have a look at your auction!')
    send_mail('subject', email_message, 'isAwesome@andi.domi', [user2.email])


def showBidDetails(request, offset):
    dollar = exhange_rate()
    print('we are in show bid details')
    print('lets see the request first')
    print(request)
    print('but also lets see the offset')
    print(offset)
    if request.user.is_authenticated:
        auction = Auction.objects.filter(id=offset)
        return render(request, "bidlist.html", {'auction': auction, 'authuser': request.user,'dollar':dollar})
    else:
        messages.add_message(request, messages.INFO, "You are not logged in, please login to see the auction details")
        return HttpResponseRedirect(reverse("/login/"))

# in here we search for an auction through api
# because i dont really have time i copied the entire
def api_search(request):
    print('we are in search')
    if request.method == "GET":
        searchText = request.GET["id"]
        if request.user.is_superuser:
            print("is superuser")
            auction = Auction.objects.filter(title__contains=searchText)

            auctions_ser = serializers.serialize('json', auction)
            struct = json.loads(auctions_ser)
            auctions_ser = json.dumps(struct)
            return HttpResponse(auctions_ser, content_type='application/json')

        elif request.user.is_authenticated():
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            auctions_ser = serializers.serialize('json', auction)
            struct = json.loads(auctions_ser)
            auctions_ser = json.dumps(struct)
            return HttpResponse(auctions_ser, content_type='application/json')

        else:
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            auctions_ser = serializers.serialize('json', auction)
            struct = json.loads(auctions_ser)
            auctions_ser = json.dumps(struct)
            return HttpResponse(auctions_ser, content_type='application/json')



# in this function we create random users and emials
# all the password are = "passpass"
# ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
# normaly you have once 1/10000000000000000 to generate an exception
# by generatin the same username
def createRandomStuff(request):
    if request.method == "GET":
        numbers_of_random = request.GET["id"]
        print(numbers_of_random)
        i = 1
        while i <= int(numbers_of_random):
            random_number = str(random.randint(1, 10000000000000000))
            random_username = "user" + random_number
            random_email = random_number+"abo.fi"
            new_user = User.objects.create(
                username=random_username,
                email=random_email,
                # passpass is the password my padawan!
                password="pbkdf2_sha256$36000$CIOL9xBIIT6e$O5P5ha6oNZlHJku7G1JN0hKVwt0dOK1zWSTTEQ4OVqg="
            )

            print(new_user)
            userprofile = User_profile.objects.create(user=new_user, language='en')
            userprofile.save()

            b_title = 'title nr' + str(i)
            b_details = 'Here there are some details and with a number of nr' + str(i)
            b_bid = random.randint(1, 10000)
            b_res = datetime.now() + timedelta(hours=72)
            bid_user = random_username
            auction_save = Auction.objects.create(title=b_title, details=b_details, bid_res=b_res,
                                                  timestamp=datetime.now(),
                                                  author=new_user, active=1, last_bid=b_bid, last_bider=bid_user)
            auction_save.save()
            i = i + 1
            bids_save = Bids.objects.create(
                bid=b_bid,
                auction=auction_save,
                bid_by=new_user
            )
            bids_save.save()

        return HttpResponse({"Code Generated:{ 'User Cloned' :{ 'Password Salted' :{ 'Cookies backed' }  } }"
                             }, content_type='application/json')
