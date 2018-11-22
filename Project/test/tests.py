import re

from django.contrib.auth import authenticate
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from Project.views import *
from Project.models import *
from django.contrib.messages import get_messages
from datetime import datetime

import requests
from Project.models import User_profile, Auction
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in


class UserHistoryTest(TestCase):
    # client = Client()  # May be you have missed this line
    client = Client(enforce_csrf_checks=False)


    def setUp(self):
        self.user = User.objects.create_superuser(username='andi2', password='passpass2', email='admin@admin.com')

    # creates a bid without being authorised
    def test_create_bid_without_auth(self):
        resp_get = self.client.get('/add_auction/')
        self.failUnlessEqual(resp_get.status_code,302)

    # creates a bid while being authorised
    def test_create_bid_with_auth(self):
        resp_login = self.client.login(username='andi2', password='passpass2')
        self.failUnlessEqual(resp_login,True)
        resp_get = self.client.get('/add_auction/',{
            'id_title':'title test',
            'id_details':'a',
            'id_bid':1,
            'id_bid_res':'2019-11-26T15:38'
        })
        self.failUnlessEqual(resp_get.status_code,200)

    def test_auction_data(self):

        resp_login = self.client.login(username="andi2", password="passpass2")
        self.failUnlessEqual(resp_login, True)


        # correct format input
        form_data = {'option': 'Yes', 'b_title': "Test Title", 'b_details': 'test details', 'b_bid': 1000,'b_res':"2019-11-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'New auction has been created!')
            self.assertRedirects(response, '/')


        # saying no to the agreement
        form_data = {'option': 'no', 'b_title': "Test Title", 'b_details': 'test details', 'b_bid': 1000,'b_res':"2019-11-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'You should agree our terms and conditions')
            self.assertRedirects(response, '/add_auction/')

        # saying nothing in the agreement
        form_data = {'option': '', 'b_title': "Test Title", 'b_details': 'test details', 'b_bid': 1000,'b_res':"2019-11-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'You should agree our terms and conditions')
            self.assertRedirects(response, '/add_auction/')


        # no title format input
        form_data = {'option': 'Yes', 'b_title': "", 'b_details': 'test details', 'b_bid': 1000,'b_res':"2019-11-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'Title is empty!')
            self.assertRedirects(response, '/add_auction/')


        # no minimum bid specified (in case of 0 it becomes automatically 0.1) format input
        form_data = {'option': 'Yes', 'b_title': "Test Title", 'b_details': 'test details', 'b_bid':"",'b_res':"2019-11-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'You didnt put a starting bid!')
            self.assertRedirects(response, '/add_auction/')


        # less then 72 resolution time format input
        form_data = {'option': 'Yes', 'b_title': "Test Title", 'b_details': 'test details', 'b_bid': 1000,'b_res':"2018-10-30T00:00" }
        response = self.client.post('/savebid/',form_data,follow=True)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'Resolution time is in less then 72 hours, please try again!')
            self.assertRedirects(response, '/add_auction/')


    def test_bid_data(self):
        resp_login = self.client.login(username="andi2", password="passpass2")
        self.failUnlessEqual(resp_login, True)

        # we create an auction to take the id so we can add the bids to that auction
        auction = Auction.objects.create(title='Test Title', details='test details', bid_res=(datetime.now()+timedelta(seconds=20)), timestamp= datetime.now(),
                                                  author=self.user, active=1, last_bid=1000, last_bider='andi2')

        # data to be sent to the bid
        # try good format bid
        form_data = {'bid': 10000, 'version': 1, 'auction_ID':auction.id}
        response = self.client.post('/makebid/', form_data, follow=True)
        print (response.status_code)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'Bid made!')
            self.assertRedirects(response, '/')


        # try bad bid value format bid
        form_data = {'bid': '', 'version': 1, 'auction_ID':auction.id}
        response = self.client.post('/makebid/', form_data, follow=True)
        print (response.status_code)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), '{"Error!": "You didnt put a bid number, please try again!"}')
            self.assertRedirects(response, '/')

        # try concurrency by modifying the version
        form_data = {'bid': 100000, 'version': 0.1, 'auction_ID':auction.id}
        response = self.client.post('/makebid/', form_data, follow=True)
        print (response.status_code)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'We are sorry but the auction was updated while you tried to bid, please try again!')
            self.assertRedirects(response, '/showDetails/1/')


        # no auction id
        form_data = {'bid': 100000, 'version': 1, 'auction_ID':''}
        response = self.client.post('/makebid/', form_data, follow=True)
        print (response.status_code)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), '{"Error!": "Auction ID is empty, please try again!"}')
            self.assertRedirects(response, '/')


        # make a bid with +0.1 value
        form_data = {'bid': 10000.01, 'version': 1, 'auction_ID':auction.id}
        response = self.client.post('/makebid/', form_data, follow=True)
        print (response.status_code)
        matches = [m.message for m in list(response.context['messages'])]
        if len(matches) == 1:
            msg = matches[0]
            print(msg)
            self.assertEqual(str(msg), 'Bid made!')
            self.assertRedirects(response, '/')
