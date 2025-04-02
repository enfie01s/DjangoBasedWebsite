from django.db import models

class Contact(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=254, null=True)
    phone = models.CharField(max_length=255, null=True)
    street = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    postcode = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.firstName

    def fullName(self):
        return self.firstName + ' ' + self.lastName

    class Meta:
        db_table = 'user_contact'
