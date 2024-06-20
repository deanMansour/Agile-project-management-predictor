from django.urls import path
from . import views

urlpatterns = [
    # path('<sending parameter>', views.home, name='home')   <> used to send parameter
    path('', views.home_page_view.as_view(), name='home_page_view_path'),   
    
    path('login/', views.loging_page_view.as_view(), name='loging_page_view_path'),
    
    path('signup/', views.signup_page_view.as_view(), name='signup_page_view_path'),
    
    path('logout/', views.logout_page_view, name='logout_page_view_path'), 
 
    
    path('Dashboard/', views.dashboard.as_view(), name='Dashboard_path'),   
    #================================================================================
    path('Dashboard/AdminEditor/', views.admin_MainPage_view.as_view(), name='admin_MainPage_view_path'),
    #================================================================================
    
    # Add URL pattern for the overview page with a project ID parameter
    path('Dashboard/overview/<int:project_id>/', views.overview_page, name='overview_page_view_path'),
    
    # Add URL pattern for the measurements page with a project ID parameter
    path('Dashboard/measurements/<int:project_id>/', views.measurements_page, name='measurements_page_view_path'),

]