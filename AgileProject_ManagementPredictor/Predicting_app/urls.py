from django.urls import path
from . import views

urlpatterns = [
    #path('<sending parameter>', views.home, name='home')   <> used to send parameter
    path('homepage', views.home, name='home'),
]