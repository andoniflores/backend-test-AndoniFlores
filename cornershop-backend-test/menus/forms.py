from django import forms
from django.contrib.postgres.forms import SimpleArrayField
import datetime
from .models import Menu, MenuRequest

class MenuForm(forms.ModelForm):

    class Meta:
        model = Menu

        fields = [
            "menu_date",
            "menu_greeting_msg",
            "menu_goodbye_msg",
            "menu_option_1",
            "menu_option_2",
            "menu_option_3",
            "menu_option_4",
            ]

class MenuRequestForm(forms.ModelForm):

    class Meta:
        model = MenuRequest

        fields = [
            "menu",
            "menu_request_employee_name",
            "menu_option_chosen",
            "menu_option_chosen_comment",
            ]
    # menu_date = forms.DateField(label='Date', initial=datetime.date.today, required=True)
    # menu_greeting_msg = forms.CharField(max_length=255)
    # menu_goodbye_msg = forms.CharField(max_length=255)
    # menu_option_1 = forms.CharField(max_length=255, required=True)
    # menu_option_2 = forms.CharField(max_length=255)
    # menu_option_3 = forms.CharField(max_length=255)
    # menu_option_4 = forms.CharField(max_length=255)