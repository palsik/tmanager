# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import profile

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.contrib import messages
from numpy.ma import count
from django.core.exceptions import ObjectDoesNotExist

from apps.home.models import *
from apps.home.forms import *

from apps.home.functions import *

from django.http import JsonResponse
from .models import Task, Profile1

from django.shortcuts import get_object_or_404
from django.db.models import Min, Max
import logging
from datetime import date
from datetime import date, datetime
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@login_required(login_url="/login/")
def index(request):
    emptyBlogs = []
    completedBlogs = []
    monthCount = 0

    blogs = Blog.objects.filter(profile=request.user.profile)
    for blog in blogs:
        sections = BlogSection.objects.filter(blog=blog)
        if sections.exists():
            ## Calculate Blog Words
            blogwords = 0
            for section in sections:
                blogwords += int(section.wordcount)
                monthCount += int(section.wordcount)
            blog.wordcount = str(blogwords)
            blog.save()
            completedBlogs.append(blog)
        else:
            emptyBlogs.append(blog)

    # allowance = checkCountAllowance(request.user.profile)
    context = {'segment': 'index'}

    context['numBlogs'] = len(completedBlogs)
    context['monthCount'] = str(monthCount) ##update later
    context['emptyBlogs'] = emptyBlogs
    context['completedBlogs'] = completedBlogs
    # context['allowance'] = allowance

    html_template = loader.get_template('home/index3.html')
    # html_template = loader.get_template('home/profile.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def profileView(request):
    context = {}
    # user = profile.user

    if request.method == 'GET':
        form = profileForm(instance=request.user.Profile)
        context['form'] = form
        return render(request, 'home/profile.html', context)

    if request.method == 'POST':
        form = profileForm(request.POST, instance=request.user.Profile)

        if form.is_valid():
            # form.username = form.cleaned_data['username'],
            # form. = form.cleaned_data['email'],
            form.firstname = form.cleaned_data['firstname'],
            form.lastname = form.cleaned_data['lastname'],
            form.address = form.cleaned_data['address'],
            form.aboutinfo = form.cleaned_data['aboutinfo']

            print()

            form.save()
            return redirect('submit-profile')

    return render(request, 'home/profile.html')

def create_task(request):
    if request.method == 'POST':
        print('Create task has been reached')
        task_name = request.POST.get('task_name')
        description = request.POST.get('description')
        client_username = request.POST.get('client')
        files = request.FILES.getlist('file')  # Handle multiple file uploads

        # Save task to the database
        task = Task.objects.create(
            task_name=task_name,
            description=description,
            client=client_username,
            status='pending',
            created_at=timezone.now()
        )

        # Save uploaded files
        for uploaded_file in files:
            print(f'Uploading file: {uploaded_file.name}')
            TaskFile.objects.create(task=task, file=uploaded_file)

        # Return success response
        return JsonResponse({'success': True, 'message': 'Task created successfully'})
    else:
        # Return error response for non-POST requests
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

def task_list(request):
    tasks = Task.objects.all()
    return render(request, 'home/supervisor.html', {'tasks': tasks})

@login_required
def fetch_clients(request):
    print('The fetch_clients function has been reached')  # Debugging line
    if request.method == 'GET':
        clients_profiles = Profile1.objects.filter(user_type='client')

        client_list = [
            {
                "username": client_profile.username,
                "company": client_profile.company,
                "first_name": client_profile.first_name,
                "last_name": client_profile.last_name
            } for client_profile in clients_profiles
        ]

        print(client_list)  # Print the entire list in the console for debugging

        return JsonResponse({"clients": client_list})
    return JsonResponse({"error": "Invalid request"}, status=400)


from django.http import JsonResponse
from django.db.models import Min
from .models import Task, Profile1, TaskAssignmentCount  # Adjust imports based on your project structure
from django.core.exceptions import ObjectDoesNotExist

def assign_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        department = request.POST.get('department')
        assigned_to = request.POST.get('assigned_to')
        print('This is the department selected: ' + department)  # Print department selection

        if not task_id and department:  # When department is selected without task
            # Get all personnel in the department and their task counts
            personnel_in_department = Profile1.objects.filter(department=department, user_type='personnel')
            personnel_counts = TaskAssignmentCount.objects.filter(personnel__profile1__in=personnel_in_department)

            # Debug information for fetched personnel and task counts
            print(f'Personnel fetched for department "{department}": {[person.username for person in personnel_in_department]}')

            # Find personnel with the minimum task count within the selected department
            min_task_count = personnel_counts.aggregate(Min('task_count'))['task_count__min']
            eligible_personnel = personnel_counts.filter(task_count=min_task_count)

            # Return eligible personnel for manual selection if task count is same for all personnel
            eligible_personnel_list = eligible_personnel.values('personnel__id', 'personnel__first_name', 'personnel__last_name')
            print(f'Eligible personnel: {list(eligible_personnel_list)}')  # Print fetched personnel
            return JsonResponse({'success': True, 'personnel': list(eligible_personnel_list)})

        if task_id and assigned_to:
            print('this is the user ID of assigned_to ' + assigned_to)

            # Get the task
            try:
                task = Task.objects.get(task_id=task_id)
            except Task.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Task not found'})

            # Check if the task is pending
            if task.status != 'pending':
                return JsonResponse({'success': False, 'message': 'Only pending tasks can be assigned'})

            # Check if specific personnel is assigned
            try:
                assigned_profile = Profile1.objects.get(uniqueId=assigned_to)
                assigned_user = assigned_profile.username
                assigned_personnel = User.objects.get(username=assigned_user)
            except (ValueError, ObjectDoesNotExist):
                return JsonResponse({'success': False, 'message': 'Invalid user ID'})

            # Assign the task to the selected personnel
            task.assigned_personnel = assigned_personnel
            task.status = 'in_progress'
            task.save()

            # Update the task count for the assigned personnel
            assignment_count, created = TaskAssignmentCount.objects.get_or_create(personnel=assigned_personnel)
            assignment_count.task_count += 1
            assignment_count.department = department
            assignment_count.save()

            return JsonResponse({'success': True, 'message': 'Task assigned successfully'})

        return JsonResponse({'success': False, 'message': 'Task ID and Department are required'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})

