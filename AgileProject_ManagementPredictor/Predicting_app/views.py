from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


# Create your views here.

def home(request):
    return render(request, 'Predicting_app/home_page.html')