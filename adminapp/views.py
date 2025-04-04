from django.shortcuts import render
from django.contrib.auth import authenticate, login 
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from adminapp.serializers import *
from adminapp.models import *
import jwt, datetime
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from rest_framework.decorators import api_view
import os
# Create your views here.
SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 20  # 1 minute
ACCESS_TOKEN_EXPIRATION = 90  # 1 minute

@csrf_exempt
def Signin(request):
    if request.method == "POST":
        try:
             # parse the incoming JSON data
            user_data = JSONParser().parse(request)
            username = user_data.get('username')
            password = user_data.get('password')
            
            # checking  username and password  is provided
            if not username or not password:
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 400,
                    "message": "Username and password are required.",
                    "debugMessage": "Username or password not provided."
                })

            user = authenticate(request, username=username, password=password)
            
            # checking user is valid
            if user is not None:
                request.session['user_id'] = user.id

                try:
                    login_obj = MyUser.objects.get(username=username)

                    # checking  where user is employee  then check worklog  time is less than 8 hours
                    if login_obj.role == "employee":
                        current_date = datetime.date.today()

                        existing_work_logs = WorkLog.objects.filter(created_by=user, created_date=current_date)

                        total_work_log_time = sum(log.work_log_time for log in existing_work_logs)

                      
                        new_work_log_time = user_data.get('work_log_time', 0)

                        if total_work_log_time + new_work_log_time >= 8:
                            response_data = {
                                "hasError": True,
                                "errorCode": 400,
                                "message": "Cannot log more than 8 hours in a day.",
                                "debugMessage": f"Total work log time today: {total_work_log_time} hours."
                            }
                            response_data['redirect'] = 'signin' 
                            return JsonResponse(response_data, status=400)

                    access_token_payload = {
                        'id': user.id,
                        'role': login_obj.role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION),
                        'iat': datetime.datetime.utcnow()
                    }
                    access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

                    refresh_token_payload = {
                        'id': user.id,
                        'role': login_obj.role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRATION),
                        'iat': datetime.datetime.utcnow()
                    }
                    refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')

                    response_data = {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': user.id
                    }

                    if login_obj.role == "admin":
                        login(request, user)
                        response_data['redirect'] = 'adminhome'
                    elif login_obj.role == "manager":
                        login(request, user)
                        response_data['redirect'] = 'managerhome'
                    elif login_obj.role == "employee":
                        login(request, user)
                        response_data['redirect'] = 'userhome'
                    else:
                        return JsonResponse({
                            "hasError": True,
                            "errorCode": 400,
                            "message": "Invalid role",
                            "debugMessage": ""
                        })

                    response = JsonResponse({
                        "hasError": False,
                        "errorCode": 0,
                        "message": "Success",
                        "debugMessage": "",
                        "data": response_data
                    })

                    response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True)
                    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True)

                    return response

                except MyUser.DoesNotExist:
                    return JsonResponse({
                        "hasError": True,
                        "errorCode": 404,
                        "message": "User does not exist",
                        "debugMessage": ""
                    })

            else:
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 400,
                    "message": "Incorrect username or password.",
                    "debugMessage": ""
                })

        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "An unexpected error occurred.",
                "debugMessage": str(e)
            })

    return JsonResponse({
        "hasError": True,
        "errorCode": 400,
        "message": "Invalid request",
        "debugMessage": ""
    })

    
    
SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 90  # 1 minute
ACCESS_TOKEN_EXPIRATION = 10  # 1 minute

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh_token', None)

   
    if not refresh_token:
       
        return JsonResponse({"error": "Refresh token is required"}, status=400)

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=["HS256"])

        user_id = payload['id']
        user = MyUser.objects.get(id=user_id)
      

        access_token_payload = {
            'id': user.id,
            'role': user.role,  
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRATION),
            'iat': datetime.datetime.utcnow()
        }

       
        access_token = jwt.encode(access_token_payload, SECRET_KEY, algorithm='HS256')

        refresh_token_payload = {
            'id': user.id,
            'role': user.role ,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRATION),
            'iat': datetime.datetime.utcnow()
        }

        refresh_token = jwt.encode(refresh_token_payload, SECRET_KEY, algorithm='HS256')
        print(10)
        print(refresh_token)
      
        return JsonResponse({
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Refresh token has expired"}, status=400)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid refresh token"}, status=400)
    except MyUser.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)



    
