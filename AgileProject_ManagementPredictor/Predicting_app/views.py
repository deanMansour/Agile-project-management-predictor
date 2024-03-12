#-------------------------
import io
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
#-------------------------------to upload and handle Excel/csv file---------------------------
#from .forms import UploadExcelForm, UploadCSVForm          #not used
from .models import Excel_File_Data, Excel_Row_Data
import pandas as pd    # for this : pip install pandas
import csv          # for csv files


# Create your views here.
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
        return render(request, 'Predicting_app/home_page.html', {'form': form, 'data':data_to_render })
    #--------------------------------------------------------------------------------
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
    #--------------------------------------------------------------------------------
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
    selected_project_ids = []
    selected_excel_projects = []
    @method_decorator(login_required)
    def get(self, request):
        #form = UploadExcelForm()
        form = []
        self.selected_excel_projects = []
        self.selected_project_ids = []

        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files
        user_object = request.user
        data_to_render = {
            'display': "Admin Main Page", 
            'all_projects': all_excel_projects, 
            'selected_excel_projects': self.selected_excel_projects,
            'selected_project_ids': self.selected_project_ids,  # Pass selected project IDs to the template
        }
      
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data':data_to_render, 'user':user_object, 'form': form})
    #--------------------------------------------------------------------------------
    def post(self, request):      
        
        def upload_csv():
            csv_file = request.FILES['file']                
            # Wrap the file content in a text stream
            with io.TextIOWrapper(csv_file, encoding='utf-8') as file:
                csv_data = csv.reader(file)
                all_data = []  # Create a list to hold the data from all rows
                field_names = next(csv_data)  # Assuming the first row contains field names

                # Iterate over the remaining rows
                for row in csv_data:
                    row_data = {}
                    for field_name, value in zip(field_names, row):
                        row_data[field_name] = value
                    all_data.append(row_data)  # Append the row data to the list
                
                # Create instances of Excel_Row_Data and save them to the database
                excel_rows_data_instances = []
                for data in all_data:
                    # excel_row_data_instance = Excel_Row_Data.objects.create(**data)
                    excel_row_data_instance = Excel_Row_Data.objects.create(json_data=data)
                    excel_rows_data_instances.append(excel_row_data_instance)

                # Create an instance of Excel_File_Data and associate it with the Excel_Row_Data instances
                excel_file_instance = Excel_File_Data.objects.create()
                # To pick the project name from the first row and name the project
                for field_name, value in zip(field_names, all_data[0].values()):
                    # Check if the field name contains "project name" (case insensitive)
                    if "project name" in field_name.lower():
                        # Set the project name to the corresponding value
                        excel_file_instance.project_name = value
                        excel_file_instance.save()
                        break  # Exit the loop after setting the project name
                excel_file_instance.excel_rows.add(*excel_rows_data_instances)
        #----------------------
        def upload_excel():
            excel_file = request.FILES['file']
            with excel_file.open(mode='rt') as file:
                df = pd.read_excel(excel_file, engine='openpyxl')  # Specify the engine manually

                # Create a list to hold the data from all rows
                all_data = []
                for index, row in df.iterrows():
                    # Create a dictionary to hold the data for the current row
                    row_data = {}
                    for field in df.columns:
                        row_data[field] = row[field]
                    # Append the row data to the list
                    all_data.append(row_data)

                # Create instances of Excel_Row_Data and save them to the database
                excel_rows_data_instances = []
                for data in all_data:
                    # excel_row_data_instance = Excel_Row_Data.objects.create(**data)
                    excel_row_data_instance = Excel_Row_Data.objects.create(json_data=data)
                    excel_rows_data_instances.append(excel_row_data_instance)

                # Create an instance of Excel_File_Data and associate it with the Excel_Row_Data instances
                excel_file_instance = Excel_File_Data.objects.create()
                # To pick the project name from the first row and name the project
                for field_name, value in zip(df.columns, all_data[0].values()):
                    # Check if the field name contains "project name" (case insensitive)
                    if "project name" in field_name.lower():
                        # Set the project name to the corresponding value
                        excel_file_instance.project_name = value
                        excel_file_instance.save()
                        break  # Exit the loop after setting the project name
                excel_file_instance.excel_rows.add(*excel_rows_data_instances)
        #----------------------
        def delete_project():
            # Loop through each selected project and delete it along with its associated rows
            for project in self.selected_excel_projects:
                # Delete associated rows first
                project.excel_rows.all().delete()
                # Remove the project from the list of selected projects
                self.selected_project_ids.remove(project.id)
                self.selected_excel_projects.remove(project)
                # Now delete the project itself
                project.delete()
        #----------------------
        def compute_predicts():
            return redirect('admin_measurement_pageview_path',self.selected_project_ids,self.selected_excel_projects)
        #--------------------------------------------------------------------------------
        form = []

        # Check if 'selected-project' is in the request POST data--->if yes, then there is already selected list of projects id
        if 'selected-projects' in request.POST:
            # Retrieve selected project IDs from the request POST data
            self.selected_project_ids = request.POST.getlist('selected-projects', [])

            # Retrieve selected excel projects from the database
            self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)
        
        #if clicked on unselect button
        if 'Unselect Projects' in request.POST:
            # Retrieve selected project IDs from the request POST data
            self.selected_project_ids = []
            self.selected_excel_projects = []    
        
        error_message = None
        # if clicked on "Select Projects" button
        if 'Select Projects' in request.POST:
            # Check if 'selected-project-ids' is in the request POST data--->if yes, then now some projects been selected
            if 'selected-project-ids' in request.POST:
                # Retrieve selected project IDs from the request POST data
                self.selected_project_ids = request.POST.getlist('selected-project-ids', [])

                # Retrieve selected excel projects from the database
                self.selected_excel_projects = Excel_File_Data.objects.filter(id__in=self.selected_project_ids)
            else:
                error_message = 1 # Add an error message
            
        # if clicked on "Upload Project Data" button
        if 'Upload Project Data' in request.POST: # if file uploaded-->check validation and save it to DB
            # Check the file type
            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                if uploaded_file.name.endswith('.csv'):
                    upload_csv()
                else:
                    upload_excel()
            else:
                # Handle error if no file chosen
                error_message = 2
            
        # if clicked on "Delete selected projects data" button
        #(its shown in template only if there is selected project)
        if 'Delete selected projects data' in request.POST:
            delete_project()

        
        # if clicked on "Get project Predict measurements according to selected projects data" button
        #(its shown in template only if there is selected project)
        if 'Get project Predict measurements according to selected projects data' in request.POST:
            compute_predicts()
        
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Admin Main Page",
            'all_projects': all_excel_projects,
            'selected_excel_projects': self.selected_excel_projects,
            'selected_project_ids': self.selected_project_ids,  # Pass selected project IDs to the template
            'error_message': error_message
        }        
        return render(request, 'Predicting_app/admin_OR_user_MainPage.html', {'data': data_to_render, 'user': user_object, 'form': form}) 

#================================================================================      
#--------------------------------------------------------------------------------
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
    @method_decorator(login_required)
    def get(self, request):
        # request.user--> returns the authenticated User class object
        user_object = request.user
        data_to_render = {'display': "Admin Measurement Page"}
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data':data_to_render, 'user':user_object})
    #--------------------------------------------------------------------------------
    def post(self, request):
        return None
#================================================================================
class user_measurement_page_view(View):
    @method_decorator(login_required)
    def get(self, request):
        data_to_render = {'display': "User Measurement Page"}
        return render(request, 'Predicting_app/admin_OR_user_measurementPage.html', {'data':data_to_render})
    #--------------------------------------------------------------------------------
    def post(self, request):
        return None