# def get_personnel_by_department(request):
#     department = request.GET.get('department')
#     if department:
#         personnel = Profile1.objects.filter(department=department, user_type='personnel').values('user__id', 'first_name', 'last_name', 'uniqueId')
#         for person in personnel:
#             print( 'this is the correct user id' + f"UniqueId: {person['uniqueId']}")
#         return JsonResponse({'personnel': list(personnel)})
#     return JsonResponse({'personnel': []})

def get_personnel_by_department(request):
    department = request.GET.get('department')
    if not department:
        return JsonResponse({'personnel': []})

    # Get all personnel in the department
    personnel_in_department = Profile1.objects.filter(department=department, user_type='personnel')
    if not personnel_in_department.exists():
        return JsonResponse({'personnel': []})

    # Ensure task count is initialized for each personnel
    for personnel in personnel_in_department:
        username = personnel.username  # Get the username from the Profile1 instance
        user = User.objects.get(username=username)  # Get the User instance from the username
        TaskAssignmentCount.objects.get_or_create(personnel=user)

    # Get their task counts
    personnel_counts = TaskAssignmentCount.objects.filter(personnel__profile1__in=personnel_in_department)

    if not personnel_counts.exists():
        # No task counts found, return all personnel in the department
        personnel = personnel_in_department.values('user__id', 'first_name', 'last_name', 'uniqueId')
        for person in personnel:
            print(f"Personnel: {person['first_name']} {person['last_name']} (ID: {person['user__id']}, UniqueID: {person['uniqueId']}), Task Count: 0")
        return JsonResponse({'personnel': list(personnel)})

    # Find the minimum task count within the selected department
    min_task_count = personnel_counts.aggregate(Min('task_count'))['task_count__min']

    # Filter personnel with the minimum task count
    eligible_personnel = personnel_counts.filter(task_count=min_task_count)
    eligible_personnel_ids = eligible_personnel.values_list('personnel__profile1__user__id', flat=True)

    # Check if all personnel have the same task count
    if personnel_counts.values('task_count').distinct().count() == 1:
        # All personnel have the same task count, return all personnel in the department
        personnel = personnel_in_department.values('user__id', 'first_name', 'last_name', 'uniqueId')
    else:
        # Return only personnel with the minimum task count
        personnel = personnel_in_department.filter(user__id__in=eligible_personnel_ids).values('user__id', 'first_name', 'last_name', 'uniqueId')

    # Print the personnel list with their task counts
    for person in personnel:
        user_id = person['user__id']
        task_count = TaskAssignmentCount.objects.get(personnel__profile1__user__id=user_id).task_count
        print(f"Personnel: {person['first_name']} {person['last_name']} (ID: {user_id}, UniqueID: {person['uniqueId']}), Task Count: {task_count}")

    return JsonResponse({'personnel': list(personnel)})

@login_required
def get_tasks_in_progress(request):
    pending_tasks = Task.objects.filter(status='pending')
    tasks_list = list(pending_tasks.values('task_id', 'task_name'))
    return JsonResponse({'tasks': tasks_list})


def get_personnel(request):
    if request.is_ajax() and request.method == 'GET':
        department = request.GET.get('department')
        personnel_list = [{'id': personnel.id, 'name': f"{personnel.first_name} {personnel.last_name}"} for personnel in Profile1.objects.filter(department=department)]
        return JsonResponse({'personnel': personnel_list})
    else:
        return JsonResponse({'error': 'Invalid request'})
    
    
@login_required
def assign_task_view_menu(request):
    tasks_in_progress = Task.objects.filter(status='in_progress')
    context = {
        'tasks': tasks_in_progress,
        'departments': ['auditing', 'bookkeeping']
    }
    return render(request, 'assign_task.html', context)

# @login_required
def initialize_task_count_for_new_personnel(user, department):
    max_task_count = TaskAssignmentCount.objects.filter(personnel__profile1__department=department).aggregate(Max('task_count'))['task_count__max']
    max_task_count = max_task_count if max_task_count is not None else 0

    task_assignment_count, created = TaskAssignmentCount.objects.get_or_create(personnel=user, department=department)
    if created:
        task_assignment_count.task_count = max_task_count
        task_assignment_count.save()

# @login_required
# def create_recurring_task(request):
#     print('create_recurring_task has been reached')
#     if request.method == 'POST':
#         print("POST data received:")
#         print(request.POST)  # Print the entire POST data for debugging

#         task_name = request.POST.get('task_name')
#         description = request.POST.get('description')
#         start_date = request.POST.get('start_date')
#         end_date = request.POST.get('end_date')
#         interval = request.POST.get('interval')
#         client_username = request.POST.get('client1')
#         assigned_personnel_username = request.POST.get('assigned_personnel')

#         print(f"Task Name: {task_name}")
#         print(f"Description: {description}")
#         print(f"Start Date: {start_date}")
#         print(f"End Date: {end_date}")
#         print(f"Interval: {interval}")
#         print(f"Client Username: {client_username}")
#         print(f"Assigned Personnel Username: {assigned_personnel_username}")

#         try:
#             client = get_object_or_404(Profile1, user__username=client_username)
#             assigned_personnel = get_object_or_404(Profile1, user__username=assigned_personnel_username) if assigned_personnel_username else None

#             print(f"Client: {client}")
#             print(f"Assigned Personnel: {assigned_personnel}")

#             recurring_task = Task.objects.create(
#                 task_name=task_name,
#                 description=description,
#                 start_date=start_date,
#                 end_date=end_date,
#                 interval=interval,
#                 client=client.company,  # Assuming you want to store the company name
#                 assigned_personnel=assigned_personnel.user if assigned_personnel else None
#             )

#             if 'files' in request.FILES:
#                 recurring_task.file = request.FILES['files']
#                 recurring_task.save()

