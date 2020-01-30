from django.contrib import admin
from . import models


admin.site.register(models.UserProfile)
admin.site.register(models.Friend)
admin.site.register(models.Rundown)
admin.site.register(models.RundownDetail)