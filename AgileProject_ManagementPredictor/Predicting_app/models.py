from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# class Profile_model(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     def __str__(self):
#         return f'{self.user.username}'
    # ----------------------------------------
class Uploaded_file_model(models.Model):
    # it always recommended to store file in hard drive not DB
    # upload_to = the path on my directory(it enough to enter the name of file)
    uploaded_file = models.FileField(upload_to="")
