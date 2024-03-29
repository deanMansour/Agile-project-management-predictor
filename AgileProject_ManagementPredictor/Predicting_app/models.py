from django.db import models
from django.contrib.auth.models import User
# from django.contrib.postgres.fields import JSONField #for this do in terminal---> pip install psycopg2

# Create your models here.

# class Profile_model(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     def __str__(self):
#         return f'{self.user.username}'
#=======================================================================================================
class Excel_Row_Data(models.Model):
    json_data = models.JSONField(null=True) # Allow null values for existing rows

    # summary = models.CharField(max_length=255)
    # issue_key = models.CharField(max_length=100)
    # issue_id = models.CharField(max_length=100)
    # parent_id = models.CharField(max_length=100)
    # issue_type = models.CharField(max_length=100)
    # status = models.CharField(max_length=100)
    # project_key = models.CharField(max_length=100)
    # project_name = models.CharField(max_length=255)
    # project_type = models.CharField(max_length=100)
    # project_description = models.TextField()
    # project_url = models.URLField()
    # priority = models.CharField(max_length=100)
    # resolution = models.CharField(max_length=100)
    # assignee = models.CharField(max_length=255)
    # reporter = models.CharField(max_length=255)
    # creator = models.CharField(max_length=255)
    # created = models.DateTimeField()
    # updated = models.DateTimeField()
    # last_viewed = models.DateTimeField()
    # resolved = models.DateTimeField()
    # affects_versions = models.CharField(max_length=255)
    # fix_versions = models.CharField(max_length=255)
    # original_estimate = models.DurationField()
    # remaining_estimate = models.DurationField()
    # time_spent = models.DurationField()
    # work_ratio = models.FloatField()
    # original_estimate_currency = models.CharField(max_length=10)
    # remaining_estimate_currency = models.CharField(max_length=10)
    # time_spent_currency = models.CharField(max_length=10)

    # def __str__(self):
    #     return ""
#=======================================================================================================
class Excel_File_Data(models.Model):
    excel_rows = models.ManyToManyField(Excel_Row_Data) # Many-to-Many relationship becuase we could make copy of the excel file
    project_name = models.CharField(max_length=255)   

    def aggregate_rows(self):
        all_rows = self.excel_rows.all()
        # Combine all rows into a single dictionary
        aggregated_data = {field.name: [] for field in Excel_Row_Data._meta.fields}
        for row in all_rows:
            for field in aggregated_data:
                aggregated_data[field].append(getattr(row, field))
        return aggregated_data