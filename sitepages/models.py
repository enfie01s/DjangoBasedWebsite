from django.db import models

# Create your models here.
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

    def fullAddress(self):
        return self.street + ', ' + self.city + ', ' + self.county + ', ' + self.postcode + ', ' + self.country

    def qrVcard(self):
        vcard = "BEGIN:VCARD"
                + "\nVERSION:3.0"
                + "\nN:{lastName};{firstName}"
                + "\nFN:{fullName}"
                + "\nADR:;;{street};{city};{county};{postCode};{country}"
                + "\nTEL;WORK;VOICE:"
                + "\nTEL;CELL:{phone}"
                + "\nTEL;FAX:"
                + "\nEMAIL;WORK;INTERNET:{email}"
                + "\nURL:"
                + "\nEND:VCARD"

        return vcard.format(
            firstName=self.firstName,
            lastName=self.lastName,
            fullName=self.fullName(),
            street=self.street,
            city=self.city,
            county=self.county,
            postCode=self.postcode,
            country=self.country,
            phone=self.phone,
            email=self.email
        )

    class Meta:
        db_table = 'user_contact'
