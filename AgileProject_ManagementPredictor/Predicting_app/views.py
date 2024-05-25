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
from django.contrib import messages #import messages
    

# Create your views here.
#================================================================================  
#============================Support Classes=====================================
#================================= 1 ===============================================
class Selected_Projects:
    # the attributes recommended to be private(to set it only through methods)
    def __init__(self, selected_project_ids=None, dashboard_project_id=None):
        self._selected_project_ids = []  # Private attribute
        self._selected_excel_projects = []  # Private attribute
        self._dashboard_project_id = None  # Private attribute
        self._dashboard_project = None  # Private attribute

        if selected_project_ids:
            self.set_projects_by_ids_list(selected_project_ids)

        if dashboard_project_id:
            self.set_dashboard_project_by_id(dashboard_project_id)
                
                #----selected projects list methods-----
    
    def set_projects_by_ids_list(self, project_ids_list):
        self._selected_project_ids = project_ids_list
        self._selected_excel_projects = Excel_File_Data.objects.filter(id__in=self._selected_project_ids)
    
    def get_selected_projects_list(self):
        return self._selected_excel_projects
    
    def get_selected_projects_ids_list(self):
        return self._selected_project_ids

    def unselect(self):
        self._selected_project_ids = []
        self._selected_excel_projects = []

    def is_selected(self):
        # Return True if there are selected projects
        return bool(self._selected_excel_projects)

    def delete_selected_projects(self):
       
        # Loop through each selected project and delete it along with its associated rows
        for project in self._selected_excel_projects:
            # Delete associated rows first
            project.excel_rows.all().delete()
            # Remove the project from the list of selected projects
            self._selected_project_ids.remove(str(project.id))
            self._selected_excel_projects = list(self._selected_excel_projects)  # Convert QuerySet to list
            self._selected_excel_projects.remove(project)
            # Now delete the project itself
            project.delete()


                #----Dashboard project methods-----
    
    def set_dashboard_project_by_id(self, project_id):
        self._dashboard_project_id = project_id
        self._dashboard_project = Excel_File_Data.objects.filter(id=self._dashboard_project_id).first()
    
    def get_dashboard_project(self):
        return self._dashboard_project

    def get_dashboard_project_id(self):
        return self._dashboard_project_id
    
    def unselect_dashboard_project(self):        
        self._dashboard_project_id = None
        self._dashboard_project = None

    def is_dashboard_selected(self):
        # Return True if there is dashboard project
        return bool(self._dashboard_project)

    def dashboard_compute_DES(self):
        excel_rows = self._dashboard_project.excel_rows.all()
        developers_name_list = [excel_row.json_data.get("Assignee", "").lower() for excel_row in excel_rows]
        des_results_list = {
            'priority_weighted_fixed_issues' : Compute_Developer_Expertise_Score.priority_weighted_fixed_issues(self._dashboard_project, excel_rows, developers_name_list),
            'versatility_and_breadth_index' : Compute_Developer_Expertise_Score.versatility_and_breadth_index(self._dashboard_project),
            'developer_average_bug_fixing_time' : Compute_Developer_Expertise_Score.developer_average_bug_fixing_time(self._dashboard_project, excel_rows, developers_name_list),
        }    
        return des_results_list
    
       ##### issues information for chart  #####
    def project_tasks_overview(self,status):
        excel_rows = self._dashboard_project.excel_rows.all()
        story_count=bug_count=task_count=subTask_count=0
        task_type_counts = {}
        for excel_row in excel_rows:
            if excel_row.json_data["Status"] == status:
                task_type = excel_row.json_data["Issue Type"]
                if task_type == "Story":
                    story_count += 1
                elif task_type == "Bug":
                    bug_count += 1
                elif task_type == "Task":
                    task_count += 1
                elif task_type == "Sub-task":
                    subTask_count += 1
        task_type_counts={"Task":task_count,"Sub-task":subTask_count,"Story":story_count,"Bug":bug_count}

        
        return task_type_counts