@csrf_exempt
def Manager(request):
    # GET data of manager
    if request.method == "GET":
        myuser = MyUser.objects.filter(role='manager')
        myuser_serializer = MyUserSerializer(myuser, many=True)

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": myuser_serializer.data
        })

    # POST  to insert data of manager
    elif request.method == "POST":
        
         # parse the incoming JSON data
        user_data = JSONParser().parse(request)
        print(user_data)
        user_id = getattr(request, 'user_id', None)
        print(user_id) 

        
        password = user_data.get('password')
        username = user_data.get('username')
        email = user_data.get('email')
        role = user_data.get('role')
        createdById = user_id

        # checking whether password,username,email and role is provided
        if not (password and username and email and role ):
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Failed to Register",
                "debugMessage": "Missing required fields"
            }, status=400)

        try:
          
            reg_login = MyUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                created_by_id=createdById,
                role=role
            )

            
            reg_login.save()

            return JsonResponse({
                "hasError": False,
                "errorCode": 0,
                "message": "Manager registration successful",
                "debugMessage": ""
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "Failed to Register",
                "debugMessage": str(e)
            }, status=500)


    return JsonResponse({
        "hasError": True,
        "errorCode": 405,
        "message": "Invalid request method",
        "debugMessage": "Only GET and POST methods are allowed"
    }, status=405)
    
@csrf_exempt
def Employee(request):
    # GET data of employee
    if request.method == "GET":
        try:
            myuser = MyUser.objects.filter(role='employee')
            myuser_serializer = MyUserSerializer(myuser, many=True)
            return JsonResponse({
                "hasError": False,
                "errorCode": 0,
                "message": "Success",
                "debugMessage": "",
                "data": myuser_serializer.data
            })
        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "Internal Server Error",
                "debugMessage": str(e)
            })
            
    
    # POST  to insert data of employee
    elif request.method == "POST":
        try:
             # parse the incoming JSON data
            user_data = JSONParser().parse(request)
            user_id = getattr(request, 'user_id', None)

            password = user_data.get('password')
            username = user_data.get('username')
            email = user_data.get('email')
            role = user_data.get('role')
            createdById = user_id

            # checking whether password,username,email and role is provided
            if not (password and username and email and role ):
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 400,
                    "message": "Missing required fields",
                    "debugMessage": "Please provide all required fields"
                }, status=400)

            reg_login = MyUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                created_by_id=createdById,
                role=role
            )
            reg_login.save()

            return JsonResponse({
                "hasError": False,
                "errorCode": 0,
                "message": "Employee registration successful",
                "debugMessage": ""
            }, status=201)

        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "Internal Server Error",
                "debugMessage": str(e)
            }, status=500)

    return JsonResponse({
        "hasError": True,
        "errorCode": 405,
        "message": "Invalid request method",
        "debugMessage": "Only GET and POST methods are allowed"
    }, status=405)
    
    
