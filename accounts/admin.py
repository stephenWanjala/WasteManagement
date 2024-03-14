from django.contrib import admin

from accounts import models


# Register your models here.
@admin.register(models.CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_resident', 'is_collector', 'location')
    list_filter = ('is_resident', 'is_collector')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'location')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    readonly_fields = ('date_joined', 'last_login')
    list_per_page = 20
    actions = ('make_resident', 'make_collector')

    def make_resident(self, request, queryset):
        queryset.update(is_resident=True)

    make_resident.short_description = 'Mark selected users as residents'

    def make_collector(self, request, queryset):
        queryset.update(is_collector=True)

    make_collector.short_description = 'Mark selected users as waste collectors'


admin.site.site_header = 'Waste Management Admin'
admin.site.site_title = 'Waste Management Admin Portal'
admin.site.index_title = 'Welcome to Waste Management Admin Portal'
admin.site.register(models.Resident)
admin.site.register(models.WasteType)
admin.site.register(models.Waste)
admin.site.register(models.WasteCollector)
admin.site.register(models.IssueReport)
admin.site.register(models.PickupZone)
admin.site.register(models.Schedule)
