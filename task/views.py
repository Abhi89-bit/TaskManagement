from django.shortcuts import render, redirect, get_object_or_404
from .models import Task  # Assuming Task is the model name
from django.contrib.auth.decorators import login_required
from .models import Task, TaskAssignment, EmployeeProfile, Manager, Employee
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from .models import Task


@login_required
def task_detail(request, assignment_id):
    task = get_object_or_404(Task, task_id=assignment_id)  # Use task_id instead of id
    return render(request, 'task_detail.html', {'task': task})


@login_required
def dashboard(request):

    # Handle marking a task as completed
    if request.method == "POST" and 'mark_completed' in request.POST:
        assignment_id = request.POST.get('assignment_id')
        assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)
        if assignment.employee.user == request.user or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():
            assignment.status = 'Completed'
            assignment.completed_at = timezone.now()
            assignment.save()
            messages.success(request, f"Task '{assignment.task.task_title}' marked as completed.")

    # Task filtering based on user role
    if request.user.is_superuser:  # Admins see all tasks
        tasks = TaskAssignment.objects.all()
    elif request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():  # Team Leaders/Managers see their assigned tasks or tasks assigned to them
        tasks = TaskAssignment.objects.filter(assigned_by=request.user) | TaskAssignment.objects.filter(employee__user=request.user)
    else:  # Employees see only tasks assigned to them
        tasks = TaskAssignment.objects.filter(employee__user=request.user)

    # Apply filters
    employee_filter = request.GET.get('employee')
    status_filter = request.GET.get('status')
    start_date_from = request.GET.get('start_date_from')
    start_date_to = request.GET.get('start_date_to')

    if employee_filter and request.user.is_superuser:  # Admin-only filter
        tasks = tasks.filter(employee__user__username=employee_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if start_date_from and start_date_to:
        tasks = tasks.filter(task__start_date__range=[start_date_from, start_date_to])

    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_tasks = tasks.count()
    completed = tasks.filter(status='Completed').count()
    pending = tasks.filter(status='Pending').count()
    in_progress = tasks.filter(status='In Progress').count()

    # Employees for filter (admin-only)
    employees = User.objects.filter(employee_account__isnull=False).exclude(id=request.user.id) if request.user.is_superuser else []

    context = {
        'page_obj': page_obj,
        'stats': {'total': total_tasks, 'completed': completed, 'pending': pending, 'in_progress': in_progress},
        'employees': employees,
        'is_admin': request.user.is_superuser,
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_task(request):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to create tasks.")
        return redirect('task:dashboard')

    if request.method == 'POST':
        try:
            task = Task.objects.create(
                task_title=request.POST['task_title'],
                task_description=request.POST['task_description'],
                task_priority=request.POST['task_priority'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                task_type=request.POST['task_type'],
            )
            employee = Employee.objects.get(user__username=request.POST['assigned_to'])
            TaskAssignment.objects.create(
                task=task,
                employee=employee,
                assigned_by=request.user,
            )
            messages.success(request, 'Task created successfully!')
            return redirect('task:dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
        except Exception as e:
            messages.error(request, f'Error creating task: {str(e)}')

    if request.user.is_superuser:
        employees = Employee.objects.all().values_list('user__username', flat=True)
    else:
        employees = Employee.objects.filter(
            profile_manager_user=request.user
        ).values_list('user__username', flat=True)

    return render(request, 'create_task.html', {'employees': employees})

@login_required
def update_task(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)

    # Restrict updates to the assigned_by user, Admin, or authorized roles
    if not (request.user == assignment.assigned_by or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to update this task.")
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            assignment.task.task_title = request.POST['task_title']
            assignment.task.task_description = request.POST['task_description']
            assignment.task.task_priority = request.POST['task_priority']
            assignment.task.start_date = request.POST['start_date']
            assignment.task.end_date = request.POST['end_date']
            assignment.task.task_type = request.POST['task_type']
            assignment.employee = Employee.objects.get(user__username=request.POST['assigned_to'])
            assignment.status = request.POST['status']
            assignment.task.save()
            assignment.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('dashboard')
        except Employee.DoesNotExist:
            messages.error(request, 'Selected employee does not exist.')
        except Exception as e:
            messages.error(request, f'Error updating task: {str(e)}')

    # Fetch Employee objects for the dropdown
    if request.user.is_superuser:
        employees = Employee.objects.all()  # Admins see all employees
    elif request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists():
        employees = Employee.objects.filter(profile_manager_user=request.user)  # Employees under this manager
    else:
        employees = []  # Regular employees can't reassign tasks

    context = {
        'assignment': assignment,
        'employees': employees,
    }
    return render(request, 'update_task.html', context)
@login_required
def delete_task(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, assignment_id=assignment_id)  # Correctly refer to TaskAssignment

    # Restrict deletion to the assigned_by user, Admin, or authorized roles
    if not (request.user == assignment.assigned_by or request.user.is_superuser or request.user.groups.filter(name__in=['TeamLeader', 'Manager']).exists()):
        messages.error(request, "You do not have permission to delete this task.")
        return redirect('dashboard')

    if request.method == 'POST':
        assignment.task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('dashboard')
    return render(request, 'delete_task.html', {'assignment': assignment})