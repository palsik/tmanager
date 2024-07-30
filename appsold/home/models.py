# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from datetime import timezone
from uuid import uuid4

import self as self
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django_resized import ResizedImageField
from django.utils import timezone
from django.urls import reverse
from uuid import uuid4
import os
from django.conf import settings


# Create your models here.

class Profile1(models.Model):
    USER_TYPES = [
        ('supervisor', 'Supervisor'),
        ('personnel', 'Personnel'),
        ('client', 'Client'),
    ]

    DEPARTMENTS = [
        ('auditing', 'Auditing'),
        ('bookkeeping', 'Bookkeeping'),
        ('hr', 'Human Resources'),
    ]

    user = models.OneToOneField(User, related_name='profile1', on_delete=models.CASCADE)
    uniqueId = models.CharField(null=True, blank=True, max_length=300)
    user_type = models.CharField(max_length=100, choices=USER_TYPES, blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENTS, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.first_name, self.last_name, self.email)

    def save(self, *args, **kwargs):
        if not self.pk:  # If it's a new instance
            self.date_created = timezone.now()  # Set date_created only for new instances
            if self.uniqueId is None:
                self.uniqueId = str(uuid4().hex)

            if not self.slug:
                self.slug = slugify('{} {} {}'.format(self.first_name, self.last_name, self.email))

        self.last_updated = timezone.localtime(timezone.now())  # Always update last_updated
        super(Profile1, self).save(*args, **kwargs)



class Profile(models.Model):
    SUBSCRIPTION_OPTIONS = [
        ('free', 'Free'),
        ('starter', 'Starter'),
        ('advanced', 'Advanced'),
    ]
    USER_TYPES = [
        ('supervisor', 'Supervisor'),
        ('client', 'Client'),
        ('personnel', 'Personnel'),
    ]
    DEPARTMENTS = [
        ('auditing', 'Auditing'),
        ('bookkeeping', 'Bookkeeping'),
    ]

    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    user_type = models.CharField(choices=USER_TYPES, default='supervisor', max_length=20)
    department = models.CharField(choices=DEPARTMENTS, max_length=20, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    firstname = models.CharField(max_length=100, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    uniqueId = models.CharField(null=True, blank=True, max_length=300)
    aboutinfo = models.CharField(max_length=250, blank=True, null=True)

    subscriptionType = models.CharField(choices=SUBSCRIPTION_OPTIONS, default='free', max_length=100)
    subscribed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {} {}'.format(self.firstname, self.lastname, self.email)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4().hex)

        self.slug = slugify('{} {} {}'.format(self.firstname, self.lastname, self.email))
        self.last_updated = timezone.localtime(timezone.now())
        super(Profile, self).save(*args, **kwargs)

# Task management Models
class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('on_hold', 'On Hold'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    task_id = models.AutoField(primary_key=True)
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    assigned_personnel = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned', null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='task_files/', null=True, blank=True)
    client = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.task_name

class SubTask(models.Model):
    parent_task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    subtask_name = models.CharField(max_length=100)
    description = models.TextField()
    assigned_personnel = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # Assuming user ID 1 exists
    status = models.CharField(max_length=20, choices=Task.STATUS_CHOICES, default='in_progress')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to='subtask_files/', null=True, blank=True)

    def __str__(self):
        return self.subtask_name    

    
class TaskFile(models.Model):
    task = models.ForeignKey(Task, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='task_files/')

    def __str__(self):
        return self.file.name

class TaskAssignmentCount(models.Model):
    personnel = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    task_count = models.IntegerField(default=0)
    department = models.CharField(max_length=50, choices=(('auditing', 'Auditing'), ('bookkeeping', 'Bookkeeping')),  null=True)

class Assignment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_received', null=True)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_given')
    assigned_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f'{self.task.task_name} - {self.assigned_to.username}'

 
class TaskCost(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='costs')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_costs')

    def __str__(self):
        return f"{self.description} - {self.amount}"
  
  
 
 #models handlling recurring 
class RecurrentFiles(models.Model):
    file = models.FileField(upload_to='recurrent_task_files/') 

class RecurringTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    INTERVAL_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    task_name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    assigned_personnel = models.ForeignKey(Profile1, on_delete=models.CASCADE, related_name='assigned_recurring_tasks')
    client = models.ForeignKey(Profile1, on_delete=models.CASCADE, related_name='recurring_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    files = models.ManyToManyField(RecurrentFiles, related_name='recurring_tasks', blank=True)  # New field for files

    def __str__(self):
        return self.task_name
    
class TaskUpdate(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE, related_name='updates')
    update_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=RecurringTask.STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    files = models.ManyToManyField(RecurrentFiles, related_name='task_updates', blank=True)

    def __str__(self):
        return f"Update for {self.task.task_name} on {self.update_date}"
    
def task_directory_path(instance, filename):
    client_name = instance.task.client.user.username
    year = instance.task.start_date.year
    month = instance.task.start_date.strftime('%B')
    task_name = instance.task.task_name
    return os.path.join('task_files', client_name, str(year), month, task_name, filename)

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # other fields
    
class RecurringTaskFile(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE, related_name='task_files')
    file = models.FileField(upload_to='recurrent_task_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Create directory structure before saving
        task = self.task
        task_year = task.start_date.year
        task_month = task.start_date.strftime("%B")
        task_path = os.path.join(settings.MEDIA_ROOT, 'recurrent_task_files', str(task.client.id), str(task_year), task_month, task.task_name)
        os.makedirs(task_path, exist_ok=True)
        self.file.name = os.path.join(task_path, os.path.basename(self.file.name))
        super().save(*args, **kwargs)

class TaskDirectory(models.Model):
    task = models.ForeignKey(RecurringTask, on_delete=models.CASCADE)
    client = models.ForeignKey(Profile1, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, blank=True)
    month = models.CharField(max_length=20, null=True, blank=True)
    path = models.CharField(max_length=255)

    def __str__(self):
        return self.path

  
class Blog(models.Model):
    title = models.CharField(max_length=200)
    blogIdea = models.CharField(null=True, blank=True, max_length=200)
    keywords = models.CharField(null=True, blank=True, max_length=300)
    audience = models.CharField(null=True, blank=True, max_length=100)
    wordcount = models.CharField(null=True, blank=True, max_length=100)

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)

    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.title,  self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4().hex)
            # self.uniqueId = str(uuid4()).split('_')[5]

        self.slug = slugify('{}{}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        super(Blog, self).save(*args, **kwargs)


class BlogSection(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True, max_length=200)
    wordcount = models.CharField(null=True, max_length=200)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    uniqueId = models.CharField(null=True, blank=True, max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}' '{}'.format(self.title, self.uniqueId)

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4().hex)
            # self.uniqueId = str(uuid4()).split('_')[4]

        self.slug = slugify('{} {}'.format(self.title, self.uniqueId))
        self.last_updated = timezone.localtime(timezone.now())
        ##Count words
        if self.body:
            x = len(self.body.split(' '))
            self.wordcount = str(x)
        super(BlogSection, self).save(*args, **kwargs)
