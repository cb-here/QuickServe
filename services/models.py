from django.db import models
from autoslug import AutoSlugField

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='service_name', unique=True, null=True)
    
    def __str__(self):
        return self.service_name
    
class SubService(models.Model):
    services = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='subservices') 
    sub_service_name = models.CharField(max_length=255)
    sub_service_image = models.ImageField(upload_to='subservice_images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = AutoSlugField(populate_from='sub_service_name', unique=True)

    def __str__(self):
        return self.sub_service_name