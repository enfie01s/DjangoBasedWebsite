from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime, date

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    seotitle = models.CharField(max_length=50,unique=True)
    pub_date = models.DateTimeField()
    image = models.ImageField(upload_to='portfolio/%Y/%m/%d/',null=True,blank=True)
    body = models.TextField()
    #date = models.IntegerField(null=True,blank=True)
    #intro = models.CharField(max_length=200,null=True,blank=True)

    def __str__(self):
        return self.title

    def pub_date_pretty(self):
       return self.pub_date.strftime('%b %e %Y')

    def summary(self):
        return self.body[:100]

    def url(self):
        datestuff = self.pub_date.strftime('%Y/%m/%d')
        return '{0}/{1}'.format(datestuff,self.seotitle)

    class Meta:
        unique_together = ("pub_date", "seotitle")