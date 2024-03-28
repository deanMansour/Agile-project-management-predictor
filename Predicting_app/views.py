#-------------------------
from urllib import request
from django import template
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
#-------------------------------to upload and handle Excel/csv file---------------------------
#from .forms import UploadExcelForm, UploadCSVForm          #not used
from .models import Excel_File_Data, Excel_Row_Data
import pandas as pd    # for this : pip install pandas
import csv          # for csv files
import io

# Create your views here.
#================================================================================  
#============================Support Classes=====================================
#================================= 1 ===============================================
class Selected_Projects:
    selected_project_ids = []
    selected_excel_projects = []
    selected_main_project = None
    
    def __init__(self, selected_project_ids=None):
        if selected_project_ids is None:
            selected_project_ids = []
        self.selected_project_ids = selected_project_ids
        self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)

    def get_list_of_projects(self):
        #get list of selected projects instances
        return self.selected_excel_projects
    
    
    def get_list_of_projects_id(self):
        return self.selected_project_ids
    
    def define_projects_by_ids_list(self, project_ids_list):
        self.selected_project_ids = project_ids_list
        self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)

    def unselect(self):
        self.selected_project_ids = []
        self.selected_excel_projects = []

    def is_selected(self):
        # Return True if there are selected projects
        return bool(self.selected_excel_projects)

    def delete_selected_projects(self):
        # Loop through each selected project and delete it along with its associated rows
        for project in self.selected_excel_projects:
            # Delete associated rows first
            project.excel_rows.all().delete()
            # Remove the project from the list of selected projects
            self.selected_project_ids.remove(project.id)
            self.selected_excel_projects.remove(project)
            # Now delete the project itself
            project.delete()

    def compute_DES(self):
        des_results_list = Compute_developer_expertise_score(self.selected_project_ids, self.selected_excel_projects)     
        return des_results_list
    
    def get_main_project(self,project):
        selected_main_project=Excel_File_Data.objects.filter(id__in=project)
        return selected_main_project

#================================= 2 ===============================================
class Upload_to_DB:    
    @staticmethod
    def csv_file(request):
        uploaded_file = request.FILES['file']                
        # Wrap the file content in a text stream
        with io.TextIOWrapper(uploaded_file, encoding='utf-8') as file:
            csv_data = csv.reader(file)
            all_data = []  # Create a list to hold the data from all rows
            field_names = next(csv_data)  # Assuming the first row contains field names

            # Iterate over the remaining rows
            for row in csv_data:
                row_data = {}
                for field_name, value in zip(field_names, row):
                    row_data[field_name] = value
                all_data.append(row_data)  # Append the row data to the list

            return Upload_to_DB.create_excel_file(field_names, all_data)
    #--------------------------------------------------------------------------------
    @staticmethod
    def excel_file(request):
        uploaded_file = request.FILES['file']
        with uploaded_file.open(mode='rt') as file:
            df = pd.read_excel(uploaded_file, engine='openpyxl')  # Specify the engine manually

            # Create a list to hold the data from all rows
            all_data = []
            for index, row in df.iterrows():
                # Create a dictionary to hold the data for the current row
                row_data = {}
                for field in df.columns:
                    row_data[field] = row[field]
                # Append the row data to the list
                all_data.append(row_data)
            
            field_names = df.columns
            
            return Upload_to_DB.create_excel_file(field_names, all_data)
    #--------------------------------------------------------------------------------
    @staticmethod
    def create_excel_file(field_names, all_data):
        # Create instances of Excel_Row_Data and save them to the database
        excel_rows_data_instances = []
        for data in all_data:
            # excel_row_data_instance = Excel_Row_Data.objects.create(**data)
            excel_row_data_instance = Excel_Row_Data.objects.create(json_data=data)
            excel_rows_data_instances.append(excel_row_data_instance)

        # Create an instance of Excel_File_Data and associate it with the Excel_Row_Data instances
        excel_file_DB_instance = Excel_File_Data.objects.create()
        # To pick the project name from the first row and name the project
        for field_name, value in zip(field_names, all_data[0].values()):
            # Check if the field name contains "project name" (case insensitive)
            if "project name" in field_name.lower():
                # Set the project name to the corresponding value
                excel_file_DB_instance.project_name = value
                excel_file_DB_instance.save()
                break  # Exit the loop after setting the project name
        excel_file_DB_instance.excel_rows.add(*excel_rows_data_instances)
        return excel_file_DB_instance
