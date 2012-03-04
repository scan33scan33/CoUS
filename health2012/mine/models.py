from django.db import models

# Create your models here.
class Item(models.Model):
    topic = models.CharField(max_length=50)
    subtopic = models.CharField(max_length=50)
    qtopic = models.CharField(max_length=50)
    attr = models.CharField(max_length=50) #All attributes, comma separated

    #race = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    #education = models.CharField(max_length=30)
    #age = models.CharField(max_length=30)
    
    value = models.FloatField() 
