from django.db import models
from django.contrib.auth.models import User

class Manager(models.Model):
    """
    Represents a user with a managerial role (e.g., Admin, Team Leader, Manager).
    Linked to a User instance with additional attributes like department and title.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    department = models.CharField(max_length=100, blank=True, help_text="The department managed by this user")
    title = models.CharField(max_length=100, default='Manager', help_text="The managerial title (e.g., Team Lead, Manager)")

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Employee(models.Model):
    """
    Represents an employee (non-manager user) with a link to the User model.
    Used for task assignments to distinguish employees from managers.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_account')
    employee_id = models.CharField(max_length=50, unique=True, blank=True, help_text="Unique ID for the employee")
    joining_date = models.DateField(null=True, blank=True, help_text="The date the employee joined")

    def __str__(self):
        return f"{self.user.username} - Employee"

class EmployeeProfile(models.Model):
    """
    Represents an employee’s profile and their relationship to a manager.
    Now linked to the Employee model instead of User directly.
    """
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates',
                               help_text="The manager overseeing this employee")

    def __str__(self):
        return self.employee.user.username

class Task(models.Model):
    """
    Represents a task with details like title, description, priority, dates, and type.
    """
    TASK_PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]
    TASK_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team')
    ]

    task_id = models.AutoField(primary_key=True)
    task_title = models.CharField(max_length=100, help_text="The title of the task")
    task_description = models.CharField(max_length=300, help_text="A brief description of the task")
    task_priority = models.CharField(max_length=200, choices=TASK_PRIORITY_CHOICES, default='Medium',
                                    help_text="The priority level of the task")
    start_date = models.DateField(help_text="The start date of the task")
    end_date = models.DateField(help_text="The end date of the task")
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES, default='Individual',
                                help_text="The type of task (Individual or Team)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date the task was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date the task was last updated")

    def __str__(self):
        return self.task_title

class TaskAssignment(models.Model):
    """
    Represents the assignment of a task to an employee by a user.
    Now uses the Employee model for the employee field.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]

    assignment_id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments',
                            help_text="The task being assigned")
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tasks',
                                help_text="The employee to whom the task is assigned")
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned',
                                   help_text="The user who assigned the task")
    assigned_date = models.DateTimeField(auto_now_add=True, help_text="The date the task was assigned")
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending',
                             help_text="The current status of the task")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="The date the task was completed")

    def __str__(self):
        return f"{self.task.task_title} - {self.employee.user.username}"