#-------------------------
from datetime import timedelta
import datetime
from itertools import count
import json
from time import timezone
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
import random
import math
from collections import defaultdict
from django.http import JsonResponse
    


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
    
    #### issues information for chart  #####
    def project_tasks_overview(self,status):
        excel_rows = self._dashboard_project.excel_rows.all()
        task_type_counts = {}

        for excel_row in excel_rows:
            if excel_row.json_data["Status"] == status:
                task_type = excel_row.json_data["Issue Type"]
                if task_type in task_type_counts:
                  task_type_counts[task_type] += 1
                else:
                   task_type_counts[task_type] = 1
        
        return task_type_counts

#================================= 2 ===============================================
class Compute_Developer_Expertise_Score:

    def __init__(self, weights=None):
        self._measurements={}
        self._DES_scores_dict={}
        self.bugs_per_component_dict={}
        self.issue_resolution_time_results_dict={}
        self.velocity_by_priority_dict={}

        if weights:
            self.alpha_dict= weights
        else: self.alpha_dict=[1/3,1/3,1/3]
         
        #initializing dictionaries
        self.measurements_dict()
        self.compute_DES()
        self.bugs_per_component()
        self.issue_resolution_time()
        self.velocity_by_priority()

        

    
    def priority_weighted_fixed_issues(self ):
        priorities_list =self.all_priority_names()
        developers_name_list=self.all_developers_names()
        status_list = self.all_status_names()
        
       #** right now the weight is constant, after we need the user to input weight for each priority 
        weight_for_each_priorty={'blocker': 0.4, 'critical': 0.25, 'high': 0.15, 'medium ': 0.1, 'medium': 0.1, 'low': 0.05, 'not prioritized': 0.05}

        same_priority_bugs_count_fixed_by_developer = {developer_name: {priority: 0 for priority in priorities_list} for developer_name in developers_name_list}
        same_priority_total_count = {priority: 0 for priority in priorities_list}        
        # Initialize dictionary to store the developer names as keys and and each priority compute result as value  
        priority_weighted_fixed_results_dict = {developer_name:0 for developer_name in developers_name_list}
        # Iterate over all Excel rows to count bugs fixed by priority and developer
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
           excel_rows = project.excel_rows.all()
           for row in excel_rows:
            issue_type = row.json_data.get("Issue Type", "").lower()
            developer_name = row.json_data.get("Assignee", "").lower()
            priority = row.json_data.get("Priority", "").lower() 
            issue_status = row.json_data.get("Status", "").lower() 
            
            # Check if the issue is a bug 
            if issue_type == "Bug".lower() and (issue_status=="closed" or issue_status=="resolved"):
                # Increment total bugs with same priority count
                if priority in priorities_list:
                    same_priority_total_count[priority] += 1
                # Increment priority count for the developer
                if developer_name in developers_name_list:
                    same_priority_bugs_count_fixed_by_developer[developer_name][priority] += 1

        # Calculate the weighted priority dict for each developer
        for developer_name in developers_name_list:
            for priority in priorities_list:
                if priority !='priority':
                   weight = weight_for_each_priorty[priority]
                   # Calculate the priority weighted fixed issues count for each developer
                   if developer_name in same_priority_bugs_count_fixed_by_developer:
                       fixed_bugs_by_priority=same_priority_total_count[priority]
                       fixed_bugs_by_priority_by_dev=same_priority_bugs_count_fixed_by_developer[developer_name][priority]
                       priority_weighted_fixed_results_dict[developer_name] += ((fixed_bugs_by_priority_by_dev/fixed_bugs_by_priority)*weight)
        
        for developer_name in priority_weighted_fixed_results_dict:
            priority_weighted_fixed_results_dict[developer_name] = round(priority_weighted_fixed_results_dict[developer_name],2)
        return priority_weighted_fixed_results_dict
    #--------------------------------------------------------------------------------
    
    def versatility_and_breadth_index(self):
       # Fetch all developer names and fixed issues count by developer
       all_developers_names = self.all_developers_names()
       fixed_issues_count_by_developer = self.bugs_fixed_by_developer()

       # Calculate number of bugs per product type
       product_bug_counts = defaultdict(int)
       all_projects = Excel_File_Data.objects.all()
       for project in all_projects:
           excel_rows = project.excel_rows.all()
           for row in excel_rows:
              issue_type = row.json_data.get("Issue Type", "").lower()
              product_name = row.json_data.get("Component_test", "").lower()
              status=row.json_data.get("Status", "").lower()
              if issue_type == "bug"  and (status == "closed" or status == "resolved"):
                product_bug_counts[product_name] += 1
       # Calculate versatility index
       versatility_index = {developer_name:0 for developer_name in all_developers_names}
       total_products = len(product_bug_counts)
       for developer, product_counts in fixed_issues_count_by_developer.items():
            vd = 0.0
            for product, bugs_resolved in product_counts.items():
               total_bugs_product = product_bug_counts.get(product, 1)  # Avoid division by zero
            
               if total_bugs_product > 0:
                   p_d_j = bugs_resolved / total_bugs_product
                   if p_d_j > 0:
                       vd -= p_d_j * math.log(p_d_j)
        
            versatility_index[developer] = vd
       
       for developer_name in versatility_index:
            versatility_index[developer_name] = round(versatility_index[developer_name],2)

       return versatility_index
    
    #function that help find all the developers 
    def all_developers_names(self):
        developers_names = set()
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
           excel_rows = project.excel_rows.all()
           for row in excel_rows:
              developer_name = row.json_data.get("Assignee", "").lower()
              if developer_name:
                  developers_names.add(developer_name)
        return list(developers_names)
        
    def all_priority_names(self):
        priority_names = set()
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
           excel_rows = project.excel_rows.all()
           for row in excel_rows:
              priority_name = row.json_data.get("Priority", "").lower()
              if priority_name:
                  priority_names.add(priority_name)
        return list(priority_names)
    
   
    def all_status_names(self):
        status_names = set()
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
           excel_rows = project.excel_rows.all()
           for row in excel_rows:
              status_name = row.json_data.get("Status", "").lower()
              if status_name:
                  status_names.add(status_name)
        return list(status_names)
        
    #function that find all the types of bugs
    def all_products_name(self):
        products_names = set()
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
               product_name = row.json_data.get("Component_test", "").lower()
               if product_name:
                  products_names.add(product_name)
        return list(products_names)

    # function that find the number of bugs fixed by a developer in each product
    def bugs_fixed_by_developer(self):
        developer_bug_counts = defaultdict(lambda: defaultdict(int))
        all_developers = set(self.all_developers_names())
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
                developer_name = row.json_data.get("Assignee", "").lower()
                product_name = row.json_data.get("Component_test", "").lower()
                issue_type = row.json_data.get("Issue Type", "").lower()
                status = row.json_data.get("Status", "").lower()
            
                if developer_name in all_developers and issue_type == "bug" and (status == "closed" or status == "resolved"):
                   developer_bug_counts[developer_name][product_name] += 1

        return developer_bug_counts
    #--------------------------------------------------------------------------------
    
    def developer_average_bug_fixing_time(self):
        developers_name_list=self.all_developers_names()
        total_time_spent_by_developer = {developer_name: 0 for developer_name in developers_name_list}
        count_of_bugs_fixed_by_developer = {developer_name: 0 for developer_name in developers_name_list}        
        developer_average_bug_fixing_time_results_dict = {developer_name: 0 for developer_name in developers_name_list}
        
        # Iterate over all Excel rows to count bugs fixed by each developer and count total time spent to fix bugs by each developer
        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
                issue_type = row.json_data.get("Issue Type", "").lower()
                developer_name = row.json_data.get("Assignee", "").lower()
                time_spent_str = row.json_data.get("Σ Time Spent", "")  # Replace with your actual key
                time_spent = float(time_spent_str) if time_spent_str.replace('.', '', 1).isdigit() else 0.0
                issue_status = row.json_data.get("Status", "").lower()
                # Check if the issue is a bug and Increment priority count
                if issue_type == "Bug".lower() and (issue_status=="closed" or issue_status=="resolved"):
                   # Increment priority count for the developer
                   if developer_name in developers_name_list:
                       total_time_spent_by_developer[developer_name] += time_spent
                       count_of_bugs_fixed_by_developer[developer_name] += 1
            
        # Calculate the developer average bug fixing time
        for developer_name in developers_name_list:
            if count_of_bugs_fixed_by_developer[developer_name] > 0:
                developer_average_bug_fixing_time_results_dict[developer_name] = total_time_spent_by_developer[developer_name] / count_of_bugs_fixed_by_developer[developer_name]
       
        for developer_name in developer_average_bug_fixing_time_results_dict:
            developer_average_bug_fixing_time_results_dict[developer_name] = round(developer_average_bug_fixing_time_results_dict[developer_name],2)        
            return developer_average_bug_fixing_time_results_dict
    
    #--------------------------------------------------------------------------------
     ## Function to compute DES and return list of developers by DES score order
     ##right now i need to figure out how to choose alpha var based on the academic paper 
    def compute_DES(self):
       DES_scores = {}
    
       all_developers_names=self.all_developers_names()
       average_fix_time=self.developer_average_bug_fixing_time()
       versatility_index=self.versatility_and_breadth_index()
       priority_index=self.priority_weighted_fixed_issues()
       for developer in all_developers_names:
            mu_d =priority_index.get(developer, 0.0)
            vd = versatility_index.get(developer, 0.0)
            td = average_fix_time.get(developer, 0.0)
            Sd = self.alpha_dict[0] * mu_d + self.alpha_dict[1] * vd + self.alpha_dict[2] * td
            
            DES_scores[developer] = Sd

       # Rank developers based on DES score
       ranked_developers = sorted(DES_scores.items(), key=lambda x: x[1], reverse=True)
       
       ranked_developers = [(key, round(value, 2)) for key, value in ranked_developers]

       self._DES_scores_dict=ranked_developers
    
