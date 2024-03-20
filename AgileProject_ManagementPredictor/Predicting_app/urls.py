from django.urls import path
from . import views

urlpatterns = [
    # path('<sending parameter>', views.home, name='home')   <> used to send parameter
    path('', views.home_page_view.as_view(), name='home_page_view_path'),    
    #--------------------------------------------------------------------------------
    path('login/', views.loging_page_view.as_view(), name='loging_page_view_path'),
    #--------------------------------------------------------------------------------
    path('signup/', views.signup_page_view.as_view(), name='signup_page_view_path'),
    #--------------------------------------------------------------------------------
    path('logout/', views.logout_page_view, name='logout_page_view_path'), 
    #================================================================================
    #================================================================================
    path('admin_account/main_Page', views.admin_MainPage_view.as_view(), name='admin_MainPage_view_path'),
    #--------------------------------------------------------------------------------
    path('user_account/main_Page', views.user_MainPage_view.as_view(), name='user_MainPage_view_path'),
    #================================================================================
    #================================================================================
    path('admin_account/measurement_page', views.admin_measurement_page_view.as_view(), name='admin_measurement_pageview_path'),
    #--------------------------------------------------------------------------------
    path('user_account/measurement_page', views.user_measurement_page_view.as_view(), name='user_measurement_pageview_path'),
    

]