@csrf_exempt
def Project_Registration(request, id=None):
    # GET data of project 
    if request.method == 'GET':
        project = Project.objects.all()
        project_serializer = ProjectSerializer(project, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": project_serializer.data 
        }, safe=False)

    # POST  to insert data of project
    elif request.method == 'POST':
        project_data = JSONParser().parse(request)
        print(project_data)  

        project_name = project_data.get('project_name')
        project_description = project_data.get('project_description')
        last_date = project_data.get('last_date')
        
        
         # checking whether project_name,project_description and last_date is provided
        if not project_name or not project_description or not last_date :
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Missing required fields",
                "debugMessage": "project_name, project_description and last_date are required"
            }, status=400)

        reg_project = Project()
        reg_project.project_name = project_name
        reg_project.project_description = project_description
        reg_project.last_date = last_date
        reg_project.created_date = date.today()

        reg_project.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Project Added Successfully",
            "debugMessage": ""
        }, safe=False)

     # PUT  to update data of project
    elif request.method == 'PUT':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Project ID is required",
                "debugMessage": "Please provide a valid Project ID"
            }, status=400)

        try:
            project = Project.objects.get(project_id=id)
        except Project.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Project not found",
                "debugMessage": f"No Project found with ID {id}"
            }, status=404)

        project_data = JSONParser().parse(request)
        print(project_data)  

        project_name = project_data.get('project_name')
        project_description = project_data.get('project_description')
        last_date = project_data.get('last_date')
        

        if project_name:
            project.project_name = project_name
        if project_description:
            project.project_description = project_description
        if last_date:
            project.last_date = last_date

        project.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Project Updated Successfully",
            "debugMessage": ""
        }, safe=False)

     # DELETE  to delete  data of a project
    elif request.method == 'DELETE':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Project ID is required",
                "debugMessage": "Please provide a valid Project ID"
            }, status=400)

        try:
            print(id)
            project = Project.objects.get(project_id=id)
        except Project.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Project not found",
                "debugMessage": f"No task found with ID {id}"
            }, status=404)

        project.delete()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Project Deleted Successfully",
            "debugMessage": ""
        }, safe=False)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Invalid request method",
            "debugMessage": "Only GET, POST, PUT, and DELETE methods are allowed"
        }, status=405)
        
@csrf_exempt
def Task_Registration(request, id=None): 
     # GET data of task 
    if request.method == 'GET':
        task = Task.objects.filter(assigned_to__isnull=True)
        task_serializer = TaskSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_serializer.data 
        }, safe=False)

     # POST  to insert data of task
    elif request.method == 'POST':
        task_data = JSONParser().parse(request)
        print(task_data)  
        user_id = getattr(request, 'user_id', None)
        

        project_name = task_data.get('project_name')
        task_name = task_data.get('task_name')
        task_description = task_data.get('task_description')
        is_high_priority = task_data.get('is_high_priority')
        last_date = task_data.get('last_date')
        
        
        # checking whether project_name,task_name,task_description,is_high_priority and last_date is provided
        if not project_name or not task_name or not task_description or not is_high_priority or not last_date :
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Missing required fields",
                "debugMessage": "project_name, task_name,task_description, is_high_priority and last_date are required"
            }, status=400)

        reg_task = Task()
        reg_task.project = Project.objects.get(project_id=project_name)
        reg_task.task_name = task_name
        reg_task.task_description = task_description
        reg_task.task_last_date = last_date
        reg_task.created_at =  date.today()
        reg_task.updated_at =  date.today()
        reg_task.created_by = MyUser.objects.get(id=user_id)
        reg_task.is_high_priority = is_high_priority

        reg_task.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task Added Successfully",
            "debugMessage": ""
        }, safe=False)

     # PUT  to update data of task
    elif request.method == 'PUT':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Task ID is required",
                "debugMessage": "Please provide a valid Task ID"
            }, status=400)

        try:
            task = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Task not found",
                "debugMessage": f"No Task found with ID {id}"
            }, status=404)

         # parse the incoming JSON data
        task_data = JSONParser().parse(request)
        print(task_data)

        project_name = task_data.get('project_name')
        task_name = task_data.get('task_name')
        task_description = task_data.get('task_description')
        is_high_priority = task_data.get('is_high_priority')
        last_date = task_data.get('last_date')
        user_id = getattr(request, 'user_id', None)
        print(is_high_priority)

        if project_name:
            task.project = Project.objects.get(project_id=project_name)
        if task_name:
            task.task_name = task_name
        if task_description:
            print(task_description)
            task.task_description = task_description
        if last_date:
            task.task_last_date = last_date
            task.updated_at =  date.today()
        if user_id:
            task.created_by = MyUser.objects.get(id=user_id)
            
        task.is_high_priority = is_high_priority

        task.save()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task Updated Successfully",
            "debugMessage": ""
        }, safe=False)
        
    
    # DELETE  to delete  data of a task
    elif request.method == 'DELETE':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Task ID is required",
                "debugMessage": "Please provide a valid Task ID"
            }, status=400)

        try:
            print(id)
            task = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Task not found",
                "debugMessage": f"No Task found with ID {id}"
            }, status=404)

        task.delete()
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task Deleted Successfully",
            "debugMessage": ""
        }, safe=False)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Invalid request method",
            "debugMessage": "Only GET, POST, PUT, and DELETE methods are allowed"
        }, status=405)
        
        
