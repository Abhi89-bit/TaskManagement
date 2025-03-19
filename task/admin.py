from django.contrib import admin
from .models import Task, TaskAssignment, EmployeeProfile, Manager, Employee

# Register all models
admin.site.register(Task)
admin.site.register(TaskAssignment)
admin.site.register(EmployeeProfile)
admin.site.register(Manager)
admin.site.register(Employee)