#================================= 3 ===============================================
class Compute_developer_expertise_score:
    attribute = None

#================================Home Page views=================================
#================================================================================
class home_page_view(View):
    def get(self, request):        
        data_to_render = {'display': "Home Page"}
        user_object = request.user
        return render(request, 'Predicting_app/home_page.html',{'data':data_to_render, 'user':user_object})
    #--------------------------------------------------------------------------------
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
#--------------------------------------------------------------------------------
class loging_page_view(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home_page_view_path')
        
        form = AuthenticationForm()
        data_to_render = {'display': "Log-In Page"}
        return render(request, 'Predicting_app/home_page.html', {'form': form, 'data': data_to_render})
    
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
                else: #########--------------------this is where i change view path 
                    return redirect('Dashboard')
            else:
                # Add an error message to the form
                form.add_error(None, 'Invalid username or password.')
        # If form is not valid or user authentication fails, render the login page again
        return render(request, 'Predicting_app/home_page.html', {'form': form})

#--------------------------------------------------------------------------------
class signup_page_view(View):
    def get(self, request):
        form = User_SignUp_Form()
        data_to_render = {'display': "Sign-up Page"}
        return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render})

    def post(self, request):
        form = User_SignUp_Form(request.POST)
        if form.is_valid():
            user_object = form.save()
            user_object.refresh_from_db()
            user_object.save()
            return redirect('home_page_view_path')
        else:
            # Add error to non-field errors
            form.add_error(None, 'Invalid username or password.')
            data_to_render = {'display': "Sign-up Page"}
            return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render})
#==========================Logged-In account Main Page views=====================
#================================================================================
class admin_MainPage_view(View):    
    selected_Projects_instance = Selected_Projects()
    excel_file_DB_instance = None
    
    @method_decorator(login_required)
    def get(self, request):
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files
        user_object = request.user
        data_to_render = {
            'display': "Admin Main Page", 
            'all_projects': all_excel_projects, 
            'selected_excel_projects': self.selected_Projects_instance.get_list_of_projects(),
            'selected_Projects_instance':self.selected_Projects_instance,        }      
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data':data_to_render, 'user':user_object})
    #--------------------------------------------------------------------------------
    def post(self, request):
        #if clicked on unselect button
        if 'Unselect Projects' in request.POST:
            self.selected_Projects_instance.unselect()
        
        error_message = None
        # if clicked on "Select Projects" button
        if 'Select Projects' in request.POST:
            # Check if 'selected-project-ids' is in the request POST data--->if yes, then now some projects been selected
            if 'selected-project-ids' in request.POST:
                # Retrieve selected project IDs from the request POST data
                self.selected_Projects_instance.define_projects_by_ids_list(request.POST.getlist('selected-project-ids', []))
            else:
                error_message = 1 # Add an error message
            
        # if clicked on "Upload Project Data" button
        if 'Upload Project Data' in request.POST: # if file uploaded-->check validation and save it to DB
            # Check the file type
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    self.excel_file_DB_instance = Upload_to_DB.csv_file(request)
                else:
                    self.excel_file_DB_instance = Upload_to_DB.excel_file(request)
            else:
                # Handle error if no file chosen
                error_message = 2
            
        # if clicked on "Delete selected projects data" button
        #(its shown in template only if there is selected project)
        if 'Delete selected projects data' in request.POST:
            self.selected_Projects_instance.delete_selected_projects()

        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Admin Main Page",
            'all_projects': all_excel_projects,
            'selected_excel_projects': self.selected_Projects_instance.get_list_of_projects(),
            'selected_Projects_instance':self.selected_Projects_instance,
            'error_message': error_message
        }
        # if clicked on "Get project Predict measurements according to selected projects data" button
        #(its shown in template only if there is selected project)
        if 'Get project Predict measurements according to selected projects data' in request.POST:
            return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data': data_to_render, 'user': user_object}) 
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data': data_to_render, 'user': user_object}) 