#================================= 2 ===============================================
class Compute_Developer_Expertise_Score:
    @staticmethod
    def priority_weighted_fixed_issues(dashboard_project, excel_rows, developers_name_list):
        priorities_list = [excel_row.json_data.get("Priority", "").lower() for excel_row in excel_rows]      
        same_priority_bugs_count_fixed_by_developer = {developer_name: {priority: 0 for priority in priorities_list} for developer_name in developers_name_list}
        same_priority_total_count = {priority: 0 for priority in priorities_list}        
        # Initialize dictionary to store the developer names as keys and and each priority compute result as value  
        priority_weighted_fixed_results_dict = {developer_name: {priority: 0 for priority in priorities_list} for developer_name in developers_name_list}

        # Iterate over all Excel rows to count bugs fixed by priority and developer
        for excel_row in excel_rows:
            issue_type = excel_row.json_data.get("Issue Type", "").lower()
            developer_name = excel_row.json_data.get("Assignee", "").lower()
            priority = excel_row.json_data.get("Priority", "").lower() 
            
            # Check if the issue is a bug 
            if issue_type == "Bug".lower():
                # Increment total bugs with same priority count
                if priority in priorities_list:
                    same_priority_total_count[priority] += 1
                
                # Increment priority count for the developer
                if developer_name in developers_name_list:
                    same_priority_bugs_count_fixed_by_developer[developer_name][priority] += 1

        # Calculate the weighted priority dict for each developer
        weight = 0
        for developer_name in developers_name_list:   
            for priority, count_of_bugs_with_same_priority_fixed_by_developer in same_priority_bugs_count_fixed_by_developer[developer_name].items():
                if same_priority_total_count[priority] > 0:

                    weight = count_of_bugs_with_same_priority_fixed_by_developer / same_priority_total_count[priority]
                    priority_weighted_fixed_results_dict[developer_name][priority] = weight
            
            else:
                priority_weighted_fixed_results_dict[developer_name][priority] = 0
        
        return priority_weighted_fixed_results_dict
    #--------------------------------------------------------------------------------
    @staticmethod
    def versatility_and_breadth_index(dashboard_project):
        return None
    #--------------------------------------------------------------------------------
    @staticmethod
    def developer_average_bug_fixing_time(dashboard_project, excel_rows, developers_name_list):
        total_time_spent_by_developer = {developer_name: 0 for developer_name in developers_name_list}
        count_of_bugs_fixed_by_developer = {developer_name: 0 for developer_name in developers_name_list}        
        developer_average_bug_fixing_time_results_dict = {developer_name: 0 for developer_name in developers_name_list}
        
        # Iterate over all Excel rows to count bugs fixed by each developer and count total time spent to fix bugs by each developer
        for excel_row in excel_rows:
            issue_type = excel_row.json_data.get("Issue Type", "").lower()
            developer_name = excel_row.json_data.get("Assignee", "").lower()
            time_spent_str = excel_row.json_data.get("Time Spent", "")
            time_spent = int(time_spent_str) if time_spent_str.isdigit() else 0
            
            # Check if the issue is a bug and Increment priority count
            if issue_type == "Bug".lower():
                # Increment priority count for the developer
                if developer_name in developers_name_list:
                    total_time_spent_by_developer[developer_name] += time_spent
                    count_of_bugs_fixed_by_developer[developer_name] += 1
            
        # Calculate the developer average bug fixing time
        for developer_name in developers_name_list:
            if count_of_bugs_fixed_by_developer[developer_name] > 0:
                developer_average_bug_fixing_time_results_dict[developer_name] = total_time_spent_by_developer[developer_name] / count_of_bugs_fixed_by_developer[developer_name]
        
        return developer_average_bug_fixing_time_results_dict
#================================= 3 ===============================================
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

            return Upload_to_DB.create_excel_file(request,field_names, all_data)
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
            
            return Upload_to_DB.create_excel_file(request,field_names, all_data)
    #--------------------------------------------------------------------------------
    @staticmethod
    def create_excel_file(request,field_names, all_data):
        project_name = None
        for field_name, value in zip(field_names, all_data[0].values()):
            if "project name" in field_name.lower():
                project_name = value.strip()
                break

        # If project name is found, check if it already exists
        if project_name:
            if Excel_File_Data.objects.filter(project_name__iexact=project_name).exists():
                messages.error(request, 'Project with the same name already exists, Choose another one.')
                return

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
                    return redirect('Dashboard_path')
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
        self.selected_Projects_instance = Selected_Projects()
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files
        user_object = request.user
        data_to_render = {
            'display': "Admin Main Page", 
            'all_projects': all_excel_projects, 
            'selected_excel_projects': self.selected_Projects_instance.get_selected_projects_list(),
            'selected_Projects_instance':self.selected_Projects_instance,        }      
        return render(request, 'Predicting_app/admin_MainPage.html', {'data':data_to_render, 'user':user_object})
    #--------------------------------------------------------------------------------
    @method_decorator(login_required)
    def post(self, request):
        #if clicked on unselect button
        if 'Unselect Projects' in request.POST:
            self.selected_Projects_instance.unselect()
        
        error_message = None
        # if clicked on "Select Projects" button
        if 'Select Projects' in request.POST:
            # Check if selected project ids is in the request POST data--->if yes, then now some projects been selected
            if 'selected-projects' in request.POST:
          
                # Retrieve selected project IDs from the request POST data
                self.selected_Projects_instance.set_projects_by_ids_list(request.POST.getlist('selected-projects', []))
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
            'selected_excel_projects': self.selected_Projects_instance.get_selected_projects_list(),
            'selected_Projects_instance':self.selected_Projects_instance,
            'error_message': error_message
        }
        # if clicked on "View Dashboard" button
        if 'View Dashboard' in request.POST:
            return redirect('Dashboard_path')
        return render(request, 'Predicting_app/admin_MainPage.html', {'data': data_to_render, 'user': user_object})

