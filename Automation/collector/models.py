from django.db import models

# Create your models here.
class IDCard(models.Model):
    name = models.CharField(max_length=250)
    mat_number = models.CharField(max_length=11)
    department = models.CharField(max_length= 50)
    gender = models.CharField(max_length=7)
    blood_group = models.CharField(max_length=5)
    passport = models.ImageField(upload_to='photos/', blank=False)
    signature = models.ImageField(upload_to='signature/', blank=False)

    def __str__(self):
        return self.name
