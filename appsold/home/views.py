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


def assign_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        department = request.POST.get('department')
        assigned_to = request.POST.get('assigned_to')
        print('this is the user Id of assigned to ' + assigned_to)

        if not task_id or not department:
            return JsonResponse({'success': False, 'message': 'Task ID and Department are required'})

        # Get the task
        try:
            task = Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Task not found'})

        # Check if the task is pending
        if task.status != 'pending':
            return JsonResponse({'success': False, 'message': 'Only pending tasks can be assigned'})

        # Get all personnel in the department and their task counts
        personnel_in_department = Profile1.objects.filter(department=department, user_type='personnel')
        personnel_counts = TaskAssignmentCount.objects.filter(personnel__profile1__in=personnel_in_department)

        # Find personnel with the minimum task count within the selected department
        min_task_count = personnel_counts.aggregate(Min('task_count'))['task_count__min']
        eligible_personnel = personnel_counts.filter(task_count=min_task_count)

        # if not eligible_personnel.exists():
        #     return JsonResponse({'success': False, 'message': 'No eligible personnel found in the selected department'})

        # If all personnel have the same count, return all personnel for manual selection
        if assigned_to:
            try:
                # assigned_personnel = Profile1.objects.get(assigned_to)
                # assigned_personnel = Profile1.objects.get(uniqueId=assigned_to)
                assigned_profile = Profile1.objects.get(uniqueId=assigned_to)
                assigned_user = assigned_profile.username
                assigned_personnel = User.objects.get(username=assigned_user)            

            except (ValueError, ObjectDoesNotExist):
                return JsonResponse({'success': False, 'message': 'Invalid user ID'})
        else:
            eligible_personnel_list = eligible_personnel.values('personnel__id', 'personnel__first_name', 'personnel__last_name')
            return JsonResponse({'success': False, 'message': 'All eligible personnel have the same task count. Please select one manually.', 'personnel': list(eligible_personnel_list)})

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

    print('this is the user at the dashboard_view :'+ str(department))

    if department == 'auditing':
        user = request.user
        tasks = Task.objects.filter(assigned_personnel=user)
        assigned_recurring_tasks = RecurringTask.objects.filter(assigned_personnel=user_profile)
        print(f"Assigned recurring tasks for {user.username}: {assigned_recurring_tasks}")
        return render(request, "home/adt_dashboard.html", {
            "user_tasks": tasks,
            "assigned_recurring_tasks": assigned_recurring_tasks
        })
    
    elif department == 'bookkeeping':
        user = request.user
        tasks = Task.objects.filter(assigned_personnel=user)
        assigned_recurring_tasks = RecurringTask.objects.filter(assigned_personnel=user_profile)
        print(f"Assigned recurring tasks for {user.username}: {assigned_recurring_tasks}")
        return render(request, "home/bk_dashboard.html", {
            "user_tasks": tasks,
            "assigned_recurring_tasks": assigned_recurring_tasks
        })
    
    elif user_type == 'supervisor':
        tasks_pending = Task.objects.filter(status='pending')
        tasks_in_progress = Task.objects.filter(status='in_progress')
        tasks_completed = Task.objects.filter(status='completed')
        all_recurring_tasks = RecurringTask.objects.all()

        return render(request, "home/supervisor.html", {
            "tasks_pending": tasks_pending,
            "tasks_in_progress": tasks_in_progress,
            "tasks_completed": tasks_completed,
            "all_recurring_tasks": all_recurring_tasks
        })
    else:
        return redirect('home')  # Or some default view 

@login_required
def auditing_dashboard(request):
    user = request.user
    tasks = Task.objects.filter(assigned_personnel=user)
    
    try:
        personnel_profile = Profile1.objects.get(user=user)
        assigned_recurring_tasks = RecurringTask.objects.filter(assigned_personnel=personnel_profile)
        print(f"Assigned recurring tasks for {user.username}: {assigned_recurring_tasks}")
    except Profile1.DoesNotExist:
        assigned_recurring_tasks = None
        print(f"No profile found for username: {user.username}")

    return render(request, "home/adt_dashboard.html", {
        "user_tasks": tasks,
        "assigned_recurring_tasks": assigned_recurring_tasks,
    })

@login_required
def bookkeeping_dashboard(request):
    user = request.user
    tasks = Task.objects.filter(assigned_personnel=user)

    try:
        personnel_profile = Profile1.objects.get(user=user)
        assigned_recurring_tasks = RecurringTask.objects.filter(assigned_personnel=personnel_profile)
        print(f"Assigned recurring tasks for {user.username}: {assigned_recurring_tasks}")
    except Profile1.DoesNotExist:
        assigned_recurring_tasks = None
        print(f"No profile found for username: {user.username}")

    return render(request, "home/bk_dashboard.html", {
        "user_tasks": tasks,
        "assigned_recurring_tasks": assigned_recurring_tasks,
    })

