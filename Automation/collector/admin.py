from django.contrib import admin
from .models import IDCard

class IDCardAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'mat_number',
        'department',
        'gender',
    ]

    list_filter = [
        'gender',
        'department',
    ]


admin.site.register(IDCard, IDCardAdmin)

