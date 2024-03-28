from django.contrib import admin

# Register your models here.
from .models import Excel_File_Data, Excel_Row_Data

# Register your models here.
#to show and edit appearance of model class in database page


admin.site.register(Excel_File_Data)


admin.site.register(Excel_Row_Data)


