from django.contrib import admin

from scans import models


@admin.register(models.IssueScan)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['publication', 'issuecode', 'year']
    list_filter = ['publication', 'year']
