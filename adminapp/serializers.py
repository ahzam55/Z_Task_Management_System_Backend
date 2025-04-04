from rest_framework import serializers
from adminapp.models import *

class MyUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MyUser
        fields = ['username', 'email','role','id']
        
class ProjectSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = Project
        fields = ['project_id','project_name', 'project_description','last_date','username']
        
class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)  
    username = serializers.CharField(source='assigned_to.username', read_only=True)
    created_username = serializers.CharField(source='created_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)  
    
    class Meta:
        model = Task
        fields = ['task_id','created_username','status_display','project_id','task_name', 'task_description','task_last_date', 'assigned_to','status','is_high_priority', 'project_name', 'username']

class WorkLogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WorkLog
        fields = ['work_log_id','work_log_time', 'work_log_description','created_date']
        
class TaskReportSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)  
    
    class Meta:
        model = TaskReport
        fields = ['taskreport_id', 'task', 'user', 'report_date', 'report_file', 'task_name', 'username']

        