
from django.test import TestCase
from django.test import Client
from django.urls import reverse

csrf_client = Client(enforce_csrf_checks=True)
import requests
from Project.models import User_profile
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in

#
# class UserHistoryTest(TestCase):
#     client = Client()  # May be you have missed this line
#
#     def setUp(self):
#         self.user = User.objects.create_superuser(username='testuser13', password='pass@123', email='admin@admin.com')
#
#     def test_history(self):
#         self.client.login(username=self.user.username, password='pass@123')
#         # get_history function having login_required decorator
#         # response = self.client.post('/', {'user_id': self.user.id})
#         # self.assertEqual(response.status_code, 200)


class TestCalls(TestCase):

    # def test_call_view_denies_anonymous(self):
    #     response = self.client.get('/add', follow=True)
    #     self.assertRedirects(response, '/')
    #     # response = self.client.post('/url/to/view', follow=True)
    #     # self.assertRedirects(response, '/login/')

    def test_call_view_loads(self):
        self.client.login(username='andi', password='passpass')  # defined in fixture or with factory in setUp()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'conversation.html')

    # def test_call_view_fails_blank(self):
    #     self.client.login(username='testuser1', password='pass@123')
    #     response = self.client.post('/home', {}) # blank data dictionary
        # self.assertFormError(response, 'form', 'some_field', 'This field is required.')
        # etc. ...
    #
    # def test_call_view_fails_invalid(self):
    #     # as above, but with invalid rather than blank data in dictionary
    #
    # def test_call_view_fails_invalid(self):
    #     # same again, but with valid data, then
    #     self.assertRedirects(response, '/contact/1/calls/')