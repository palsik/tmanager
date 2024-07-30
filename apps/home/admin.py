# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from apps.home.models import *


# Register your models here.
admin.site.register(Profile)
admin.site.register(Profile1)
admin.site.register(Task)
admin.site.register(SubTask)
admin.site.register(RTaskFile)
admin.site.register(TaskAssignmentCount)
admin.site.register(Assignment)
admin.site.register(TaskCost)
admin.site.register(RecurringTask)
admin.site.register(RTaskUpdate)  
admin.site.register(RecurrentFiles)
admin.site.register(RTaskDirectory)
# admin.site.register(Blog)
# admin.site.register(BlogSection)
