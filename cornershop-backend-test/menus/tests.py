from django.conf.urls import url
from django.test import TestCase, Client
from django.urls import reverse

from datetime import datetime

from rest_framework import status
from rest_framework.test import APIClient

from menus import views
from . models import Menu, MenuRequest
from .forms import MenuForm, MenuRequestForm
from .tasks import send_reminder_task
import uuid
from django.contrib.auth.models import User
import json

# Create your tests here.
class TestMenus(TestCase):

    def setUp(self):
        Menu.objects.create(
            menu_date='2021-09-05',
            menu_greeting_msg='Hi',
            menu_goodbye_msg= 'Goodbye',
            menu_option_1= 'chicken',
            menu_option_2= 'fish',
            menu_option_3= 'beef',
            menu_option_4= 'vegan'
        )
        MenuRequest.objects.create(
            menu=Menu.objects.first(),
            menu_request_employee_name='John',
            menu_option_chosen=Menu.objects.first().menu_option_1,
            menu_option_chosen_comment='no salt pls'
        )
        self.credentials = {
            'username': 'nora',
            'password': '12345'
        }
        self.user = User.objects.create_user(**self.credentials)
        self.url = 'http://127.0.0.1:8000/menu/' + str(uuid.uuid4())
        self.payload = '{"text": "%s"}' % self.url 

    def test_menu_form(self):
        date = str(datetime.now().date())
        form_data = {
            'menu_date': date,
            'menu_greeting_msg': 'Hi',
            'menu_goodbye_msg': 'Goodbye',
            'menu_option_1': 'chicken',
            'menu_option_2': 'fish',
            'menu_option_3': 'beef',
            'menu_option_4': 'vegan',
        }
        form = MenuForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_menu_form_invalid(self):
        date = str(datetime.now().date())
        # form_data without date
        form_data = {
            'menu_greeting_msg': 'Hi',
            'menu_goodbye_msg': 'Goodbye',
            'menu_option_1': 'chicken',
            'menu_option_2': 'fish',
            'menu_option_3': 'beef',
            'menu_option_4': 'vegan',
        }
        form = MenuForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_menu_request_form(self):
        menu = Menu.objects.get(menu_date="2021-09-05")
        form_data = {
            'menu': menu,
            'menu_request_employee_name': 'Juan',
            'menu_option_chosen': 'chicken',
            'menu_option_chosen_comment': 'juicy pls'
        }
        form = MenuRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_menu_request_form_invalid(self):
        # form without foreign key
        form_data = {
            'menu_request_employee_name': 'Juan',
            'menu_option_chosen': 'chicken',
            'menu_option_chosen_comment': 'juicy pls'
        }
        form = MenuRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
    

    def test_reminder_task(self):
        response = send_reminder_task(self.payload)
        self.assertEqual(response.text,'ok')

    #Integration Tests
    def test_index_view_not_authenticated(self):
        response = self.client.get(reverse('menus:index'))
        self.assertRedirects(response, reverse('menus:login'))

    def test_index_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        response = self.client.get(reverse('menus:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu_list.html')
    
    def test_create_view_not_authenticated(self):
        response = self.client.get(reverse('menus:create_view'))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_create_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        response = self.client.get(reverse('menus:create_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_menu.html')

    def test_detail_view_not_authenticated(self):
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:detail_view', kwargs={'id':menu.id}))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_detail_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:detail_view', kwargs={'id':menu.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail_menu.html')
    
    def test_delete_view_not_authenticated(self):
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:delete_view', kwargs={'id':menu.id}))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_delete_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:delete_view', kwargs={'id':menu.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'delete_menu.html')

        response = self.client.post(reverse('menus:delete_view', kwargs={'id':menu.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('menus:index'))

    def test_update_view_not_authenticated(self):
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:update_view', kwargs={'id':menu.id}))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_update_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        menu = Menu.objects.first()
        response = self.client.get(reverse('menus:update_view', kwargs={'id':menu.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_menu.html')
        data = {'menu_date': str(menu.menu_date), 'menu_greeting_msg': menu.menu_greeting_msg,
                'menu_goodbye_msg': menu.menu_goodbye_msg, 'menu_option_1': menu.menu_option_1, 'menu_option_2': menu.menu_option_2, 
                'menu_option_3': menu.menu_option_3, 'menu_option_4': menu.menu_option_4}
        response = self.client.post(reverse('menus:update_view', kwargs={'id':menu.id}), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('menus:index'))

    def test_choose_meal_view(self):
        uuid_string = str(uuid.uuid4())
        menu = Menu.objects.first()
        data = {
            'menu_id': menu.id,
            'employee_name': 'Andoni',
            'meal_list': menu.menu_option_1,
            'meal_comment': 'test comment'
        }
        response = self.client.post(reverse('choose_meal', kwargs={'request_id': uuid_string}), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'choose_meal_succesful.html')

        response = self.client.get(reverse('choose_meal', kwargs={'request_id': uuid_string}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'choose_meal.html')
    
    def test_request_list_view_not_authenticated(self):
        response = self.client.get(reverse('menus:requests'))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_request_list_authenticated(self):
        self.client.login(username='nora', password='12345')
        response = self.client.get(reverse('menus:requests'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_list.html')

    def test_request_details_view_not_authenticated(self):
        menu = Menu.objects.first()
        date = str(menu.menu_date)
        response = self.client.get(reverse('menus:request_details',kwargs={'date': menu.menu_date}))
        self.assertRedirects(response, reverse('menus:login'))
    
    def test_request_details_view_authenticated(self):
        self.client.login(username='nora', password='12345')
        menu = Menu.objects.first()
        date = str(menu.menu_date)
        response = self.client.get(reverse('menus:request_details', kwargs={'date': menu.menu_date}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'request_details.html')
    