import math
from django.shortcuts import render
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
from datetime import datetime, timedelta
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import translation
from django.core.mail import send_mail

# TODO: check if the bid is active in all the views that are called

## done
def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()

            messages.add_message(request, messages.INFO, "New User is created. Please Login")

            return HttpResponseRedirect(reverse("home"))
        else:
            form = SignUpForm(request.POST)
    else:
        form = SignUpForm()

    return render(request, "register.html", {'form': form})


## done
@method_decorator(login_required, name="dispatch")
class Createbid(View):
    def get(self, request):
        time_min=datetime.now()+ timedelta(hours=72)
        time_min=str(time_min.strftime('%Y-%m-%dT%H:%m'))
        return render(request, 'createbid.html',{'time':time_min})


    def post(self, request):
        form = CreateBid(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            bid_t = cd['title']
            bid_details = cd['details']
            bid_bid = cd['bid']
            bid_res = cd['bid_res']
            print("cd bid",bid_res)
            form = confBid()
            return render(request, 'wizardtest.html', {'form': form,
                                                       "b_title": bid_t,
                                                       "b_details": bid_details,
                                                       "b_bid": bid_bid,
                                                       "b_res": bid_res})
        else:
            messages.add_message(request, messages.ERROR, )
            return render(request, 'createbid.html', {'form': form, })



## TODO: save all the users who did a bid
## TODO: send an email to all the users who bided
## TODO: Add concurrency
def savebid(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        b_title = request.POST.get('b_title', '')
        b_details = request.POST.get('b_details', '')
        b_bid = request.POST.get('b_bid', )
        b_res = request.POST.get('b_res', )
        bid_save = Auction(title=b_title, details=b_details, bid=b_bid, bid_res=b_res, timestamp=datetime.now(),
                           author= request.user,bid_by= request.user,active=1)
        bid_save.save()
        messages.add_message(request, messages.INFO, "New bid has been saved")
        sendMailAuthor(bid_save)
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))



## todo: add api
def archive(request):

    ##check if bid is active
    isBidActive(Auction.objects.all())

    # if superuser
    if request.user.is_superuser:
        bid = Auction.objects.order_by('-timestamp')
        return render(request, "bidlist.html", {'bid': bid,
                                            'authuser': request.user})

    # if normal user
    elif request.user.is_authenticated():
        bid = Auction.objects.filter(banned=False).order_by('-timestamp')
        return render(request, "bidlist.html",{'bid':bid,
                                               'authuser': request.user})
    #if guest
    else:
        bid = Auction.objects.filter(banned=False).order_by('-timestamp')
        return render(request, "bidlist.html", {'bid': bid,
                                                'guest': 'Your are not loged in, please log in to bid!'})



## TODO: add concurrency
def editbid(request, offset):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    else:
        bid = get_object_or_404(Auction, id=offset)

        return render(request, "editbid.html",
                {'author': request.user,
                "title": bid.title,
                "id": bid.id,
                "bid_details": bid.details,
                "bid_res": bid.bid_res,
                "bid_by": bid.bid_by
                    })







## todo: add concurrncy
def updatebid(request, offset):
    bids = Auction.objects.filter(id= offset)
    if len(bids) > 0:
        bid = bids[0]
    else:
        messages.add_message(request, messages.INFO, "Invalid bid id")
        return HttpResponseRedirect(reverse("home"))

    if request.method=="POST":

        details = request.POST["details"]
        bid.details = details
        bid.save()
        messages.add_message(request, messages.INFO, "Bid updated")

    return HttpResponseRedirect(reverse("home"))


## todo: add concurrency
## todo: saver user who made the bid
## todo: add api
def makebid(request, offset):
    bids = Auction.objects.filter(id= offset)
    if len(bids) > 0:
        bid = bids[0]
    else:
        messages.add_message(request, messages.INFO, "Invalid bid id")
        return HttpResponseRedirect(reverse("home"))

    if request.method == "POST":
        bidmade = request.POST["bid"].strip()
        bid.bid = bidmade
        bid.bid_by = request.user
        bid.save()
        messages.add_message(request, messages.INFO, "Bid made!")
        sendMailAll('A new bid was made!',offset)

    return HttpResponseRedirect(reverse("home"))

# done
def search(request):
    if request.method == "GET":
        searchText=request.GET["id"]

        if request.user.is_superuser:
            bid = Auction.objects.filter(title__contains=searchText,banned=True)
            return render(request, "bidlist.html", {'bid': bid,
                                                    'authuser': request.user})

        elif request.user.is_authenticated():
            bid = Auction.objects.filter(title__contains=searchText,banned=False)
            return render(request, "bidlist.html", {'bid': bid,
                                                    'authuser': request.user})

        else:
            bid = Auction.objects.filter(title__contains=searchText,banned=False)
            return render(request, "bidlist.html",{'bid':bid,
                                               'guest':'Your are not loged in, please log in to bid!'})
## todo: Concurrency?
def bann_auction(request,id):
    if request.method=="GET":
        auction_to_bann = Auction.objects.get(pk=id)
        auction_to_bann.banned=True
        auction_to_bann.save()
        messages.add_message(request, messages.INFO, "Auction banned!")
    return HttpResponseRedirect(reverse("home"))


## done
def changelanguage(request,iduser):
    try:
        user = User.objects.get(id=iduser)
        print(user.password)
        if request.GET['password']:
            user.set_password(request.GET['password'])
            user.save()
            print(user.password)
        if request.GET['email']:
            user.email=request.GET['email']
            user.save()

    except  User.DoesNotExist:
        messages.add_message(request, messages.INFO, "User doesnt exist, stop hacking my page!")


    messages.add_message(request, messages.INFO, "Changes to profile made!")

    return HttpResponseRedirect(reverse("home"))

def editP(request):
    return render(request, "editprofile.html")

# done
def editL(request):
    print("hello editL")
    print(request.POST['dropdown'])
    if request.POST['dropdown']:
        language = request.POST['dropdown']
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
    for a in bid2:
        a2 = datetime.now()
        b2 = a.bid_res
        if str(b2)<str(a2):
            a.active = 0
            a.save()


# send emails to the one who are partecipating in this auction
def sendMailAll(what_happened,auction_ID):
    auction = Auction.objects.get(pk=auction_ID)
    auction.bid_by
    user = User.objects.get(username=auction.bid_by)
    a = user.email
    print(a)
    #send_mail('subject', what_happened, 'noreply@parsifal.co',a)

def sendMailAuthor(bidsave):
    user = User.objects.get(username=bidsave.author)
    sent_TO = str(user.email)
    print (sent_TO)
    email_message= " Hello "+ str(bidsave.author)+ '! You just created a bid with Title : "'+ str(bidsave.title)+\
                   '" with Detail: "' + str(bidsave.details) + '" bid resoultion time: ' + str(bidsave.bid_res) + " and minimum bid of " + str(bidsave.bid)
    send_mail('subject', email_message, 'imAwesome@andi.comi',[user.email])

