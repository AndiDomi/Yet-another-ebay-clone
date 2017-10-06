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
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib import messages
import datetime
from django.conf import settings


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
        form = CreateBid()
        return render(request, 'createbid.html', {'form': form})

    def post(self, request):
        form = CreateBid(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            bid_t = cd['title']
            bid_details = cd['details']
            bid_bid = cd['bid']
            bid_res = cd['bid_res']
            form = confBid()
            return render(request, 'wizardtest.html', {'form': form,
                                                       "b_title": bid_t,
                                                       "b_details": bid_details,
                                                       "b_bid": bid_bid,
                                                       "b_res": bid_res})
        else:
            messages.add_message(request, messages.ERROR, "Not valid data")
            return render(request, 'createbid.html', {'form': form, })


def savebid(request):
    option = request.POST.get('option', '')
    if option == 'Yes':
        b_title = request.POST.get('b_title', '')
        b_details = request.POST.get('b_details', '')
        b_bid = request.POST.get('b_bid', )
        b_res = request.POST.get('b_res', )

        bid_save = Auction(title=b_title, details=b_details, bid=b_bid, bid_res=b_res, timestamp=datetime.datetime.now(),
                           author= request.user,bid_by= request.user)
        bid_save.save()
        messages.add_message(request, messages.INFO, "New bid has been saved")
        return HttpResponseRedirect(reverse("home"))
    else:
        return HttpResponseRedirect(reverse("home"))




def archive(request):

    bid = Auction.objects.order_by('-timestamp')
    print("we are here now!")
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
