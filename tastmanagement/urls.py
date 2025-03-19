from django.contrib import admin
from django.urls import path, include
from task import views
from task.views import task_detail

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),  
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_task, name='create_task'),
    path('update/<int:assignment_id>/', views.update_task, name='update_task'),
    path('delete/<int:assignment_id>/', views.delete_task, name='delete_task'),
    path('task/<int:assignment_id>/', views.task_detail, name='task_detail'),
]
