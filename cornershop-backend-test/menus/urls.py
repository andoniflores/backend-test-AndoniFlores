from django.urls import path

from menus import views

app_name = 'menus'

urlpatterns = [
    path('', views.index, name='index'),
    path('/create', views.create_view, name='create_view'),
    path('/detail/<int:id>', views.detail_view, name='detail_view'),
    path('/delete/<int:id>', views.delete_view, name='delete_view'),
    path('/update/<int:id>', views.update_view, name='update_view'),
    path('/login', views.login_view, name='login'),
    path('/logout', views.logout_view, name='logout'),
    path('/requests', views.request_list_view, name='requests'),
    path('/requests/<str:date>', views.request_details_view, name='request_details'),
    path('/send_reminder', views.send_reminder, name="send_reminder")
]