@csrf_exempt
def All_Employee(request, id=None): 
     # GET data of  all employee
    if request.method == 'GET':
        user = MyUser.objects.filter(role="employee")
        myuser_serializer = MyUserSerializer(user, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": myuser_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Task_Assign(request, id):
     # PUT  to update data of assigned_to in task 
    if request.method == 'PUT':
        if id is None:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Task ID is required",
                "debugMessage": "Please provide a valid Task ID"
            }, status=400)
        try:
            task = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Task not found",
                "debugMessage": f"No Task found with ID {id}"
            }, status=404)
        task_data = JSONParser().parse(request)
        print(task_data)

        assigned_to = task_data.get('assigned_to')
        is_high_priority = task_data.get('is_high_priority')

        if assigned_to:
            try:
                user = MyUser.objects.get(id=assigned_to)
            except MyUser.DoesNotExist:
                return JsonResponse({
                    "hasError": True,
                    "errorCode": 400,
                    "message": "Invalid assigned_to ID",
                    "debugMessage": "No user found with this ID"
                }, status=400)
            # checking whether the user only have less than 3 high priority task
            if is_high_priority:
                high_priority_count = Task.objects.filter(assigned_to=user, is_high_priority=True).count()
                print(high_priority_count)

                if high_priority_count >= 3:
                    return JsonResponse({
                        "hasError": True,
                        "errorCode": 400,
                        "message": "User already has 3 high-priority tasks",
                        "debugMessage": ""
                    }, status=400)

            # assign task to the user
            task.assigned_to = user

        # update the is_high_priority field if it exists in the request
        if is_high_priority is not None:
            task.is_high_priority = is_high_priority

        # Save the task with the updated data
        task.save()

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task Assigned Successfully",
            "debugMessage": ""
        }, safe=False)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Method Not Allowed",
            "debugMessage": "Only PUT method is allowed"
        }, status=405)
        
@csrf_exempt
def Task_Without_Assign(request): 
     # GET data of task without assign
    if request.method == 'GET':
        task = Task.objects.filter(assigned_to__isnull=True)
        task_serializer = TaskSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_serializer.data 
        }, safe=False)
        
        
@csrf_exempt
def Task_With_Assign(request): 
     # GET data of task with assign
    if request.method == 'GET':
        task = Task.objects.filter(assigned_to__isnull=False)
        task_serializer = TaskSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_serializer.data 
        }, safe=False)
        
