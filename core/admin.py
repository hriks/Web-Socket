# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from core.models import WorkBook


@admin.register(WorkBook)
class WorkBookAdmin(admin.ModelAdmin):
    list_display = ("id", "role", "primary_skill", "secondary_skill")
    search_fields = ('id', "primary_skill", 'secondary_skill')
    list_filter = ('role',)
