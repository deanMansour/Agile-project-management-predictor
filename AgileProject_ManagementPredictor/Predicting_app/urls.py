from django.urls import path
from . import views

urlpatterns = [
    # path('<sending parameter>', views.home, name='home')   <> used to send parameter
    path('', views.home_pageview.as_view(), name='home_pageview_path'),    
    #--------------------------------------------------------------------------------
    path('', views.register_pageview.as_view(), name='register_pageview_path'),   
    #--------------------------------------------------------------------------------
    path('', views.loging_pageview.as_view(), name='loging_pageview_path'),
    #================================================================================
    #================================================================================
    path('admin/', views.admin_MainPage_view.as_view(), name='admin_MainPage_view_path'),
    #--------------------------------------------------------------------------------
    path('user/', views.user_MainPage_view.as_view(), name='user_MainPage_view_path'),
    #================================================================================
    #================================================================================
    path('admin/admin_measurement_page', views.admin_measurement_pageview.as_view(), name='admin_measurement_pageview_path'),
    #--------------------------------------------------------------------------------
    path('user/user_measurement_page', views.user_measurement_pageview.as_view(), name='user_measurement_pageview_path'),
    

]