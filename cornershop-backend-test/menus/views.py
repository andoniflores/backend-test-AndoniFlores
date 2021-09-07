from django.shortcuts import get_object_or_404, render, HttpResponseRedirect, redirect
from .models import Menu, MenuRequest
from .forms import MenuForm
from datetime import datetime, date
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
import requests
from django.urls import reverse
from .tasks import send_reminder_task
import uuid

# Get list of menus by date
def index(request):
    if request.user.is_authenticated:
        menus = Menu.objects.all()
        context = {'menu_list': menus}
        return render(request, 'menu_list.html', context)
    else:
        return redirect('menus:login')

# Create a new menu
def create_view(request):
    if request.user.is_authenticated:
        context={}

        form = MenuForm(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('menus:index')
        
        context['form'] = form
        return render(request, "create_menu.html", context)
    else:
        return redirect('menus:login')

# See menu detail
def detail_view(request, id):
    if request.user.is_authenticated:
        context={}

        context["obj"] = Menu.objects.get(id=id)
        return render(request, "detail_menu.html", context)
    else:
        return redirect('menus:login')

# Deletes a menu
def delete_view(request, id):
    if request.user.is_authenticated:
        context={}

        obj = get_object_or_404(Menu, id=id)

        if request.method == "POST":
            obj.delete()
            return redirect("menus:index")

        context["obj"] = obj
        return render(request, "delete_menu.html", context)
    else:
        return redirect('menus:login')

# Updates a menu
def update_view(request, id):
    if request.user.is_authenticated:
        context={}

        obj = get_object_or_404(Menu, id=id)

        form = MenuForm(request.POST or None, instance = obj)

        if form.is_valid():
            form.save()
            return redirect("menus:index")

        context["form"] = form
        return render(request, "update_menu.html", context)
    else:
        return redirect('menus:login')

# Authenticate views: Login and logout 
def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('menus:index')
        else:
            return render(request, 'login_error.html')
    else:
        return render(request, "login.html", context)

def logout_view(request):
    logout(request)
    return redirect('menus:login')

# Form to choose a meal out of the 4 options in the menu
# If it is past 11:00 a.m. CLT, it won't let you choose a meal and it will display a message
def choose_meal_view(request, request_id):
    context = {}
    context['request_id'] = request_id
    fulldate = datetime.now()
    date = str(fulldate.date())
    context['date'] = date
    if request.method == 'POST':
        menu = Menu.objects.get(id = request.POST['menu_id'])
        menu_request = MenuRequest.objects.create(
            menu_id = menu.id,
            menu_request_employee_name = request.POST['employee_name'],
            menu_option_chosen = request.POST['meal_list'],
            menu_option_chosen_comment = request.POST['meal_comment']
        )
        context['menu_request'] = menu_request
        return render(request, "choose_meal_succesful.html", context)
    else:
        if fulldate.time().hour < 11:
            context['deadline_met'] = False
            try:
                menu = Menu.objects.get(menu_date = date)
            except:
                menu = None
            if not menu is None:
                context['menu'] = menu
                context['menu_exist'] = True
                return render(request, "choose_meal.html", context)
            else:
                context['menu_exist'] = False
                return render(request, "choose_meal.html", context)
        else:
            context['deadline_met'] = True
            context['time'] = fulldate.time()
            return render(request, "choose_meal.html", context)

# List of request group by date
def request_list_view(request):
    if request.user.is_authenticated:
        request_list = MenuRequest.objects.all()
        request_dict = {}
        for request in request_list:
            if not str(request.menu.menu_date) in request_dict:
                request_dict[str(request.menu.menu_date)] = 1
            else:
                request_dict[str(request.menu.menu_date)] += 1
        context = {'requests': request_dict}
        return render(request, 'request_list.html', context)
    else:
        return redirect('menus:login')

# See details of an specific menu requests
def request_details_view(request, date):
    context = {}
    if request.user.is_authenticated:
        try:
            menu_requests = MenuRequest.objects.filter(menu__menu_date__contains = date)
            context['date'] = str(menu_requests[0].menu.menu_date)
            context['menu_requests'] = menu_requests
            return render(request, 'request_details.html', context)
        except:
            return redirect('menus:requests')
    else:
        return redirect('menus:login')

# Creates the url for meal choosing, and pass it to a task that sends a slack message asynchronously
@csrf_exempt
def send_reminder(request):
    if request.method == 'POST':
        urluuid = str(uuid.uuid4())
        url = 'http://' + request.get_host() + '/menu/' + urluuid
        payload = '{"text": "%s"}' % url
        response = send_reminder_task.delay(payload)
        return response
