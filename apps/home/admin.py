# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from apps.home.models import Profile, Profile1, Task, SubTask, RTaskFile, TaskAssignmentCount, Assignment, TaskCost, RecurringTask, RTaskUpdate, RecurrentFiles, RTaskDirectory
from django.db.models import Q  # Import Q for advanced filtering

# Registering your models
admin.site.register(Profile)

# Custom Admin class for Profile1
class Profile1Admin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('user', 'get_user_type_display', 'get_department_display', 'company', 'email', 'phone')
    
    # Add filters for user_type and department
    list_filter = ('user_type', 'department')
    
    # Allow search by fields
    search_fields = ['user__username', 'first_name', 'last_name', 'company', 'email']
    
    def get_queryset(self, request):
        """Customize the queryset to filter by user type and department."""
        queryset = super().get_queryset(request)

        # Show all profiles for superusers
        if request.user.is_superuser:
            return queryset  

        # Filter for 'client' user type and 'personnel' of auditing or bookkeeping
        return queryset.filter(
            Q(user_type='client') | 
            Q(user_type='personnel', department__in=['auditing', 'bookkeeping'])
        )

    def get_user_type_display(self, obj):
        """Get user type with correct spelling"""
        return dict(Profile1.USER_TYPES).get(obj.user_type, obj.user_type)

    def get_department_display(self, obj):
        """Get department with correct spelling"""
        return dict(Profile1.DEPARTMENTS).get(obj.department, obj.department)

    # Custom titles for admin columns
    get_user_type_display.short_description = 'User Type'
    get_department_display.short_description = 'Department'

# Register Profile1 with the custom admin class
admin.site.register(Profile1, Profile1Admin)

# Register other models as usual
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
