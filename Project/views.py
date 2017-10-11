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
from datetime import datetime, timedelta
from django.conf import settings
from django.core.paginator import Paginator
from django.utils import translation




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


# @login_required(login_url='/login')

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
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))




def archive(request):

    bid = Auction.objects.order_by('-timestamp')
    bid2 = Auction.objects.all()

    for a in bid2:
        a2 = datetime.now()
        print(str(a2))
        b2 = a.bid_res
        print(str(b2))


        if str(b2)<str(a2):
            print("smaller")
            print(a.active," before ")
            a.active = 0
            a.save()
            print(a.active," after")
        else:
            print("bigger")



    if request.user.is_authenticated():
        return render(request, "bidlist.html",{'bid':bid,
                                               'authuser': request.user})
    else:
        return render(request, "bidlist.html",{'bid':bid,
                                               'guest':'Your are not loged in, please log in to bid!'})





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

    return HttpResponseRedirect(reverse("home"))


def search(request):
    if request.method == "GET":
        searchText=request.GET["id"]
        bid = Auction.objects.filter(title__contains=searchText)
        if request.user.is_authenticated():
            return render(request, "bidlist.html",{'bid':bid,
                                               'authuser': request.user})
        else:
            return render(request, "bidlist.html",{'bid':bid,
                                               'guest':'Your are not loged in, please log in to bid!'})

def delete_auction(request,id):
    if request.method=="GET":
        Auction.objects.get(pk=id).delete()
        messages.add_message(request, messages.INFO, "Auction banned!")
    return HttpResponseRedirect(reverse("home"))



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

        language = request.GET['dropdown']
        print(language)

        if language=='en':
            translation.activate('en')
            request.session[translation.LANGUAGE_SESSION_KEY] = 'en'
        if language=='al':
            translation.activate('al')
            request.session[translation.LANGUAGE_SESSION_KEY] = 'al'


    except  User.DoesNotExist:
        messages.add_message(request, messages.INFO, "User doesnt exist, stop hacking my page!")


    messages.add_message(request, messages.INFO, "Changes to profile made!")

    return HttpResponseRedirect(reverse("home"))

def editP(request):
    return render(request, "editprofile.html")