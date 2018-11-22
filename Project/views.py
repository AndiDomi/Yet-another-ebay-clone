import decimal
import random
import requests

from django.core import serializers
from django.views import View
from django.contrib.auth import login, authenticate
from django.shortcuts import redirect
from Project.forms import *
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.contrib import messages
from Project.models import Auction
from Project.models import Bids
from Project.models import User_profile
from datetime import datetime, timedelta
from django.utils import translation
from django.core.mail import send_mail
import json


# done
def is_auction_active():
    time_now=datetime.now() + timedelta(hours=72)
    try:
        auctions = Auction.objects.filter(active=1)
        for item in auctions:
            if item.bid_res < datetime.now():
                item.active=0
                item.save()
                sendMailAll('Auction is resloved! The winner is '+str(item.last_bider), item.id)
    except:
        print(' we have no actions to make')

# done
def login_user(request):
    is_auction_active()
    if request.method == 'GET':
        print('we are in login get')
        return render(request, "login.html")
    else:
        print(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                language = 'en'
            else:
                language = user.user_profile.language
            messages.add_message(request, messages.INFO, "Login Successful")
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            return HttpResponseRedirect(reverse("home"))
        else:
            messages.add_message(request, messages.INFO, "Couldn't log in, please try again")
            return HttpResponseRedirect(reverse("home"))


# when user logs in funciton


def sendMailAll(what_happened, auction_id):
    send_spam_to = []
    for p in User.objects.raw(
                    'SELECT Project_bids.bid_by_id as id from Project_bids WHERE Project_bids.auction_id=' + str(
                    auction_id)):
        print(User.objects.get(username=p).email)
        send_spam_to.append(User.objects.get(username=p).email)
    send_mail('subject', what_happened, 'noreply@parsifal.co', send_spam_to)


def sendMailAuthor(user, auction):
    user2 = User.objects.get(username=user)
    sent_TO = str(user2.email)
    email_message = " Hello " + str(user2) + '! You just created an auction with Title : "' + str(auction.title) + \
                    '" with Detail: "' + str(auction.details) + '" bid resoultion time: ' + str(
        auction.bid_res) + " and minimum bid of " + str(auction.last_bid + ""
                                                                           ' please, go here http://127.0.0.1:8000/showDetails/' + str(
        auction.id) + '  to have a look at your auction!')
    send_mail('subject', email_message, 'isAwesome@andi.domi', [user2.email])


# done
def register_user(request):
    is_auction_active()
    print('we are in register')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            print(form)
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
class add_auction(View):
    is_auction_active()
    def get(self, request):
        print('get add auction'+str(request))
        global time_min
        time_min = datetime.now() + timedelta(hours=72)

        time_min = time_min.strftime('%Y-%m-%dT%H:%M')
        print(time_min)
        return render(request, 'createbid.html', {'time': time_min})

    def post(self, request):
        print('we are in post')
        form = CreateBid(request.POST)
        try:
            if form.is_valid():
                cd = form.cleaned_data
                bid_t = cd['title']
                if bid_t == "":
                    messages.add_message(request, messages.INFO, "Title is empty, try again")
                    return render(request, 'createbid.html', {'form': form})
                bid_details = cd['details']
                bid_bid = cd['bid']
                if bid_bid == "":
                    bid_bid = 0.01
                bid_res = cd['bid_res']
                if bid_bid == "":
                    bid_res = time_min
                if bid_res < time_min:
                    bid_res = time_min
                form = confBid()
                return render(request, 'wizardtest.html', {'form': form,
                                                           "b_title": bid_t,
                                                           "b_details": bid_details,
                                                           "b_bid": bid_bid,
                                                           "b_res": bid_res})
            else:
                messages.add_message(request, messages.INFO, "well..well..well..something went wrong...")
                return render(request, 'createbid.html', {'form': form })
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
            return render(request, 'createbid.html', {'form': form})


def save_auction(request):
    is_auction_active()
    option = request.POST.get('option')
    if option == 'Yes':
        try:
            b_title = request.POST.get('b_title')
            if b_title=="":
                raise NameError('Title is empty!')
            b_details = request.POST.get('b_details')
            b_bid = request.POST.get('b_bid')
            if b_bid=="":
                raise NameError('You didnt put a starting bid!')
            if float(b_bid) < 0.01 and float(b_bid)==0:
                b_bid = str(float(b_bid) + 0.01)
            b_res = request.POST.get('b_res')
            if b_res==""  :
                raise NameError('Resolution time is empty, please try again!')
            try:
                datetime.strptime(b_res, '%Y-%m-%dT%H:%M')
            except ValueError:
                raise ValueError("Incorrect data format, should be Y-m-dT%H:M")
            if b_res < str(datetime.now()+ timedelta(hours=72)):
                raise NameError('Resolution time is in less then 72 hours, please try again!')
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
        except Exception as e:
            messages.add_message(request, messages.INFO, e)
            return HttpResponseRedirect(reverse("add_bid"))
    else:
        messages.add_message(request, messages.INFO, "You should agree our terms and conditions")
        return HttpResponseRedirect(reverse("add_bid"))



def list_auctions(request):
    is_auction_active()
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



def edit_auction(request, offset):
    is_auction_active()
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

def edit_auction_details(request, offset):
    is_auction_active()
    auction = Auction.objects.get(id=offset)
    print(auction.id)
    if request.method == "POST":
        if auction.active==1:
            details = request.POST["details"]
            print(details)
            auction.details = details
            print(auction.version)
            auction.version += auction.version
            auction.save()
            messages.add_message(request, messages.INFO, "Auction details updated!")
            sendMailAll('Auction details updated by the OP!',offset)
        else:
            messages.add_message(request, messages.INFO, "You cannot bid in a resolver auction!")
    else:
        messages.add_message(request, messages.INFO, "The request you made was not a get one!")
    return HttpResponseRedirect(reverse("home"))


def bid(request):
    is_auction_active()
    print(request)
    try:
        if request.user.is_authenticated():
            if request.method == "POST":
                print('post')
                auctionID = request.POST["auction_ID"]
                if auctionID == "" or not auctionID:
                    raise NameError('Auction ID is empty, please try again!')
                auction = Auction.objects.get(id=auctionID)
                if not auction:
                    raise NameError('Auction ID doesnt exist!')
                if auction.active==0:
                    raise NameError('You cannot bid in a resolved auction!')
                bidmade = request.POST["bid"].strip()
                if bidmade == "":
                    raise NameError('You didnt put a bid number, please try again!')
                request_version = request.POST["version"]
                if float(request_version) >= float(auction.version):
                    if float(bidmade) >= auction.last_bid + decimal.Decimal('0.01'):
                        print(auction.last_bid + decimal.Decimal('0.01'))
                        auction.last_bid = bidmade
                        auction.last_bider = request.user.username
                        auction.version = auction.version + auction.version
                        auction.save()
                        # here we add 5 min to the bid if its close to the deadline
                        if auction.bid_res < datetime.now()+timedelta(minutes=5):
                            auction.bid_res += timedelta(minutes=5)
                        bids_save = Bids.objects.create(
                            bid=bidmade,
                            auction=auction,
                            bid_by=User.objects.get(username=request.user.username)
                        )
                        bids_save.save()
                        # sendMailAll('A new bid was made!', offset)
                        messages.add_message(request, messages.INFO, "Bid made!")
                        return HttpResponseRedirect(reverse("home"))
                    else:
                        print(bidmade)
                        print(auction.last_bid + decimal.Decimal('0.01'))
                        messages.add_message(request, messages.INFO,
                                             "We are sorry but the bid you made is less than the previews one, please try again!")
                        return redirect("/showDetails/" + str(auction.id) + '/')
                else:
                    messages.add_message(request, messages.INFO,
                                         "We are sorry but the auction was updated while you tried to bid, please try again!")
                    return redirect("/showDetails/" + str(auction.id) + "/")
            else:
                raise NameError("We are sorry but this is not an API-GET request but a POST one")
        else:
            raise NameError("We are sorry but we do not allow bids if you are not authenticated!")

    except Exception as e:
        message_on_error = {
            "Error!": str(e)}  # dict
        message_on_error = str(message_on_error)
        message_on_error = message_on_error.replace("\'", "\"")
        messages.add_message(request, messages.INFO,message_on_error)
        return HttpResponseRedirect(reverse("home"))


# in here we search for different auctions
# search is done only by title to keep things a bit simplier
def search(request):
    is_auction_active()
    dollar = exhange_rate()
    if request.method == "GET":
        searchText = request.GET["id"]
        try:
            api_or_not = request.GET["api"]
        except:
            api_or_not = 'NO'

        if request.user.is_superuser:
            auction = Auction.objects.filter(title__contains=searchText)
            data={
                'auction': auction,
                'authuser': request.user,
                'dollar': dollar
            }
            return return_api_search(api_or_not,request,"bidlist.html",data)

        elif request.user.is_authenticated():
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            data={
                'auction': auction,
                'authuser': request.user,
                'dollar': dollar
            }
            return return_api_search(api_or_not,request,"bidlist.html",data)

        else:
            auction = Auction.objects.filter(title__contains=searchText, banned=False)
            data={
                'auction': auction,
                'authuser': request.user,
                'dollar': dollar
            }
            return return_api_search(api_or_not,request, "bidlist.html", data)



def bann_auction(request, id):
    is_auction_active()
    if request.method == "GET":
        auction_to_bann = Auction.objects.get(pk=id)
        auction_to_bann.banned = True
        auction_to_bann.save()
        messages.add_message(request, messages.INFO, "Auction banned!")
        sendMailAll('Auction banned by admin!',id)
    return HttpResponseRedirect(reverse("home"))



def changelanguage(request, iduser):
    is_auction_active()
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
    is_auction_active()
    return render(request, "editprofile.html")


# function to select langauge and save it
def editL(request):
    is_auction_active()
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



# send emails to the one who are partecipating in this auction


def show_auction_details(request, offset):
    is_auction_active()
    dollar = exhange_rate()
    if request.user.is_authenticated:
        auction = Auction.objects.filter(id=offset)
        return render(request, "bidlist.html", {'auction': auction, 'authuser': request.user,'dollar':dollar})
    else:
        messages.add_message(request, messages.INFO, "You are not logged in, please login to see the auction details")
        return HttpResponseRedirect(reverse("/login/"))


# in this function we create random users and emials
# all the password are = "passpass"
# ¨¨¨¨¨¨¨¨¨¨¨¨¨¨¨
# normaly you have once 1/10000000000000000 to generate an exception
# by generatin the same username
def create_n_users(request):
    is_auction_active()
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
        return HttpResponseRedirect(reverse("home"))



def return_api_search(is_api,request,url,data):
    if is_api=='NO':
        return render(request, url, data)
    else:

        auction = Auction.objects.filter(title__contains=9, banned=False)
        auctions_ser = serializers.serialize('json', data["auction"])
        struct = json.loads(auctions_ser)
        auctions_ser = json.dumps(struct)
        return HttpResponse(auctions_ser, content_type='application/json')

def return_api_bid(is_api,request,url,data):
    if is_api=='NO':
        return render(request, url, data)
    else:

        auction = Auction.objects.filter(title__contains=9, banned=False)
        auctions_ser = serializers.serialize('json', data["auction"])
        struct = json.loads(auctions_ser)
        auctions_ser = json.dumps(struct)
        return HttpResponse(auctions_ser, content_type='application/json')


def create_auction_api(request):
    option = request.GET["option"]
    if option == 'Yes':
        try:
            b_title = request.GET["b_title"]
            if b_title=="":
                raise NameError('Title is empty!')
                print('Title is empty!')
            b_details = request.GET['b_details']
            b_bid = request.GET['b_bid']
            if b_bid=="":
                raise NameError('You didnt put a starting bid!')
                print('You didnt put a starting bid!')
            if float(b_bid) < 0.01:
                b_bid = str(float(b_bid) + 0.01)
            b_res = request.GET['b_res']
            if b_res == "":
                raise NameError('Resolution time is empty, please try again!')
                print('Resolution time is empty, please try again!')
            try:
                datetime.strptime(b_res, '%Y-%m-%dT%H:%M')
                print()
            except ValueError:
                raise ValueError("Incorrect data format, should be Y-m-dT%H:M")
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
            bids_save.save()


            messages.add_message(request, messages.INFO, "New auction has been created!")
            # sendMailAuthor(request.user, auction_save)

            auction_2 = Auction.objects.filter(id=auction_save.id)
            auctions_ser = serializers.serialize('json', auction_2)
            struct = json.loads(auctions_ser)
            auctions_ser = json.dumps(struct)
            return HttpResponse(auctions_ser, content_type='application/json')

        except Exception as e:
            message_on_error = {
                "Error!": str(e)}  # dict
            message_on_error = str(message_on_error)
            message_on_error = message_on_error.replace("\'", "\"")
            return HttpResponse(message_on_error, content_type='application/json')
    else:
        message_on_error = {"Error!": "We are sorry but you should specify YES when making a API call as a mean to accept our condictions"}  # dict
        message_on_error = str(message_on_error)
        message_on_error=message_on_error.replace("\'", "\"")
        return HttpResponse(message_on_error, content_type='application/json')



def bid_api(request):
    is_auction_active()
    try:
        if request.user.is_authenticated():
            if request.method == "GET":
                auctionID=request.GET["aid"]
                if auctionID=="":
                    raise NameError('Auction ID is empty, please try again!')
                auction = Auction.objects.get(id=auctionID)
                if not auction:
                    raise NameError('Auction ID doesnt exist!')
                bidmade = request.GET["bid"].strip()
                if bidmade=="":
                    raise NameError('You didnt put a bid number, please try again!')

                request_version = request.GET["version"]
                if request_version:
                    request_version=auction.version
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

                        bid=Bids.objects.filter(id=bids_save.id)
                        auctions_ser = serializers.serialize('json', bid)
                        struct = json.loads(auctions_ser)
                        auctions_ser = json.dumps(struct)
                        return HttpResponse(auctions_ser, content_type='application/json')
                    else:
                        message_on_error = {
                            "Error!": "We are sorry but the bid you made is less than the previews one, please try again!"}  # dict
                        message_on_error = str(message_on_error)
                        message_on_error = message_on_error.replace("\'", "\"")
                        return HttpResponse(message_on_error, content_type='application/json')
                else:
                    message_on_error = {
                        "Error!": "We are sorry but the auction was updated while you tried to bid, please try again!"}  # dict
                    message_on_error = str(message_on_error)
                    message_on_error = message_on_error.replace("\'", "\"")
                    return HttpResponse(message_on_error, content_type='application/json')
            else:
                return HttpResponseRedirect(reverse("home"))
                message_on_error = {
                    "Error!": "We are sorry but this is not an API-GET request but a POST one"}  # dict
                message_on_error = str(message_on_error)
                message_on_error = message_on_error.replace("\'", "\"")
                return HttpResponse(message_on_error, content_type='application/json')
        else:
            raise NameError("We are sorry but we do not allow bids if you are not authenticated!")
    except Exception as e:
        message_on_error = {
            "Error!": str(e)}  # dict
        message_on_error = str(message_on_error)
        message_on_error = message_on_error.replace("\'", "\"")
        return HttpResponse(message_on_error, content_type='application/json')