#---------------------- SETTERS/GETTERS---------------------------#
       
    def measurements_dict(self):
        priority=self.priority_weighted_fixed_issues()
        versatility=self.versatility_and_breadth_index()
        fix_time=self.developer_average_bug_fixing_time()
        measurements= {
            'priority_weighted_fixed_issues' :priority,
            'versatility_and_breadth_index' : versatility,
            'developer_average_bug_fixing_time' : fix_time}
        
        self._measurements=measurements

       # print('**************',measurements)

    def get_DES_scores_dict(self):
        return self._DES_scores_dict

    def set_DES_scores_dict(self, DES_scores_dict):
        self._DES_scores_dict = DES_scores_dict

    def get_measurements(self):
        return self._measurements

    def set_measurements(self, measurements):
        self._measurements = measurements

    def set_weights(self, weights):
        self.alpha_dict= weights
        self.compute_DES()
    
    def get_bugs_per_components(self):
        return self.bugs_per_component_dict
    
    def get_resolution_time(self):
        return self.issue_resolution_time_results_dict
    
    def get_velocity_by_priority(self):
        return self.velocity_by_priority_dict

    #================== more measurements ==============#
    def bugs_per_component(self):
        component_bug_counts = {}
        component_total_counts = defaultdict(lambda: defaultdict(int))

        all_projects = Excel_File_Data.objects.all()
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
                component_name = row.json_data.get("Component/s", "").lower()
                issue_type = row.json_data.get("Issue Type", "").lower()
                priority=row.json_data.get("Priority", "").lower()
                if component_name and issue_type == "bug":
                    component_total_counts[component_name][priority] += 1

        component_total_counts_regular = {component: dict(priorities) for component, priorities in component_total_counts.items()}
        self.bugs_per_component_dict = component_total_counts_regular
        
    

    ####


    def issue_resolution_time(self):
        all_projects = Excel_File_Data.objects.all()
        issue_resolution_time_results_dict = {}
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
                 issue_type = row.json_data.get("Issue Type", "").lower()
                 issue_status = row.json_data.get("Status", "").lower()
                 resolved_date_str = row.json_data.get("Resolved", "")
                 created_date_str = row.json_data.get("Created", "")
                 original_estimate_str = row.json_data.get("Original Estimate", "")
                 issue_key=row.json_data.get("Issue key", "")
                 priority=row.json_data.get("Priority", "")

                 if issue_status == "resolved" or issue_status=='completed':
                     if resolved_date_str and created_date_str and original_estimate_str:  # Check if dates are not empty
                        try:
                           resolved_date = datetime.datetime.strptime(resolved_date_str, '%d/%m/%Y %H:%M')
                           created_date = datetime.datetime.strptime(created_date_str, '%d/%m/%Y %H:%M')
                           time_taken = resolved_date - created_date
                           time_taken_hours = round(time_taken.total_seconds() / 3600, 2)
                           # Convert original estimate from seconds to hours
                           original_estimate_hours = round(float(original_estimate_str) / 3600, 2)
                           resolution =round(original_estimate_hours - time_taken_hours, 2)

                           issue_resolution_time_results_dict[issue_key] = {'priority':priority,'created':created_date,'resolved':resolved_date,'issue_resolution_time':resolution,'estimated_time':original_estimate_hours}
                        except ValueError as e:
                           print(f"Error parsing dates for key {issue_key}: {e}")
        print('********** length: ',len(issue_resolution_time_results_dict))
        self.issue_resolution_time_results_dict = issue_resolution_time_results_dict

    ####

    def get_period_start(self,date, start_date):
       delta = date - start_date
       period_start = start_date + datetime.timedelta(weeks=(delta.days // 28) * 4)
       return period_start
    
    def collect_data_from_projects(self):
        data = []
        all_projects=Excel_File_Data.objects.all()
        for project in all_projects:
            excel_rows = project.excel_rows.all()
            for row in excel_rows:
                issue_type = row.json_data.get("Issue Type", "").lower()
                issue_status = row.json_data.get("Status", "").lower()
                resolved_date_str = row.json_data.get("Resolved", "")
                created_date_str = row.json_data.get("Created", "")
                original_estimate_str = row.json_data.get("Original Estimate", "")
                issue_key = row.json_data.get("Issue key", "")
                priority = row.json_data.get("Priority", "")
                project_name=row.json_data.get("Project name", "")
                if  issue_status == "resolved" or issue_status == "closed":
                   if resolved_date_str and created_date_str and original_estimate_str:
                      try:
                        resolved_date = datetime.datetime.strptime(resolved_date_str, '%d/%m/%Y %H:%M')
                        created_date = datetime.datetime.strptime(created_date_str, '%d/%m/%Y %H:%M')
                        time_taken = resolved_date - created_date
                        time_taken_hours = round(time_taken.total_seconds() / 3600, 2)
                        original_estimate_hours = round(float(original_estimate_str) / 3600, 2)
                        resolution = round(original_estimate_hours - time_taken_hours, 2)

                        data.append({
                            'Project': project_name,
                            'Issue Key': issue_key,
                            'Resolved': resolved_date,
                            'Priority': priority
                        })
                      except ValueError as e:
                        print(f"Error parsing dates for key {issue_key}: {e}")

        return data

    
    def velocity_by_priority(self):
            
            data = self.collect_data_from_projects()
            # Create DataFrame from data
            df = pd.DataFrame(data)

            # Convert Resolved date to datetime format
            df['Resolved'] = pd.to_datetime(df['Resolved'])

            # Calculate the start date of the first period
            start_date = df['Resolved'].min()

            # Add Period Start column
            df['Start'] = df['Resolved'].apply(lambda x: self.get_period_start(x, start_date))

            # Add Period End column
            df['End'] = df['Start'] + pd.Timedelta(weeks=4)

            # Group by Project, Period Start, Period End, and Priority
            grouped_tasks = df.groupby(['Project', 'Start', 'End', 'Priority']).size().reset_index(name='Completed')

            # Calculate total completed tasks per period per project
            velocity_by_priority = grouped_tasks.groupby(['Project', 'Start', 'End'])['Completed'].sum().reset_index(name='Total_Completed')

            # Merge results
            result = pd.merge(grouped_tasks, velocity_by_priority, on=['Project', 'Start', 'End'])
            result['Velocity'] = result['Completed'] / result['Total_Completed']
            
            # Add Period Number column
            result['Period_Number'] = result.groupby('Project').cumcount() + 1
            result_dict = result.to_dict(orient='records')
            # Store the result in a dictionary
            self.velocity_by_priority_dict = result_dict


        

        
    

        



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
            
                random_values = ["Logic Error", "Runtime Error", "Syntax Error", "Performance Issue", "Security Bug", "UI Bug"]
                row_data['Component_test'] = random.choice(random_values)
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

            # Generate random values for the new column Component_test 
            # *** DO NOT FORGET TO DELETE WHEN HANOH GIVES US UPDATED DATA***
            random_values = ["Logic Error", "Runtime Error", "Syntax Error", "Performance Issue", "Security Bug", "UI Bug"]
            df['Component_test'] = [random.choice(random_values) for _ in range(len(df))]


            return Upload_to_DB.create_excel_file(request,field_names, all_data)
    #--------------------------------------------------------------------------------
    @staticmethod
    def create_excel_file(request,field_names, all_data):
        project_name = None
        for field_name, value in zip(field_names, all_data[0].values()):
            if "project name" in field_name.lower():
                project_name = value.strip()
                break
            elif "issue key" in field_name.lower():
                   project_name = value.strip()
                   project_name = project_name.split('-')[0]
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
                excel_file_DB_instance.project_name = project_name
                excel_file_DB_instance.save()
                break  # Exit the loop after setting the project name
        excel_file_DB_instance.excel_rows.add(*excel_rows_data_instances)
        if excel_file_DB_instance.project_name:
            messages.success(request, 'Project '+ excel_file_DB_instance.project_name +' uploaded successfully')
        else:
            excel_file_DB_instance.project_name=project_name
            excel_file_DB_instance.save()
        return excel_file_DB_instance

    
    
    
#--------------------------global variables

DES_scores=Compute_Developer_Expertise_Score()
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
            'bugs_per_components':DES_scores.get_bugs_per_components(), 
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
            else :
                self.selected_Projects_instance = Selected_Projects()
                
        
        results=DES_scores.get_measurements()
        des_scores=DES_scores.get_DES_scores_dict()

        issue_count_open=self.selected_Projects_instance.project_tasks_overview('Open')   
        issue_count_close=self.selected_Projects_instance.project_tasks_overview('Closed')   
        issue_data = []
        for issue_type, open_count in issue_count_open.items():
           closed_count = issue_count_close.get(issue_type, 0)
           issue_data.append({"type": issue_type, "open": open_count, "closed": closed_count})
        
        if request.method == "POST":
           mu_d = float(request.POST.get('number1-1', 0))
           v_d = float(request.POST.get('number1-2', 0))
           t_d = float(request.POST.get('number1-3', 0))
        list=[mu_d,v_d,t_d]
        #print(list)
        bugs_per_components=DES_scores.get_bugs_per_components()

        all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
        user_object = request.user        
        data_to_render = {
            'display': "Dashboard Page",
            'all_projects': all_excel_projects,
            'selected_Projects_instance':self.selected_Projects_instance,
            'dashboard_project_id': self.selected_Projects_instance.get_dashboard_project_id(),
            'dashboard_project': self.selected_Projects_instance.get_dashboard_project(),
            'results' : results,
            'issue_data' : issue_data,
            'des_scores' : des_scores,
            'weights': list,
            'bugs_per_components': bugs_per_components,
            'velocity_by_priority':DES_scores.get_velocity_by_priority(),
            'issue_resolution_data':DES_scores.get_resolution_time(),
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
    result=DES_scores.get_measurements()
    des_scores = DES_scores.get_DES_scores_dict()

    bugs_per_components=DES_scores.get_bugs_per_components()
    scatter_data = []
    for component, priorities in bugs_per_components.items():
        for priority, count in priorities.items():
            scatter_data.append({'name': component, 'x': priority, 'y': count})
    


    dev_data = {}
    for developer in result['developer_average_bug_fixing_time']:
     dev_data[developer] = {
        'priority': result['priority_weighted_fixed_issues'].get(developer, 0),
        'fix_time': result['developer_average_bug_fixing_time'][developer],
    }


    data_to_render = {
        'display': "Overview Page",
        'all_projects': all_excel_projects,
        'selected_Projects_instance': selected_Projects_instance,
        'dashboard_project_id': selected_Projects_instance.get_dashboard_project_id(),
        'dashboard_project': selected_Projects_instance.get_dashboard_project(),
        'issue_data': issue_data,
        'results': result,
        'des_scores':des_scores,
        'bugs_per_components':bugs_per_components,
        'velocity_by_priority':DES_scores.get_velocity_by_priority(),
        'issue_resolution_data':DES_scores.get_resolution_time(),

        
    }
    return render(request, 'Predicting_app/overview.html', {'data': data_to_render, 'user': user_object})
#--------------------------------------------------------------------------------
def measurements_page(request, project_id):
    selected_Projects_instance = Selected_Projects()
    results = {}
    mu_d=v_d=t_d=1/3

    if request.method == 'POST':
        try:
            data_received = json.loads(request.body)
            mu_d = float(data_received.get('mu_d', 0))
            v_d = float(data_received.get('v_d', 0))
            t_d = float(data_received.get('t_d', 0))

            total = mu_d + v_d + t_d

            if total == 1:
                weights = [mu_d, v_d, t_d]
                DES_scores.set_weights(weights)
                return JsonResponse({'success': True, 'weights': weights})
            else:
                return JsonResponse({'success': False, 'message': 'Weights do not sum to 1'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    
    if project_id:
        selected_Projects_instance.set_dashboard_project_by_id(project_id)

        # # Debug print
        # print(result)

    results=DES_scores.get_measurements()
    bugs_per_components=DES_scores.get_bugs_per_components()
    issue_resolution_data=DES_scores.get_resolution_time()
    des_scores=DES_scores.get_DES_scores_dict()
    velocity_by_priority=DES_scores.get_velocity_by_priority()
    all_excel_projects = Excel_File_Data.objects.all()  # Retrieve all projects excel files        
    user_object = request.user    

    data_to_render = {
        'display': "Measurements Page",
        'all_projects': all_excel_projects,
        'selected_Projects_instance': selected_Projects_instance,
        'dashboard_project_id': selected_Projects_instance.get_dashboard_project_id(),
        'dashboard_project': selected_Projects_instance.get_dashboard_project(),
        'results' : results,
        'des_scores':des_scores,
        'bugs_per_components':bugs_per_components,
        'issue_resolution_data':issue_resolution_data,
        'velocity_by_priority':velocity_by_priority,
    }
    
    return render(request, 'Predicting_app/measurements.html', {'data': data_to_render, 'user': user_object})





