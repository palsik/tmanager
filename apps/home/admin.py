# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from apps.home.models import *

class TaskDirectoryAdmin(admin.ModelAdmin):
    list_display = ('task', 'client', 'year', 'month', 'path')
    search_fields = ('task__task_name', 'client__user__username', 'path')

# Register your models here.
admin.site.register(Profile)
admin.site.register(Profile1)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(TaskFile)
admin.site.register(TaskAssignmentCount)
admin.site.register(Assignment)
admin.site.register(TaskCost)
admin.site.register(RecurringTask)
admin.site.register(TaskUpdate)  
admin.site.register(RecurrentFiles)
admin.site.register(TaskDirectory, TaskDirectoryAdmin)
# admin.site.register(Blog)
# admin.site.register(BlogSection)
