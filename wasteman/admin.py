from django.contrib import admin
from wasteman import models
# Register your models here.
admin.site.register(models.Resident)
admin.site.register(models.WasteType)
admin.site.register(models.Waste)
admin.site.register(models.WasteCollector)
admin.site.register(models.IssueReport)
admin.site.register(models.PickupZone)
admin.site.register(models.Schedule)