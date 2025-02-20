from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .models import Task, Profile
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import TaskForm 
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from django.db.models.signals import post_save
from django.dispatch import receiver


def home(request):
    tasks = Task.objects.filter(user=request.user).order_by("scheduled_date")
    # Filtering Logic
    filter_option = request.GET.get('filter')
    if filter_option == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_option == 'pending':
        tasks = tasks.filter(completed=False)

    # Sorting Logic
    sort_option = request.GET.get('sort')
    if sort_option == 'a_to_z':
        tasks = tasks.order_by('title')  # Sort alphabetically A-Z
    elif sort_option == 'z_to_a':
        tasks = tasks.order_by('-title')  # Sort alphabetically Z-A
    elif sort_option == 'newest':
        tasks = tasks.order_by('-created_at')  # Sort by newest first
    elif sort_option == 'oldest':
        tasks = tasks.order_by('created_at')  # Sort by oldest first
    return render(request, 'tasks1/home.html', {'tasks': tasks})

def welcomepage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Auto-login the user after successful login
            return redirect("home")  # Redirect to home page
        else:
            return render(request, 'tasks1/welcomepage.html', {"error": "Invalid username or password"})
    return render(request, 'tasks1/welcomepage.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmpassword = request.POST.get("confirmpassword")  # Make sure this matches HTML

        if password != confirmpassword:
            return render(request, "tasks1/register.html", {"error": "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, "tasks1/register.html", {"error": "Username already exists"})

        # ✅ FIXED: Create the user properly
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)  # Auto-login the user after registration
        return redirect("home")  # Redirect to home page

    return render(request, "tasks1/register.html")


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect("home")

def completedtasks(request):
    completedtasks = Task.objects.filter(completed=True, user=request.user)

    return render(request, "tasks1/completedtasks.html", {"completedtasks": completedtasks})

def appsettings(request):
    return render(request, "tasks1/appsettings.html")
def add_task(request):
    if request.method == "POST":
        title = request.POST.get("task_title")
        description = request.POST.get("description")  # Get description from form
        start_date = request.POST.get("Start_Date")
        start_time = request.POST.get("Start_Time")
        reminder = request.POST.get("reminder")

        # Ensure description is provided
        if not description:
            return render(request, "tasks1/add_task.html", {"error": "Description is required"})

        # Process date and time
        if start_date and start_time:
            scheduled_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        else:
            scheduled_datetime = None  

        # Create and save the task
        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,  # Ensure description is saved
            scheduled_date=scheduled_datetime,
            reminder=reminder if reminder else None,  
        )
        return redirect("home")  

    return render(request, "tasks1/add_task.html")
           
@csrf_exempt
def update_task_status(request, task_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task = Task.objects.get(id=task_id, user=request.user) 
            task.completed = data.get("completed", False)
            task.save()
            return JsonResponse({"success": True})  
        except Task.DoesNotExist:
            return JsonResponse({"success": False, "error": "Task not found"}, status=404)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)
        
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    return render(request, "tasks1/task_detail.html", {"task": task})        
        
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task) 
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = TaskForm(instance=task)
    
    return render(request, "tasks1/edit_task.html", {"form": form})      
        
        
        
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == "POST":
        task.delete()
        return redirect("home")
    
    return render(request, "tasks/delete_task.html", {"task": task})


@login_required
def profile(request):
    # Ensure user has a profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")  # Reload page after saving
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, "tasks1/profile.html", {"form": form})

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


def user_logout(request):
    logout(request)  # Logs out the user
    return redirect('welcomepage')  # Redirects to the welcome page

def search_tasks(request):
    query = request.GET.get('q', '')
    tasks = Task.objects.filter(user=request.user, title__icontains=query)  # Case-insensitive search

    task_list = [{'id': task.id, 'title': task.title, 'completed': task.completed} for task in tasks]

    return JsonResponse({'tasks': task_list})