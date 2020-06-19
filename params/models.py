from django.db import models

# Create your models here.

class ColecaoB2b(models.Model):
    title       = models.CharField(max_length=20, null=False, blank=False,unique=True)
    active      = models.BooleanField(default=True)
    ordem       = models.IntegerField(null=False, blank=False,unique=True)

    def __str__(self):
        return str(self.title)


class ColecaoErp(models.Model):
    codigo      = models.CharField(max_length=10, null=False, blank=False,unique=True)
    colecaoB2b        = models.ForeignKey(ColecaoB2b, null=False, blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.codigo)

class Banner(models.Model):
    ordem = models.IntegerField(null=False, blank=False,unique=True)
    url = models.CharField(max_length=150)
    img = models.ImageField(upload_to = 'static/banners/', null=False, blank=False)
    def __str__(self):
        return str(self.url)