#================================================================================ 
class user_MainPage_view(View):
    @method_decorator(login_required)
    def get(self, request):
        # request.user--> returns the authenticated User class object    
        self.selected_excel_projects = []
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files
        user_object = request.user
        data_to_render = {
            'display': "User Main Page", 'all_projects': all_excel_projects, 
            'selected_excel_projects': self.selected_excel_projects
        }
        
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data':data_to_render, 'user':user_object})
    #--------------------------------------------------------------------------------
    def post(self, request):
        
        def compute_predicts():
            return redirect('user_measurement_pageview_path')
        #----------------------
        self.selected_excel_projects = []

        # if clicked on "Select Projects" button
        if 'Select Projects' in request.POST:
            self.selected_project_ids = request.POST.getlist('selected-projects')
            self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)# Retrieve selected excel projects from the database

        if 'Get project Predict measurements according to selected projects data' in request.POST:
            self.selected_project_ids = request.POST.getlist('selected-projects')
            self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)# Retrieve selected excel projects from the database
            compute_predicts()
        #--------------------------------------------------------------------------------        
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Admin Main Page", 'all_projects': all_excel_projects,
            'selected_excel_projects': self.selected_excel_projects
        }
        
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data': data_to_render, 'user': user_object}) 

#======================Logged-In account Measurement page views==================
#================================================================================
class admin_measurement_page_view(View):
    selected_Projects_instance = Selected_Projects()
    
    @method_decorator(login_required)
    def get(self, request):
        return None     #   will never be accessed--becuase template got activated from another class
    #--------------------------------------------------------------------------------
    def post(self, request):        
        self.selected_Projects_instance = request.POST('selected_Projects')

        # if clicked on any of compute buttons
        if 'compute_DES' in request.POST:
            des_results_list = self.selected_Projects_instance.compute_DES()

        pridict_compute_results_dict = {'des' : des_results_list}
        form = []
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Admin Measurement Page",
            'all_projects': all_excel_projects,
            'selected_excel_projects': self.selected_Projects_instance.get_list_of_projects(),
            'selected_Projects_instance':self.selected_Projects_instance,
            'result': pridict_compute_results_dict
        }        
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data': data_to_render, 'user': user_object, 'form': form})
#================================================================================
class user_measurement_page_view(View):
    @method_decorator(login_required)
    def get(self, request):
        data_to_render = {'display': "User Measurement Page"}
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data':data_to_render})
    #--------------------------------------------------------------------------------
    def post(self, request):
        return None


def dashboard(request):
        
        all_excel_projects = Excel_File_Data.objects.all() 
        user_object = request.user
        chosen_project_id = request.GET.get('project-select')
        selected_Projects_instance = Selected_Projects()
        # Define the selected projects based on the chosen project ID
        if chosen_project_id:
            selected_Projects_instance.define_projects_by_ids_list([chosen_project_id])
            try:
             # Retrieve the corresponding project
              chosen_project = all_excel_projects.get(pk=chosen_project_id)
              selected_main_project = chosen_project  # Assign the chosen project to selected_main_project
            except Excel_File_Data.DoesNotExist:
              chosen_project = None
              selected_main_project = None
        else:
           chosen_project = None
           selected_main_project = None
        
        data_to_render = {
        'display': "Dashboard Page", 
        'all_projects': all_excel_projects,
        'chosen_project': chosen_project,
        'selected_main_project': selected_main_project
        }
    
        return render(request, 'Predicting_app/Dashboard.html', {'data':data_to_render, 'user': user_object})
             
     


def overview(request):
    user_object = request.user
    all_excel_projects = Excel_File_Data.objects.all() 
    selected_Projects_instance = Selected_Projects()

    if selected_Projects_instance.selected_main_projectchosen_project_id:
        data_to_render = {
        'display': "overview Page", 
        'all_projects': all_excel_projects,
        'chosen_project': selected_Projects_instance.selected_main_project,
        }

    return render(request, 'Predicting_app/overview.html', {'data':data_to_render, 'user': user_object})

def measurements(request):
    return render(request, 'Predicting_app/measurements.html')
