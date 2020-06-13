from django.contrib import admin

# Register your models here.

from .models import (ColecaoB2b,ColecaoErp)


admin.site.register(ColecaoB2b)
admin.site.register(ColecaoErp)
