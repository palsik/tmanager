# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views


urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('profile_sbt', views. profileView, name='submit-profile'),
    path('get_personnel', views.get_personnel, name='get_personnel'),
    path('create_task/', views.create_task, name='create_task'),
    path('task_list/', views.task_list, name='task_list'),
    path('assign_task/', views.assign_task, name='assign_task'),
    path('get_personnel_by_department/', views.get_personnel_by_department, name='get_personnel_by_department'),
    path('get_tasks_in_progress/', views.get_tasks_in_progress, name='get_tasks_in_progress'),
    path('initialize_task_count_for_new_personnel/', views.initialize_task_count_for_new_personnel, name='initialize_task_count_for_new_personnel'),
    path('assign_task_view_menu/', views.assign_task_view_menu, name='assign_task_view_menu'),
    path('fetch_clients/', views.fetch_clients, name='fetch_clients'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('auditing_dashboard/', views.auditing_dashboard, name='auditing_dashboard'),
    path('bookkeeping_dashboard/', views.bookkeeping_dashboard, name='bookkeeping_dashboard'),
    path('supervisor_dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('fetch_tasks_by_type/', views.fetch_tasks_by_type, name='fetch_tasks_by_type'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('fetch_personnel/', views.fetch_personnel, name='fetch_personnel'),  # new fetch personnel view
    path('client/<str:client_username>/tasks/', views.client_recurring_tasks, name='client_recurring_tasks'),    
    path('create_recurring_task/', views.create_recurring_task, name='create_recurring_task'),  # new recurring task creation view
    path('update_recurring_task/<int:task_id>/', views.update_recurring_task, name='update_recurring_task'),
    path('recurring_task/<int:task_id>/', views.recurring_task_detail, name='recurring_task_detail'),
    path('client_recurring_tasks/<int:client_id>/', views.client_recurring_tasks, name='client_recurring_tasks'),
    path('personnel/<str:personnel_username>/Rtasks/', views.personnel_assigned_Rtasks, name='personnel_assigned_Rtasks'),
    path('recurring_task/<int:pk>/', views.personnel_recurring_task_detail, name='personnel_recurring_task_detail'),
    path('blog-section', views.blogSections, name='blogSections'),

    # Saving blog Topic for future use
    path('save-blog-topic/<str:uniqueId>', views.deleteBlogTopic, name='delete-blog-topic'),

    path('gen-frm-blog-topic/<str:uniqueId>', views.genBlogFrmsvtopic, name='gen-blog-frm-topic'),

    path('save-blog-topic/<str:blogTopic>', views.saveBlogTopic, name='save-blog-topic'),

    path('use-blog-topic/<str:blogTopic>', views.useBlogTopic, name='use-blog-topic'),

    # using request to submit profile
    path('view-generated-blog/<slug:slug>', views.viewGeneratedBlog, name='view-generated-blog'),




    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