#             return JsonResponse({'message': 'Recurring task created successfully'})
#         except Profile1.DoesNotExist as e:
#             print(f"Profile1 does not exist: {e}")
#             return JsonResponse({'error': 'Profile1 does not exist'}, status=400)
#         except Exception as e:
#             print(f"Error: {e}")
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def fetch_personnel(request):
    print('Fetch personnel has been reached')
    if request.method == 'GET':
        personnel = User.objects.filter(profile1__user_type='personnel')
        personnel_list = [
            {
                "username": person.username,
                "first_name": person.profile1.first_name,
                "last_name": person.profile1.last_name
            } for person in personnel
        ]
        return JsonResponse({"personnel": personnel_list})
    return JsonResponse({"error": "Invalid request"}, status=400)


# Beginning of DashBoard Rendering
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Task, RecurringTask, Profile1

@login_required
def dashboard_view(request):
    user_profile = Profile1.objects.get(user=request.user)
    department = user_profile.department
    user_type = user_profile.user_type

    print('this is the user at the dashboard_view :' + str(department))

    if department == 'auditing':
        return auditing_dashboard(request)
    
    elif department == 'bookkeeping':
        return bookkeeping_dashboard(request)
    
    elif user_type == 'supervisor':
        return supervisor_dashboard(request)
    else:
        return redirect('home')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Task, RecurringTask, Profile1

@login_required
def auditing_dashboard(request):
    # Get the logged-in user's Profile1 instance
    user_Profile1 = Profile1.objects.get(user=request.user)
    print("User Profile ID:", user_Profile1.id)
    print("Assigned User:", user_Profile1.user.username)
    
    # Single tasks categorized by status
    tasks_pending = Task.objects.filter(assigned_personnel=user_Profile1.user, status='pending')
    tasks_in_progress = Task.objects.filter(assigned_personnel=user_Profile1.user, status='in_progress')
    tasks_completed = Task.objects.filter(assigned_personnel=user_Profile1.user, status='completed')
    tasks_approved = Task.objects.filter(assigned_personnel=user_Profile1.user, status='approved')
    tasks_on_hold = Task.objects.filter(assigned_personnel=user_Profile1.user, status='on_hold')
    
    # Print the task IDs to debug
    for task in tasks_in_progress:
        print("In Progress Task ID:", task.task_id, "Task Name:", task.task_name)

    # Recurring tasks categorized by status
    recurring_tasks_pending = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='pending')
    recurring_tasks_in_progress = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='in_progress')
    recurring_tasks_completed = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='completed')
    recurring_tasks_on_hold = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='on_hold')
    recurring_tasks_approved = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='approved')
    recurring_tasks_assigned = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='assigned')
    
    # Print the recurring task IDs to debug
    for task in recurring_tasks_pending:
        print("Pending Recurring Task ID:", task.id, "Task Name:", task.task_name)

    return render(request, "home/adt_dashboard.html", {
        "tasks_pending": tasks_pending,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "tasks_approved": tasks_approved,
        "tasks_on_hold": tasks_on_hold,
        "recurring_tasks_pending": recurring_tasks_pending,
        "recurring_tasks_in_progress": recurring_tasks_in_progress,
        "recurring_tasks_completed": recurring_tasks_completed,
        "recurring_tasks_on_hold": recurring_tasks_on_hold,
        "recurring_tasks_approved": recurring_tasks_approved,
        "recurring_tasks_assigned": recurring_tasks_assigned,
    })

@login_required
def bookkeeping_dashboard(request):

    # Get the logged-in user's Profile1 instance
    user_Profile1 = Profile1.objects.get(user=request.user)
    print("User Profile ID:", user_Profile1.id)
    print("Assigned User:", user_Profile1.user.username)
    
    # Single tasks categorized by status
    tasks_pending = Task.objects.filter(assigned_personnel=user_Profile1.user, status='pending')
    tasks_in_progress = Task.objects.filter(assigned_personnel=user_Profile1.user, status='in_progress')
    tasks_completed = Task.objects.filter(assigned_personnel=user_Profile1.user, status='completed')
    tasks_approved = Task.objects.filter(assigned_personnel=user_Profile1.user, status='approved')
    tasks_on_hold = Task.objects.filter(assigned_personnel=user_Profile1.user, status='on_hold')
    
    # Print the task IDs to debug
    for task in tasks_in_progress:
        print("In Progress Task ID:", task.task_id, "Task Name:", task.task_name)

    # Recurring tasks categorized by status
    recurring_tasks_pending = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='pending')
    recurring_tasks_in_progress = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='in_progress')
    recurring_tasks_completed = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='completed')
    recurring_tasks_on_hold = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='on_hold')
    recurring_tasks_approved = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='approved')
    recurring_tasks_assigned = RecurringTask.objects.filter(assigned_personnel=user_Profile1, status='assigned')
    
    # Print the recurring task IDs to debug
    for task in recurring_tasks_pending:
        print("Pending Recurring Task ID:", task.id, "Task Name:", task.task_name)

    return render(request, "home/bk_dashboard.html", {
        "tasks_pending": tasks_pending,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "tasks_approved": tasks_approved,
        "tasks_on_hold": tasks_on_hold,
        "recurring_tasks_pending": recurring_tasks_pending,
        "recurring_tasks_in_progress": recurring_tasks_in_progress,
        "recurring_tasks_completed": recurring_tasks_completed,
        "recurring_tasks_on_hold": recurring_tasks_on_hold,
        "recurring_tasks_approved": recurring_tasks_approved,
        "recurring_tasks_assigned": recurring_tasks_assigned,
    })


