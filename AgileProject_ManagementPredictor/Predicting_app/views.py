from urllib import request
from django.views import View
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
#---------for USER log-in,logout,authentication, and saving in DB--------
#a django form to view fields of User and submit it.
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
#inside each class activation require log-in-->add "@method_decorator(login_required)"
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
#to manipulate saved User class objects in DB
from django.contrib.auth.models import User
#-------------------------------to import from forms.py---------------------------
from .forms import User_SignUp_Form

# Create your views here.
#================================Home Page views=================================
#================================================================================
class home_page_view(View):
    def get(self, request):        
        data_to_render = {'display': "Home Page"}
        user_object = request.user
        return render(request, 'Predicting_app/home_page.html',{'data':data_to_render, 'user':user_object})
    #----------------------
    def post(self, request):
        ## there is no button in home_page.html that submit to this class url path
        # data_to_render = {'display': "Home Page"}
        # return render(request, 'Predicting_app/home_page.html',{'data':data_to_render})
        return None
#--------------------------------------------------------------------------------
def logout_page_view(request):
    #logout(request)-->buit-in func to Remove the authenticated user's ID from the request and flush their session data.
    logout(request)
    return redirect('home_page_view_path')
#----------------------
class loging_page_view(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home_page_view_path')
        
        form = AuthenticationForm()
        data_to_render = {'display': "Log-In Page"}
        return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render })
    #----------------------
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('admin_MainPage_view_path')
        
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            print('authenticating user')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            #If the given credentials are valid, return a User object.
            user_object = authenticate(username=username, password=password)

            print('user info----------: ', user_object.get_username())
            if user_object is not None:
                login(request, user_object)
                if user_object.is_staff == True:
                    return redirect('admin_MainPage_view_path')
                else:
                    return redirect('user_MainPage_view_path')
            else:
                # Add an error message to the form
                form.add_error(None, 'Invalid username or password.')
        else:
            # Add an error message to the form
            form.add_error(None, 'Invalid username or password.')
#--------------------------------------------------------------------------------
class signup_page_view(View):
    def get(self, request):
        form = User_SignUp_Form()
        data_to_render = {'display': "Sign-up Page"}
        return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render})
    #----------------------
    def post(self, request):
        form = User_SignUp_Form(request.POST)
        if form.is_valid():
            #form.save()-->save User_SignUp_Form class instance and return the instance of its linked model class
            user_object = form.save()
            user_object.refresh_from_db()
            # save the new created model class instance that linked to User_SignUp_Form class
            user_object.save()
            return redirect('home_page_view_path')
        else:
            form = User_SignUp_Form()
            form.add_error(None, 'Invalid username or password.')
            data_to_render = {'display': "Sign-up Page"}
            return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render})

#==========================Logged-In account Main Page views=====================
#================================================================================
class admin_MainPage_view(View):
    @method_decorator(login_required)
    def get(self, request):
        # request.user--> returns the authenticated User class object
        user_object = request.user
        data_to_render = {'display': "Admin Main Page"}
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data':data_to_render, 'user':user_object})
    #----------------------
    def post(self, request):
        return None
    #----------------------
    def admin_view_data(self, request):
        return None
    #----------------------
    def admin_add_data(self, request):
        return None
    #----------------------
    def admin_delete_data(self, request):
        return None
    #----------------------
    def admin_storing_uploaded_file(self, request, file):
        #with open("", "wb+") as dest:              
        return None
#--------------------------------------------------------------------------------
class user_MainPage_view(View):
    @method_decorator(login_required)
    def get(self, request):
        # request.user--> returns the authenticated User class object
        user_object = request.user
        data_to_render = {'display': "User Main Page"}
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data':data_to_render, 'user':user_object})
    #----------------------
    def post(self, request):
        return None
    #----------------------
    def user_view_data(self, request):
        return None
#======================Logged-In account Measurement page views==================
#================================================================================
class admin_measurement_page_view(View):
    @method_decorator(login_required)
    def get(self, request):
        # request.user--> returns the authenticated User class object
        user_object = request.user
        data_to_render = {'display': "Admin Measurement Page"}
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data':data_to_render, 'user':user_object})
    #----------------------
    def post(self, request):
        return None
#--------------------------------------------------------------------------------
class user_measurement_page_view(View):
    @method_decorator(login_required)
    def get(self, request):
        data_to_render = {'display': "User Measurement Page"}
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data':data_to_render})
    #----------------------
    def post(self, request):
        return None