from django import forms
# to extend from django built-in User creation form class, and link it to django built-in User model class
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

#=======================================================================================================
""" To create class form that link to model.py,
so with User_SignUp_Form_object.save() will execute User_new_object.save()
class CustomUserCreationForm(forms.ModelForm): (to link to a class from model.py)   
"""
#   UserCreationForm is built in ModelForm for built-in User model class
class User_SignUp_Form(UserCreationForm):
    #no need for extra form fileds(User model class fields is enough)
    class Meta:
        # to link this class to built-In User class in models 
        model = User
        # field from User class that chosen to render it to template as form
        # (password2 -->for validation)
        fields = ('username', 'password1', 'password2')

#===============================EXCEL TYPE FILES(xls/csv)================================================
# class UploadExcelForm(forms.Form):
#     excel_file = forms.FileField(label='Select a xls file')

# class UploadCSVForm(forms.Form):
#     csv_file = forms.FileField(label='Select a CSV file')


