from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.
class MyUser(AbstractUser):
    role = models.CharField(max_length=50,null=True)
    created_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    

    groups = models.ManyToManyField(
        Group,
        related_name='myuser_set',  
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='myuser_permissions',  
        blank=True
    )
    class Meta:
        db_table_comment = "User Details" 
        

class Project(models.Model):
    project_id = models.AutoField(primary_key=True)  
    project_name = models.CharField(max_length=255)  
    project_description = models.TextField()         
    last_date = models.DateField()   
    created_date = models.DateField(auto_now_add=True) 
    assigned_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='project_assigned')                   

    class Meta:
        db_table_comment = "Project Details"  

    def __str__(self):
        return self.project_id


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)  
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    task_description = models.TextField()
    task_last_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='tasks_created')
    assigned_to = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='tasks_assigned')
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='not_started')

    is_high_priority = models.BooleanField(default=False)
    
    class Meta:
        db_table_comment = "Task Details" 

    def __str__(self):
        return self.task_id   
    
class WorkLog(models.Model):
    work_log_id = models.AutoField(primary_key=True)  
    work_log_time = models.IntegerField() 
    work_log_description = models.TextField()         
    created_date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True, blank=True)                    

    class Meta:
        db_table_comment = "Work Log Details"  

    def __str__(self):
        return self.work_log_id
    
class TaskReport(models.Model):
    taskreport_id = models.AutoField(primary_key=True) 
    task = models.ForeignKey(Task, on_delete=models.CASCADE)  
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)  
    report_date = models.DateTimeField(auto_now_add=True)  
    report_file = models.FileField(upload_to='task_reports/', blank=True, null=True) 
    
    class Meta:
        db_table_comment = "Task Report File"  

    def __str__(self):
        return  self.taskreport_id