from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Task
from django.utils import timezone
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import TaskForm 


def home(request):
    tasks = Task.objects.filter(user=request.user).order_by("scheduled_date")
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

def settings(request):
    return render(request, "tasks1/settings.html")
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