#===========================Logged-In account Dashboard==========================
#================================================================================
class dashboard(View):
    selected_Projects_instance = Selected_Projects()

    @method_decorator(login_required)
    def get(self, request):
        self.selected_Projects_instance = Selected_Projects()
        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Dashboard Page",
            'all_projects': all_excel_projects,
            'selected_Projects_instance':self.selected_Projects_instance,
            'dashboard_project': self.selected_Projects_instance.get_dashboard_project(),
        }
        return render(request, 'Predicting_app/Dashboard.html', {'data': data_to_render, 'user': user_object})

    #--------------------------------------------------------------------------------
    @method_decorator(login_required)
    def post(self, request):        
        # if clicked in "Select Project" button
        if 'Select_Project' in request.POST:            
            selected_project_id = request.POST.get('selected-project')
            if selected_project_id:
                self.selected_Projects_instance.set_dashboard_project_by_id(selected_project_id)
                results = {'DES' : self.selected_Projects_instance.dashboard_compute_DES()} # return dict of DES results{}
            else :
                self.selected_Projects_instance = Selected_Projects()

        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Dashboard Page",
            'all_projects': all_excel_projects,
            'selected_Projects_instance':self.selected_Projects_instance,
            'dashboard_project_id': self.selected_Projects_instance.get_dashboard_project_id(),
            'dashboard_project': self.selected_Projects_instance.get_dashboard_project(),
            'results' : results,
        }

        return render(request, 'Predicting_app/Dashboard.html', {'data': data_to_render, 'user': user_object})
#--------------------------------------------------------------------------------
def overview_page(request, project_id):
    selected_Projects_instance = Selected_Projects()
    selected_Projects_instance.set_dashboard_project_by_id(project_id)

    all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
    user_object = request.user 

    ####
    issue_count_open=selected_Projects_instance.project_tasks_overview('Open')   
    issue_count_close=selected_Projects_instance.project_tasks_overview('Closed')   
    issue_data = []
    for issue_type, open_count in issue_count_open.items():
        closed_count = issue_count_close.get(issue_type, 0)
        issue_data.append({"type": issue_type, "open": open_count, "closed": closed_count})
  
    ####
        
    data_to_render = {
        'display': "Overview Page",
        'all_projects': all_excel_projects,
        'selected_Projects_instance': selected_Projects_instance,
        'dashboard_project_id': selected_Projects_instance.get_dashboard_project_id(),
        'dashboard_project': selected_Projects_instance.get_dashboard_project(),
        'issue_data': issue_data,
    }
    return render(request, 'Predicting_app/overview.html', {'data': data_to_render, 'user': user_object})
#--------------------------------------------------------------------------------
def measurements_page(request, project_id):
    selected_Projects_instance = Selected_Projects()
    results = {}

    if project_id:
        selected_Projects_instance.set_dashboard_project_by_id(project_id)
        results = {'DES' : selected_Projects_instance.dashboard_compute_DES()} # return dict of DES results{}

        # # Debug print
        # print(result)

    all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
    user_object = request.user     
    data_to_render = {
        'display': "Measurements Page",
        'all_projects': all_excel_projects,
        'selected_Projects_instance': selected_Projects_instance,
        'dashboard_project_id': selected_Projects_instance.get_dashboard_project_id(),
        'dashboard_project': selected_Projects_instance.get_dashboard_project(),
        'results' : results,
    }
    
    return render(request, 'Predicting_app/measurements.html', {'data': data_to_render, 'user': user_object})