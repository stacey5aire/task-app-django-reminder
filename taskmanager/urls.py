
from django.shortcuts import get_object_or_404
from django.urls import path
from tasks.models import Task
from tasks.views import register, home, welcomepage, delete_task, completedtasks, appsettings, add_task,search_tasks, update_task_status, task_detail, profile, user_logout 
from django.contrib.auth import views as auth_views
from tasks import views
from django.conf.urls.static import static
from django.conf import settings 
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path("", welcomepage, name="welcomepage"),
    path("register/", register, name="register"),
    path("home/",home, name="home"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path("delete_task/<int:task_id>/", delete_task, name="delete_task"),
    path("completedtasks/", completedtasks, name="completedtasks"),
    path("appsettings/", appsettings, name="appsettings"),
    path("add_task/", add_task, name="add_task"),
    path("update_task_status/<int:task_id>/", update_task_status, name="update_task_status"),
    path("task/<int:task_id>/", views.task_detail, name="task_detail"),
    path("edit/<int:task_id>/", views.edit_task, name="edit_task"),
    path("delete/<int:task_id>/", views.delete_task, name="delete_task"),
    path("profile/", profile, name="profile"),
    path('logout/', user_logout, name='logout'),
    path('search-tasks/', search_tasks, name='search_tasks'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


