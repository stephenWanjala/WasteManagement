from django.contrib import admin

from wasteman import models


# Register your models here.

@admin.register(models.Resident)
class ResidentAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_location')
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('user',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('user', )}),
    )
    list_per_page = 20


@admin.register(models.WasteCollector)
class WasteCollectorAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    list_filter = ('user',)
    search_fields = ('user',)
    ordering = ('user',)
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('user', 'location')}),
    )
    list_per_page = 20


admin.site.register(models.WasteType)
admin.site.register(models.Waste)
admin.site.register(models.IssueReport)
admin.site.register(models.PickupZone)
admin.site.register(models.Schedule)
