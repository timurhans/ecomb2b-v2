from django.db import models
from django.contrib.auth.models import User

class Eventos(models.Model):
    user = models.CharField(max_length=30, null=False, blank=False)
    ip = models.CharField(max_length=100, null=False, blank=False)
    tipo = models.CharField(max_length=20, null=False, blank=False)
    date= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return str(self.user) + ': ' + str(self.date)
