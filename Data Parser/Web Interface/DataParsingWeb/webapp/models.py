from django.db import models

class User(models.Model):

    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

class Settings(models.Model):

    settingkey = models.CharField(max_length=50, unique=True)
    settingvalue = models.CharField(max_length=255)
