from django.db import models

# Create your models here.
class Menu(models.Model):
    menu_date = models.DateField(unique=True)
    menu_greeting_msg = models.CharField(max_length=255, blank = True, default="Here is today's menu")
    menu_goodbye_msg = models.CharField(max_length=255, blank = True, default="Have a nice day!")
    menu_option_1 = models.CharField(max_length=255, blank=True, default="")
    menu_option_2 = models.CharField(max_length=255, blank=True, default="")
    menu_option_3 = models.CharField(max_length=255, blank=True, default="")
    menu_option_4 = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f'id: {self.id} date: {str(self.menu_date)}'

class MenuRequest(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    menu_request_employee_name = models.CharField(max_length=255)
    menu_option_chosen = models.CharField(max_length=255)
    menu_option_chosen_comment = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f'id: {self.id} option: {self.menu_option_chosen} comment: {self.menu_option_chosen_comment}'