@login_required
def supervisor_dashboard(request):
    # Categorize regular tasks by status
    tasks_pending = Task.objects.filter(status='pending')
    tasks_in_progress = Task.objects.filter(status='in_progress')
    tasks_completed = Task.objects.filter(status='completed')
    tasks_approved = Task.objects.filter(status='approved')
    tasks_on_hold = Task.objects.filter(status='on_hold')

    # Get clients with recurring tasks
    clients_with_recurring_tasks = Profile1.objects.filter(recurring_tasks__isnull=False).distinct()

    # Categorize recurring tasks by status
    recurring_tasks_pending = RecurringTask.objects.filter(status='pending')
    recurring_tasks_in_progress = RecurringTask.objects.filter(status='in_progress')
    recurring_tasks_completed = RecurringTask.objects.filter(status='completed')
    recurring_tasks_on_hold = RecurringTask.objects.filter(status='on_hold')
    recurring_tasks_approved = RecurringTask.objects.filter(status='approved')
    recurring_tasks_assigned = RecurringTask.objects.filter(status='assigned')
    return render(request, "home/supervisor.html", {
        "tasks_pending": tasks_pending,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "tasks_approved": tasks_approved,
        "tasks_on_hold": tasks_on_hold,
        "clients_with_recurring_tasks": clients_with_recurring_tasks,
        "recurring_tasks_pending": recurring_tasks_pending,
        "recurring_tasks_in_progress": recurring_tasks_in_progress,
        "recurring_tasks_completed": recurring_tasks_completed,
        "recurring_tasks_on_hold": recurring_tasks_on_hold,
        "recurring_tasks_approved": recurring_tasks_approved,
    })


@login_required
def task_detail(request, task_id):
    print('The mail task detail has been reached')
    
    # Get the task object
    task = get_object_or_404(Task, task_id=task_id)
    
    # Get the user's profile
    user_profile = Profile1.objects.get(user=request.user)
    
    # Attempt to fetch the client profile using the client field in the task (which is a string)
    client_profile = Profile1.objects.filter(user__username=task.client).first()
    
    directories = TaskDirectory.objects.filter(task=task)
    files = TaskFile.objects.filter(directory__in=directories)
    costs = TaskCost.objects.filter(task=task)

    if request.method == 'POST':
        # Code for handling POST requests for status update, directory creation, file upload, and cost addition
        
        # Status update logic
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            print('condition for Post update status met')
            if user_profile.user_type == 'supervisor':
                print('condition for supervisor status met')
                if new_status in ['in_progress', 'approved']:
                    task.status = new_status
                    send_status_email_to_personnel(task, task.assigned_personnel.email)
            elif user_profile.user_type == 'personnel':
                print('condition for personnel status met')
                if new_status in ['on_hold', 'completed']:
                    task.status = new_status
                    print(f'The task is: {task.task_name}, The mail is: office@nelkins.com')
                    send_status_email_to_supervisor(task, 'office@nelkins.com')
            task.save()
            return redirect('task_detail', task_id=task_id)

        # Directory creation logic
        elif 'create_directory' in request.POST:
            directory_name = request.POST.get('directory_name')
            if directory_name:
                TaskDirectory.objects.create(
                    name=directory_name,
                    task=task,
                    created_by=request.user
                )
                return redirect('task_detail', task_id=task_id)
        
        # File upload logic
        elif 'upload_file' in request.POST:
            description = request.POST.get('file_description', '')
            if 'file' in request.FILES:
                TaskFile.objects.create(
                    directory=TaskDirectory.objects.get(id=request.POST.get('directory_id')),
                    file=request.FILES['file'],
                    uploaded_by=request.user,
                    description=description
                )
                return redirect('task_detail', task_id=task_id)
        
        # Cost addition logic
        elif 'add_cost' in request.POST:
            description = request.POST.get('cost_description')
            amount = request.POST.get('cost_amount')
            if description and amount:
                TaskCost.objects.create(
                    task=task,
                    description=description,
                    amount=amount,
                    created_by=request.user
                )
                return redirect('task_detail', task_id=task_id)

    return render(request, 'home/task_detail.html', {
        'task': task,
        'user_profile': user_profile,
        'client_profile': client_profile,  # Pass the client profile to the template
        'directories': directories,
        'files': files,
        'costs': costs,
    })


def send_status_email_to_personnel(task, recipient_email):
    send_mail(
        f'Task: "{task.task_name}" Status Updated', 
        f'The status of task "{task.task_name}" has been updated to "{task.status}" by Supervisor.',
        'office@nelkins.com',
        [recipient_email],
        fail_silently=False,
    )

def send_status_email_to_supervisor(task, recipient_email):
    send_mail(
        f'Task: "{task.task_name}" Status Updated',
        f'The status of task "{task.task_name}" has been updated to "{task.status}" by "{task.assigned_personnel}"  .',
        'office@nelkins.com',
        [recipient_email],
        fail_silently=False,
    )

@login_required
def task_directory_detail(request, task_id, directory_id):
    task = get_object_or_404(Task, task_id=task_id)
    directory = get_object_or_404(TaskDirectory, id=directory_id, task=task)

    subdirectories = TaskDirectory.objects.filter(parent_directory=directory)
    files = TaskFile.objects.filter(directory=directory)

    if request.method == 'POST':
        if 'create_subdirectory' in request.POST:
            subdirectory_name = request.POST.get('subdirectory_name')
            if subdirectory_name:
                TaskDirectory.objects.create(
                    name=subdirectory_name,
                    task=task,
                    parent_directory=directory,
                    created_by=request.user
                )
                return redirect('task_directory_detail', task_id=task_id, directory_id=directory_id)
        elif 'upload_file' in request.POST:
            if 'files' in request.FILES:
                uploaded_files = request.FILES.getlist('files')
                description = request.POST.get('description', '')
                for uploaded_file in uploaded_files:
                    TaskFile.objects.create(
                        directory=directory,
                        file=uploaded_file,
                        uploaded_by=request.user,
                        description=description
                    )
                return redirect('task_directory_detail', task_id=task_id, directory_id=directory_id)

    return render(request, 'home/task_directory_detail.html', {
        'task': task,
        'directory': directory,
        'subdirectories': subdirectories,
        'files': files,
        'path': get_directory_path(directory),
    })

def get_directory_path(directory):
    path = []
    current_directory = directory
    while current_directory is not None:
        path.insert(0, current_directory)
        current_directory = current_directory.parent_directory
    return path


