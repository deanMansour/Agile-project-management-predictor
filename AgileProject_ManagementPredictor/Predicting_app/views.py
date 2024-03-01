from urllib import request
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse


# Create your views here.

def home_pageview(request):
    return render(request, 'Predicting_app/home_page.html')
#--------------------------------------------------------------------------------
class register_pageview(request):
    def get(self, request):
        return None
    def post(self, request):
        return None
#--------------------------------------------------------------------------------
class loging_pageview(request):
    def get(self, request):
        return None
    def post(self, request):
        return None
#================================================================================
#================================================================================
class admin_MainPage_view(request):
    def get(self, request):
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html')
    #----------------------
    def post(self, request):
        return None
    #----------------------
    def admin_view_data():
        return None
    #----------------------
    def admin_add_data():
        return None
    #----------------------
    def admin_delete_data():
        return None
#--------------------------------------------------------------------------------
class user_MainPage_view(request):
    def get(self, request):
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html')
    #----------------------
    def post(self, request):
        return None
    #----------------------
    def user_view_data():
        return None
#================================================================================
#================================================================================
class admin_measurement_pageview(request):
    def get(self, request):
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html')
    #----------------------
    def post(self, request):
        return None
#--------------------------------------------------------------------------------
class user_measurement_pageview(request):
    def get(self, request):
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html') 
    #----------------------
    def post(self, request):
        return None