@login_required
def supervisor_dashboard(request):
    tasks_pending = Task.objects.filter(status='pending')
    tasks_in_progress = Task.objects.filter(status='in_progress')
    tasks_completed = Task.objects.filter(status='completed')

    # Get clients with recurring tasks
    clients_with_recurring_tasks = Profile1.objects.filter(recurring_tasks__isnull=False).distinct()

    return render(request, "home/supervisor.html", {
        "tasks_pending": tasks_pending,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "clients_with_recurring_tasks": clients_with_recurring_tasks,
    })

@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    user_profile = Profile1.objects.get(user=request.user)
    
    if request.method == 'POST':
        if 'update_task' in request.POST:
            task.remarks = request.POST.get('remarks', '')
            task.save()
            return redirect('task_detail', task_id=task_id)
        elif 'mark_completed' in request.POST:
            task.status = 'completed'
            task.save()
            return redirect('task_detail', task_id=task_id)
        elif 'mark_approved' in request.POST and user_profile.user_type == 'supervisor':
            task.approved = True
            task.save()
            return redirect('task_detail', task_id=task_id)
        elif 'download_file' in request.POST:
            file_path = task.file.path
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename={task.file.name}'
                return response

    return render(request, 'home/task_detail.html', {
        'task': task,
        'user_profile': user_profile
    })

@login_required
def fetch_tasks_by_type(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'tasks': []})

    try:
        profile = Profile1.objects.get(user=user)
        user_type = profile.user_type
        department = profile.department
    except Profile1.DoesNotExist:
        return JsonResponse({'tasks': []})

    print(f"User type: {user_type}, Department: {department}")

    # Fetch tasks assigned to the current user based on their user_type and department
    tasks = Task.objects.filter(assigned_personnel=user, assigned_personnel__profile1__user_type=user_type, assigned_personnel__profile1__department=department)
    if not tasks.exists():
        print("No tasks found for the user")
        return JsonResponse({'tasks': []})

    task_data = [{'task_name': task.task_name, 'task_id': task.task_id} for task in tasks]
    return JsonResponse({'tasks': task_data})

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

            create_task_directories(recurring_task)

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

def update_recurring_task(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')

        task_update = TaskUpdate.objects.create(
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
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def recurring_task_detail(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    return render(request, 'home/recurrent_task_detail.html', {
        'task': task,
        'months': months,
    })

def client_recurring_tasks(request, client_username):
    client_profile = get_object_or_404(Profile1, user__username=client_username)
    recurring_tasks = RecurringTask.objects.filter(client=client_profile)

    return render(request, 'home/client_recurring_tasks.html', {
        'client': client_profile,
        'recurring_tasks': recurring_tasks,
    })

def create_task_directories(task):
    print('The Create Task Directories function has been reached')
    task_path = os.path.join(settings.MEDIA_ROOT, 'recurrent_task_files', str(task.client.id), task.task_name)
    
    start_date = task.start_date  # Use the already converted date object
    print(f'Converted start_date: {start_date}')

    if task.interval == 'monthly':
        for month in range(1, 13):
            month_name = date(1900, month, 1).strftime('%B')
            month_path = os.path.join(task_path, month_name)
            print(f'Creating directory: {month_path}')
            os.makedirs(month_path, exist_ok=True)
            
            TaskDirectory.objects.create(
                task=task,
                client=task.client,
                year=start_date.year,
                month=month_name,
                path=month_path
            )
    elif task.interval == 'yearly':
        print(f'Creating directory: {task_path}')
        os.makedirs(task_path, exist_ok=True)
        
        TaskDirectory.objects.create(
            task=task,
            client=task.client,
            year=start_date.year,
            path=task_path
        )

    print('Directory creation process completed')


@login_required
def recurring_task_detail(request, task_id):
    task = get_object_or_404(RecurringTask, id=task_id)
    
    # Logic to generate six years back
    current_year = date.today().year
    six_years_back = list(range(current_year, current_year - 6, -1))
    
    # Ensure directory structure is created
    for year in six_years_back:
        for month in range(1, 13):
            month_name = date(1900, month, 1).strftime('%B')
            task_path = os.path.join(settings.MEDIA_ROOT, 'recurrent_task_files', str(task.client.id), str(year), month_name, task.task_name)
            os.makedirs(task_path, exist_ok=True)
    
    # List of month names
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    return render(request, 'home/recurrent_task_detail.html', {
        'task': task,
        'six_years_back': six_years_back,
        'months': months,
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

def personnel_recurring_task_detail(request, pk):
    task = get_object_or_404(RecurringTask, pk=pk)
    return render(request, 'home/personnel_recurring_task_detail.html', {'task': task})

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