@login_required
def fetch_tasks_by_type(request):
    user = request.user
    
    try:
        profile = Profile1.objects.get(user=user)
        user_type = profile.user_type
        department = profile.department
        
        # Fetch tasks assigned to the current user based on their user_type and department
        tasks = Task.objects.filter(
            assigned_personnel=user, 
            assigned_personnel__profile1__user_type=user_type, 
            assigned_personnel__profile1__department=department
        )

        # Categorize tasks by status
        tasks_pending = tasks.filter(status='pending')
        tasks_in_progress = tasks.filter(status='in_progress')
        tasks_on_hold = tasks.filter(status='on_hold')
        tasks_completed = tasks.filter(status='completed')
        tasks_approved = tasks.filter(status='approved')

        # Debugging output
        print(f"Pending Tasks: {tasks_pending.count()}")
        print(f"In Progress Tasks: {tasks_in_progress.count()}")
        print(f"On Hold Tasks: {tasks_on_hold.count()}")
        print(f"Completed Tasks: {tasks_completed.count()}")
        print(f"Approved Tasks: {tasks_approved.count()}")

        # Render the template with the categorized tasks
        return render(request, "home/adt_dashboard.html", {
            'tasks_pending': tasks_pending,
            'tasks_in_progress': tasks_in_progress,
            'tasks_on_hold': tasks_on_hold,
            'tasks_completed': tasks_completed,
            'tasks_approved': tasks_approved,
        })
    
    except Profile1.DoesNotExist:
        print(f"No profile found for username: {user.username}")
        return render(request, "home/adt_dashboard.html", {
            'tasks_pending': [],
            'tasks_in_progress': [],
            'tasks_on_hold': [],
            'tasks_completed': [],
            'tasks_approved': [],
        })

# Adding the view functions for recurring task