@csrf_exempt
def User_Task(request): 
     # GET data of task of the user
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)
        print(user_id) 

        task = Task.objects.filter(assigned_to=user_id)
        task_serializer = TaskSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Status_Update(request, id):
     # PUT  to update data of status in task 
    if request.method == 'PUT':
        try:
            task = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Task not found",
                "debugMessage": f"No Task found with ID {id}"
            }, status=404)
        
        # parse the incoming JSON data
        task_data = JSONParser().parse(request)
        
        # Get the task status from the parsed data
        taskstatus = task_data.get('taskstatus')
        
        if not taskstatus:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Task status is required",
                "debugMessage": "Please provide a valid task status"
            }, status=400)

        # Update the task status
        task.status = taskstatus
        task.save()

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task status updated successfully",
            "debugMessage": ""
        }, status=200)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Method Not Allowed",
            "debugMessage": "Only PUT method is allowed"
        }, status=405)
        
@csrf_exempt
def Work_Log_Registration(request):
    # GET data of worklog of the user 
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)
        
        worklog = WorkLog.objects.filter(created_by=user_id)
        work_log_serializer = WorkLogSerializer(worklog, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": work_log_serializer.data 
        }, safe=False)

    # POST  to insert data of worklog
    elif request.method == 'POST':
         # parse the incoming JSON data
        work_log_data = JSONParser().parse(request)
        print(work_log_data)  
        user_id = getattr(request, 'user_id', None)
        
        work_log_time = work_log_data.get('work_log_time')
        work_log_description = work_log_data.get('work_log_description')
        
        # checking whether  work_log_time and work_log_description are provided
        if not work_log_time or not work_log_description:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Missing required fields",
                "debugMessage": "work_log_time, work_log_description are required"
            }, status=400)

        current_date = date.today()
        existing_work_logs = WorkLog.objects.filter(created_by=user_id, created_date=current_date)
        total_work_log_time = sum(log.work_log_time for log in existing_work_logs)

        # checking whether  adding the new work log exceeds 8 hours
        if total_work_log_time + work_log_time > 8:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Total work log time exceeds 8 hours for the current date",
                "debugMessage": f"Current total work log time: {total_work_log_time} hours. Cannot exceed 8 hours."
            }, status=400)

        reg_work_log = WorkLog()
        reg_work_log.work_log_time = work_log_time
        reg_work_log.work_log_description = work_log_description
        reg_work_log.created_by = MyUser.objects.get(id=user_id)
        reg_work_log.created_date = current_date
        
        reg_work_log.save()
        
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Work Log Added Successfully",
            "debugMessage": ""
        }, safe=False)
        
@csrf_exempt
def Project_Assign(request, id):
    # PUT  to update data of assigned_to in project 
    if request.method == 'PUT':
        if not id:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "Project ID is required",
                "debugMessage": "Please provide a valid Project ID"
            }, status=400)
        
        try:
            project = Project.objects.get(project_id=id)
        except Project.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Project not found",
                "debugMessage": f"No Project found with ID {id}"
            }, status=404)
        
        # Parse the incoming data
        project_data = JSONParser().parse(request)
        print(project_data)

        assigned_to = project_data.get('assigned_to')
        
        if not assigned_to:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "'assigned_to' is required",
                "debugMessage": "Please provide the 'assigned_to' field"
            }, status=400)

        project.assigned_to = MyUser.objects.get(id=assigned_to)
        project.save()

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Task Assigned Successfully",
            "debugMessage": ""
        }, status=200)

    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Method Not Allowed",
            "debugMessage": "Only PUT method is allowed"
        }, status=405)
        
