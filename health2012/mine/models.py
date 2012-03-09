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

class URLtopic(models.Model):
    topic = models.CharField(max_length=50)
    shorttopic = models.CharField(max_length=50)
    url = models.CharField(max_length=100)


class Logo(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=100)
    attr = models.CharField(max_length=30)
    logopath = models.CharField(max_length=20)