def create_recurring_task(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        description = request.POST.get('description')
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        interval = request.POST.get('interval')
        client_username = request.POST.get('client1')
        assigned_personnel_username = request.POST.get('assigned_personnel')

        print("POST data received:")
        print(f"Task Name: {task_name}")
        print(f"Description: {description}")
        print(f"Start Date: {start_date_str}")
        print(f"End Date: {end_date_str}")
        print(f"Interval: {interval}")
        print(f"Client Username: {client_username}")
        print(f"Assigned Personnel Username: {assigned_personnel_username}")

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            print(f"Converted Start Date: {start_date}")
            print(f"Converted End Date: {end_date}")

            client_profile = Profile1.objects.get(user__username=client_username)
            assigned_personnel_profile = Profile1.objects.get(user__username=assigned_personnel_username)

            print(f"Client Profile: {client_profile}")
            print(f"Assigned Personnel Profile: {assigned_personnel_profile}")
            
            recurring_task = RecurringTask.objects.create(
                task_name=task_name,
                interval=interval,
                description=description,
                start_date=start_date,
                end_date=end_date,
                client=client_profile,
                assigned_personnel=assigned_personnel_profile
            )
            recurring_task.save()

            if request.FILES.getlist('files'):
                for file in request.FILES.getlist('files'):
                    task_file = RecurrentFiles.objects.create(file=file)
                    recurring_task.files.add(task_file)

            # create_task_directories(recurring_task)

            print("Recurring task created successfully")
            return JsonResponse({'message': 'Recurring task created successfully'})
        except Profile1.DoesNotExist as e:
            print(f"Profile1 does not exist: {e}")
            return JsonResponse({'error': 'Profile does not exist'}, status=400)
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
@login_required
def recurring_task_dashboard(request):
    # Fetch recurrent tasks based on their status
    tasks_pending = RecurringTask.objects.filter(status='pending')
    tasks_in_progress = RecurringTask.objects.filter(status='in_progress')
    tasks_on_hold = RecurringTask.objects.filter(status='on_hold')
    tasks_completed = RecurringTask.objects.filter(status='completed')

    return render(request, 'recurring_task_dashboard.html', {
        'tasks_pending': tasks_pending,
        'tasks_in_progress': tasks_in_progress,
        'tasks_on_hold': tasks_on_hold,
        'tasks_completed': tasks_completed
    })
    # Fetch tasks based on their status
    tasks_pending = RecurringTask.objects.filter(status='pending')
    tasks_in_progress = RecurringTask.objects.filter(status='in_progress')
    tasks_on_hold = RecurringTask.objects.filter(status='on_hold')
    tasks_completed = RecurringTask.objects.filter(status='completed')

    return render(request, 'supervisor.html', {
        'tasks_pending': tasks_pending,
        'tasks_in_progress': tasks_in_progress,
        'tasks_on_hold': tasks_on_hold,
        'tasks_completed': tasks_completed
    })

@login_required
def update_recurring_task(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    user_profile = Profile1.objects.get(user=request.user)
    
    if request.method == 'POST':
        if 'update_task' in request.POST:
            status = request.POST.get('status')
            remarks = request.POST.get('remarks')

            task_update = RTaskUpdate.objects.create(
                task=task,
                status=status,
                remarks=remarks
            )

            if request.FILES.getlist('files'):
                for file in request.FILES.getlist('files'):
                    task_file = RecurrentFiles.objects.create(file=file)
                    task_update.files.add(task_file)
            task_update.save()

            return JsonResponse({'message': 'Task updated successfully'})

        elif 'add_cost' in request.POST:
            description = request.POST.get('cost_description')
            amount = request.POST.get('cost_amount')

            if description and amount:
                RTaskCost.objects.create(
                    task=task,
                    description=description,
                    amount=amount,
                    created_by=request.user
                )
                return JsonResponse({'message': 'Cost added successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# def recurring_task_detail(request, task_id):
#     task = get_object_or_404(RecurringTask, id=task_id)
#     months = ["January", "February", "March", "April", "May", "June", 
#               "July", "August", "September", "October", "November", "December"]
#     return render(request, 'home/recurrent_task_detail.html', {
#         'task': task,
#         'months': months,
#     })

def client_tasks(request, client_username):
    client = get_object_or_404(Profile1, user__username=client_username)
    tasks = Task.objects.filter(client=client)
    return render(request, 'home/client_recurring_tasks.html', {
        'client': client,
        'tasks': tasks,
    })

def client_recurring_tasks(request, client_username):
    client = get_object_or_404(Profile1, user__username=client_username)
    recurring_tasks = RecurringTask.objects.filter(client=client)
    return render(request, 'home/client_recurring_tasks.html', {
        'client': client,
        'recurring_tasks': recurring_tasks,
    })

@login_required
def recurring_task_detail(request, task_id):
    task = get_object_or_404(RecurringTask, pk=task_id)
    user_profile = Profile1.objects.get(user=request.user)
    files = task.files.all()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in ['pending', 'completed']:
                task.status = new_status
                task.save()
                return redirect('recurring_task_detail', task_id=task_id)

    return render(request, 'home/recurring_task_detail.html', {
        'task': task,
        'user_profile': user_profile,
        'files': files,
    })

def personnel_assigned_Rtasks(request, personnel_username):
    try:
        personnel_profile = Profile1.objects.get(user__username=personnel_username)
        print(f"Personnel Profile: {personnel_profile}")
    except Profile1.DoesNotExist:
        print(f"No profile found for username: {personnel_username}")
        return render(request, 'home/personnel_assigned_Rtasks.html', {
            'error': 'No profile found for this username'
        })

    assigned_tasks = RecurringTask.objects.filter(assigned_personnel=personnel_profile)
    print(f"Assigned Tasks for {personnel_profile.user.username}: {assigned_tasks}")

    return render(request, 'home/personnel_assigned_Rtasks.html', {
        'personnel': personnel_profile,
        'assigned_tasks': assigned_tasks,
    })

@login_required
def personnel_recurring_task_detail(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    updates = RTaskUpdate.objects.filter(task=task)
    directories = RTaskDirectory.objects.filter(task=task, parent_directory__isnull=True)

    if request.method == 'POST':
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            print('condition for Post update status met')
            user_profile = Profile1.objects.get(user=request.user)
            if user_profile.user_type == 'personnel':
                print('condition for personnel status met')
                if new_status in ['on_hold', 'completed']:
                    task.status = new_status
                    task.save()
                    print(f'The task is: {task.task_name}, The mail is: {task.assigned_personnel.email}')
                    send_status_email_to_supervisor1(task, 'office@nelkins.com')
            return redirect('personnel_recurring_task_detail', task_id=task_id)
        elif 'create_directory' in request.POST:
            return Rcreate_directory(request, task_id)
        elif 'upload_file' in request.POST:
            directory_id = request.POST.get('directory_id')
            if directory_id:
                return Rupload_file(request, task_id, directory_id)

    return render(request, 'home/personnel_recurring_task_detail.html', {
        'task': task,
        'updates': updates,
        'directories': directories,
    })

def send_status_email_to_supervisor1(task, recipient_email):
    send_mail(
        f'Task "{task.task_name}" Status Updated',
        f'Task: "{task.task_name}" has been updated to "{task.status}" by "{task.assigned_personnel}" .',
        'office@nelkins.com',
        [recipient_email],
        fail_silently=False,
    )

@login_required
def supervisor_recurring_task_detail(request, task_id):
    print('supervisor_recurring_task_detail has been reached')
    task = get_object_or_404(RecurringTask, id=task_id)
    updates = RTaskUpdate.objects.filter(task=task)
    directories = RTaskDirectory.objects.filter(task=task, parent_directory__isnull=True)

    if request.method == 'POST':
        if 'update_status' in request.POST:
            new_status = request.POST.get('status')
            print('condition for Post update status met')
            user_profile = Profile1.objects.get(user=request.user)
            if user_profile.user_type == 'supervisor':
                print('condition for supervisor status met')
                if new_status in ['in_progress', 'approved']:
                    task.status = new_status
                    task.save()
                    print(f'The task is: {task.task_name}, The mail is: {task.assigned_personnel.email}')
                    send_status_email_to_personnel1(task, task.assigned_personnel.email)
            return redirect('supervisor_recurring_task_detail', task_id=task_id)
        elif 'create_directory' in request.POST:
            return Rcreate_directory(request, task_id)
        elif 'upload_file' in request.POST:
            directory_id = request.POST.get('directory_id')
            print(f"Directory ID from POST: {directory_id}")
            if directory_id:
                return Rupload_file(request, task_id, directory_id)

    return render(request, 'home/supervisor_recurring_task_detail.html', {
        'task': task,
        'updates': updates,
        'directories': directories,
        'client': task.client,  # Pass the client to the template
    })


def send_status_email_to_personnel1(task, recipient_email):
    print(f'send reccurring status to personnel is reached to {recipient_email}.')
    send_mail(
        f'Task: "{task.task_name}" Status Updated', 
        f'The status of task "{task.task_name}" has been updated to "{task.status}" by Supervisor.',
        'office@nelkins.com',
        [recipient_email],
        fail_silently=False,
    )


def create_directory_in_media(path):
    """
    Utility function to create a directory in the media folder.
    """
    os.makedirs(path, exist_ok=True)

@login_required
def Rcreate_directory(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    user = request.user

    try:
        main_directory = RTaskDirectory.objects.get(task=task, parent_directory__isnull=True, name=task.task_name)
    except RTaskDirectory.DoesNotExist:
        main_directory = RTaskDirectory.objects.create(
            task=task,
            name=task.task_name,
            created_by=request.user
        )
        create_directory_in_media(os.path.join(settings.MEDIA_ROOT, 'recurrent_task_files', str(main_directory.id)))

    if request.method == 'POST':
        directory_name = request.POST.get('directory_name')
        parent_directory_id = request.POST.get('parent_directory_id')
        parent_directory = None
        if parent_directory_id:
            parent_directory = get_object_or_404(RTaskDirectory, id=parent_directory_id)

        new_directory = RTaskDirectory.objects.create(
            task=task,
            name=directory_name,
            parent_directory=parent_directory or main_directory,
            created_by=request.user
        )
        parent_directory_path = os.path.join(settings.MEDIA_ROOT, 'recurrent_task_files', str(main_directory.id))
        create_directory_in_media(os.path.join(parent_directory_path, str(new_directory.id)))

        print(f"Directory created: {new_directory.name}")

        profile = Profile1.objects.get(user=user)
        if profile.user_type == 'personnel':  # Assuming user_type attribute exists
            return redirect('personnel_recurring_task_detail', task_id=task_id)
        else:
            return redirect('supervisor_recurring_task_detail', task_id=task_id)

    updates = RTaskUpdate.objects.filter(task=task)
    directories = RTaskDirectory.objects.filter(task=task, parent_directory__isnull=True)
    
    profile = Profile1.objects.get(user=user)
    if profile.user_type == 'personnel':  # Assuming user_type attribute exists
        template = 'home/personnel_recurring_task_detail.html'
    else:
        template = 'home/supervisor_recurring_task_detail.html'

    return render(request, template, {
        'task': task,
        'updates': updates,
        'directories': directories,
    })

@login_required
def Rupload_file(request, task_id, directory_id):
    print(f"Upload file view called with task_id: {task_id} and directory_id: {directory_id}")
    task = get_object_or_404(RecurringTask, id=task_id)
    directory = get_object_or_404(RTaskDirectory, id=directory_id)

    if 'file' not in request.FILES:
        return HttpResponseBadRequest("No file uploaded")

    uploaded_file = request.FILES['file']
    description = request.POST.get('description', '')

    file_instance = RTaskFile(
        directory=directory,
        file=uploaded_file,
        uploaded_by=request.user,
        description=description
    )
    file_instance.save()
    print(f"File uploaded: {uploaded_file.name}")

    return redirect('supervisor_recurring_task_detail', task_id=task_id)

@login_required
def delete_directory(request, directory_id):
    directory = get_object_or_404(RTaskDirectory, id=directory_id)
    task_id = directory.task.id
    if request.user.profile1.user_type == 'supervisor':
        directory.delete()
        messages.success(request, 'Directory deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this directory.')
    return redirect('supervisor_recurring_task_detail', task_id=task_id)

@login_required
def delete_file(request, file_id):
    rtask_file = get_object_or_404(RTaskFile, id=file_id)
    task_id = rtask_file.directory.task.id
    if request.user.profile1.user_type == 'supervisor':
        rtask_file.delete()
        messages.success(request, 'File deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this file.')
    return redirect('supervisor_recurring_task_detail', task_id=task_id)

@login_required
def recurring_directory_details(request, directory_id):
    directory = get_object_or_404(RTaskDirectory, id=directory_id)
    task = directory.task
    subdirectories = directory.subdirectories.all()
    files = directory.files.all()

    files_with_basename = [
        {
            'basename': os.path.basename(file.file.name),
            'description': file.description,
            'uploaded_by': file.uploaded_by,
            'upload_date': file.upload_date,
            'url': file.file.url
        }
        for file in files
    ]

    path = []
    current_directory = directory
    while current_directory is not None:
        path.insert(0, current_directory)
        current_directory = current_directory.parent_directory

    if request.method == 'POST':
        if 'create_subdirectory' in request.POST:
            subdirectory_name = request.POST.get('subdirectory_name')
            if subdirectory_name:
                RTaskDirectory.objects.create(
                    name=subdirectory_name,
                    task=task,
                    parent_directory=directory,
                    created_by=request.user
                )
                return redirect('recurring_directory_details', directory_id=directory_id)
        elif 'upload_file' in request.POST:
            if 'files' in request.FILES:
                uploaded_files = request.FILES.getlist('files')
                description = request.POST.get('description', '')
                for uploaded_file in uploaded_files:
                    RTaskFile.objects.create(
                        directory=directory,
                        file=uploaded_file,
                        uploaded_by=request.user,
                        description=description
                    )
                return redirect('recurring_directory_details', directory_id=directory_id)

    return render(request, 'home/recurring_directory_details.html', {
        'directory': directory,
        'task': task,
        'subdirectories': subdirectories,
        'files': files_with_basename,
        'path': path,
    })

def task_file_path(instance, filename):
    return f'recurrent_task_files/{instance.directory.task.id}/files/{filename}'

@login_required
def create_subdirectory(request, directory_id):
    if request.method == 'POST':
        parent_directory = get_object_or_404(RTaskDirectory, id=directory_id)
        subdirectory_name = request.POST.get('subdirectory_name')
        new_subdirectory = RTaskDirectory(
            name=subdirectory_name,
            task=parent_directory.task,
            parent_directory=parent_directory,
            created_by=request.user,
        )
        new_subdirectory.save()
        print(f"Subdirectory created: {new_subdirectory.name}")
        return redirect('recurring_directory_details', directory_id=directory_id)
    else:
        return HttpResponseBadRequest("Invalid request method")
    
@login_required
def upload_files(request, directory_id):
    if request.method == 'POST':
        directory = get_object_or_404(RTaskDirectory, id=directory_id)
        files = request.FILES.getlist('files')
        descriptions = request.POST.getlist('descriptions')
        for file, description in zip(files, descriptions):
            file_instance = RTaskFile(
                directory=directory,
                file=file,
                description=description,
                uploaded_by=request.user,
                upload_date=timezone.now()
            )
            file_instance.save()
            print(f"File uploaded: {file.name}, Description: {description}")
        return redirect('recurring_directory_details', directory_id=directory_id)
    else:
        return HttpResponseBadRequest("Invalid request method")

@login_required
def Radd_task_update(request, pk):
    task = get_object_or_404(RecurringTask, pk=pk)
    if request.method == 'POST':
        update_text = request.POST.get('update_text')
        task_update = RTaskUpdate(task=task, update_text=update_text, updated_by=request.user.profile1)
        task_update.save()
        return redirect('personnel_recurring_task_detail', pk=pk)
    return JsonResponse({"error": "Invalid request method"}, status=400)           

@login_required(login_url="/login/")
def blogTopic(request):
    context = {}

    if request.method == 'POST':
        # Retrieve the bogIdea String from the submitted FORM from request.POST
        blogIdea = request.POST['blogIdea']
        # saving the blodIdea string in the session for later route access
        request.session['blogIdea'] = blogIdea
        keywords = request.POST['keywords']
        request.session['keywords'] = keywords
        audience = request.POST['audience']
        request.session['audience'] = audience

        blogTopics = generatedBlogTopicIdeas(blogIdea, audience, keywords)
        if len(blogTopics) > 0:
            request.session['blogTopics'] = blogTopics
            return redirect('blogSections')
        else:
            messages.error("Ops we could not generate blog Ideas, Please try again")
            return redirect('frm-gen-blogt')

    return render(request, 'home/gen-blog.html')


@login_required(login_url="/login/")
def blogSections(request):
    if 'blogTopics' in request.session:
        pass
    else:
        messages.error(request, "Start by Creating blog topic Ideas")
        return redirect('blog-topic')

    context = {}
    blogTopics = request.session['blogTopics']
    context['blogTopics'] = blogTopics

    print(blogTopics)

    print("The size of blogTopic after receiving through session \n")
    print(len(blogTopics))

    # a_list = blogTopics.split('/n')

    if len(blogTopics) > 0:
        for blog in blogTopics:
            print(blog)

    return render(request, 'home/blog-Sections.html', context)


@login_required(login_url="/login/")
def saveBlogTopic(request, blogTopic):
    if 'blogIdea' in request.session and 'keywords' in request.session and 'audience' in request.session and \
            'blogTopics' in request.session:
        blog = Blog.objects.create(
            title=blogTopic,
            blogIdea=request.session['blogIdea'],
            keywords=request.session['keywords'],
            audience=request.session['audience'],
            profile=request.user.Profile, )
        blog.save()

        blogTopics = request.session['blogTopics']
        blogTopics.remove(blogTopic)

        request.session['blogTopics'] = blogTopics

        return redirect('blogSections')
    else:
        return redirect('frm-gen-blogt')

        # context = {}
        # blogTopics = request.session['blogTopics']
        # context['blogTopics'] = blogTopics


@login_required(login_url="/login/")
def deleteBlogTopic(request, uniqueId):
    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
        if blog.profile == request.user.Profile:
            blog.delete()
            return redirect('home')
        else:
            messages.error(request, "Access Denied")
            return redirect('home')
    except:
        messages.error(request, "Blog not found")
        return redirect('home')


# def profile(request):
#     contex = {}
#
#     if request.method == 'GET':
#         form = profileForm(request)
#         contex['form'] = form
#         return render(request, 'home/profile.html', contex)
#
#     if request.method == 'POST':
#         form = profileForm(request.POST)
#         if form.is_valid():
#             pass
#         if form.is_valid():
#             pass
#             # form.save()
#
#     return render(request, 'home/profile.html', contex)
#
#     context = {}
#
#     return render(request, 'home/profile.html')


@login_required(login_url="/login/")
def useBlogTopic(request, blogTopic):
    context = {}
    if 'blogIdea' in request.session and 'keywords' in request.session and 'audience' in request.session:
        # Start by saving the Blog
        blog = Blog.objects.create(
            title=blogTopic,
            blogIdea=request.session['blogIdea'],
            keywords=request.session['keywords'],
            audience=request.session['audience'],
            profile=request.user.Profile, )
        blog.save()

        blogSections = generatedBlogSectionTitles(blogTopic, request.session['audience'], request.session['keywords'])
    else:
        return redirect('frm-gen-blogt')

    if len(blogSections) > 0:
        # Adding the sections to the sessions
        request.session['blogSections'] = blogSections

        # Adding the sections to the context
        context['blogSections'] = blogSections
    else:
        messages.error(request, 'Oops something went wrong try again')
        return redirect('frm-gen-blogt')

    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val:
                print(val)
                # Generating blogSection details
                sectionTopics = val
                section = generatedBlogSectionDetails(blogTopic, sectionTopics, request.session['audience'],
                                                      request.session['keywords'])
                # Create Database Record
                bloSec = BlogSection.objects.create(
                    title=val,
                    body=section,
                    blog=blog)
                bloSec.save()
                # # print(section)

        return redirect('view-generated-blog', slug=blog.slug)

    return render(request, 'home/select_blog_sections.html', context)

    # blog = Blog.objects.create(
    #     title=blogTopic,
    #     blogIdea=request.session['blogIdea'],
    #     keywords=request.session['keywords'],
    #     audience=request.session['audience'],
    #     profile=request.user.Profile, )
    # blog.save()


@login_required(login_url="/login/")
def genBlogFrmsvtopic(request, uniqueId):
    context = {}

    try:
        blog = Blog.objects.get(uniqueId=uniqueId)
    except:
        messages.error(request, "Blog not found")
        return redirect('home')

    blogSections = generatedBlogSectionTitles(blog.title, blog.audience, blog.keywords)

    if len(blogSections) > 0:
        # Adding the sections to the sessions
        request.session['blogSections'] = blogSections

        # Adding the sections to the context
        context['blogSections'] = blogSections
    else:
        messages.error(request, 'Oops something went wrong try again')
        return redirect('frm-gen-blogt')

    if request.method == 'POST':
        for val in request.POST:
            if not 'csrfmiddlewaretoken' in val:
                print(val)
                # Generating blogSection details
                sectionTopics = val
                section = generatedBlogSectionDetails(blog.title, sectionTopics, blog.audience, blog.keywords)
                # Create Database Record
                bloSec = BlogSection.objects.create(
                    title=val,
                    body=section,
                    blog=blog)
                bloSec.save()
                # # print(section)

        return redirect('view-generated-blog', slug=blog.slug)

    return render(request, 'home/select_blog_sections.html', context)

    # blog = Blog.objects.create(
    #     title=blogTopic,
    #     blogIdea=request.session['blogIdea'],
    #     keywords=request.session['keywords'],
    #     audience=request.session['audience'],
    #     profile=request.user.Profile, )
    # blog.save()


@login_required(login_url="/login/")
def viewGeneratedBlog(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
    except:
        messages.error(request, 'Oops something went wrong try again')
        return redirect('frm-gen-blogt')
    # Fetch the Created Sections for the Blog
    blogSections = BlogSection.objects.filter(blog=blog)

    context = {}
    context['blog'] = blog
    context['blogSections'] = blogSections

    return render(request, 'home/view-generated-blog.html', context)