@csrf_exempt
def All_Manager(request, id=None): 
    # GET data of manager
    if request.method == 'GET':
        user = MyUser.objects.filter(role="manager")
        myuser_serializer = MyUserSerializer(user, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": myuser_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Project_Without_Assign(request): 
    # GET data of project of without assign
    if request.method == 'GET':
        project = Project.objects.filter(assigned_to__isnull=True)
        project_serializer = ProjectSerializer(project, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": project_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Project_With_Assign(request): 
     # GET data of project of with assign
     if request.method == 'GET':
        project = Project.objects.filter(assigned_to__isnull=False)
        project_serializer = ProjectSerializer(project, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": project_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Manager_Project(request): 
     # GET data of project of that user
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)
        print(user_id)
        project = Project.objects.filter(assigned_to=user_id)
        project_serializer = ProjectSerializer(project, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": project_serializer.data 
        }, safe=False)
        
        
@csrf_exempt
def Task_Report(request):
    # POST  to insert data of task report 
    if request.method == 'POST':
        if 'taskfile' not in request.FILES:
            return JsonResponse({
                "hasError": True,
                "errorCode": 400,
                "message": "No file provided",
                "debugMessage": "Please upload a file"
            }, status=400)

        uploaded_file = request.FILES['taskfile']
        
       
        task_id = request.POST.get('currentTaskId') 

        try:
            task = Task.objects.get(task_id=task_id)
        except Task.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "Task not found",
                "debugMessage": f"Task with task_id {task_id} does not exist"
            }, status=404)

        user_id = getattr(request, 'user_id', None)
        try:
            user = MyUser.objects.get(id=user_id)
        except MyUser.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "User not found",
                "debugMessage": f"User with id {user_id} does not exist"
            }, status=404)

        task_report = TaskReport()
        task_report.report_file = uploaded_file
        task_report.task = task
        task_report.user = user
        task_report.report_date = date.today()
        
        try:
            task_report.save()
        except Exception as e:
            return JsonResponse({
                "hasError": True,
                "errorCode": 500,
                "message": "Error saving task report",
                "debugMessage": str(e)
            }, status=500)

        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "File uploaded successfully",
            "debugMessage": ""
        }, status=200)
    else:
        return JsonResponse({
            "hasError": True,
            "errorCode": 405,
            "message": "Method Not Allowed",
            "debugMessage": "Only POST method is allowed"
        }, status=405)
        
@csrf_exempt
def Performance_Report(request, id=None): 
    # GET data of report
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)

        try:
            user = MyUser.objects.get(id=user_id) 
            username = user.username 
        except MyUser.DoesNotExist:
            return JsonResponse({
                "hasError": True,
                "errorCode": 404,
                "message": "User not found",
                "debugMessage": "Invalid user ID",
                "data": {}
            })

        tasks = Task.objects.filter(assigned_to=user_id)

        completed_tasks_count = tasks.filter(status='completed').count()
        print(completed_tasks_count)
        pending_tasks_count = tasks.filter(status='not_started').count()
        print(pending_tasks_count)

        # checking whether  completed tasks count is greater than 5
        if completed_tasks_count >= 5:
            performance_report = {
                "hasError": False,
                "errorCode": 0,
                "message": "Performance Report Generated",
                "debugMessage": "",
                "data": {
                    "username": username,
                    "user_id": user_id,
                    "completedTasksCount": completed_tasks_count,
                    "pendingTasksCount": pending_tasks_count,
                    "performanceReportMessage": "Employee has completed 5 or more tasks"
                }
            }
        else:
            performance_report = {
                "hasError": False,
                "errorCode": 0,
                "message": "Success",
                "debugMessage": "",
                "data": {
                    "username": username,
                    "user_id": user_id,
                    "completedTasksCount": completed_tasks_count,
                    "pendingTasksCount": pending_tasks_count,
                    "performanceReportMessage": "Employee has not yet completed 5 tasks"
                }
            }

        return JsonResponse(performance_report, safe=False)
    
    
@csrf_exempt
def Task_View(request, id=None): 
    # GET data of task
    if request.method == 'GET':
        task = Task.objects.all()
        task_serializer = TaskSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_serializer.data 
        }, safe=False)
        
@csrf_exempt
def Task_Report_View(request, id=None): 
    # GET data of task report
    if request.method == 'GET':
        task = TaskReport.objects.all()
        task_report_serializer = TaskReportSerializer(task, many=True)
        return JsonResponse({
            "hasError": False,
            "errorCode": 0,
            "message": "Success",
            "debugMessage": "",
            "data": task_report_serializer.data 
        }, safe=False)