from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'holiday_type', 'year']
    list_filter = ['holiday_type', 'year']
    search_fields = ['name']
