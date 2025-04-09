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
import logging


logger = logging.getLogger('django')

# Create your views here.

# Utility function to create a standard success response
def create_success_response(data, message="Success"):
    return JsonResponse({
        "hasError": False,
        "errorCode": 0,
        "message": message,
        "debugMessage": "",
        "data": data
    }, safe=False)

# Utility function to create a standard error response
def create_error_response(error_code, message, debug_message=""):
    return JsonResponse({
        "hasError": True,
        "errorCode": error_code,
        "message": message,
        "debugMessage": debug_message,
        "data": {}
    }, status=error_code)

SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 90  # 1 minute
ACCESS_TOKEN_EXPIRATION = 1  # 1 minute
@csrf_exempt
def Signin(request):
    if request.method == "POST":
        try:
            # Log incoming request
            logger.info('Received a sign-in request')

            # Parse the incoming JSON data
            user_data = JSONParser().parse(request)
            username = user_data.get('username')
            password = user_data.get('password')
            
            # Check if username and password are provided
            if not username or not password:
                logger.error(f'Missing username or password')
                return create_error_response(400, "Username and password are required.", "Username or password not provided.")

            # authenticate the user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                logger.info(f'User {username} authenticated successfully')
                request.session['user_id'] = user.id

                try:
                    login_obj = MyUser.objects.get(username=username)

                    # Check if the user is an employee
                    if login_obj.role == "employee":
                        current_date = datetime.date.today()

                        # Check if the employee has logged more than 8 hours
                        existing_work_logs = WorkLog.objects.filter(created_by=user, created_date=current_date)
                        total_work_log_time = sum(log.work_log_time for log in existing_work_logs)

                        new_work_log_time = user_data.get('work_log_time', 0)

                        if total_work_log_time + new_work_log_time >= 8:
                            logger.warning(f'User {username} attempted to log more than 8 hours. Total work time: {total_work_log_time} hours.')
                            response_data = {
                                "hasError": True,
                                "errorCode": 400,
                                "message": "Cannot log more than 8 hours in a day.",
                                "debugMessage": f"Total work log time today: {total_work_log_time} hours."
                            }
                            response_data['redirect'] = 'signin' 
                            return create_error_response(400, "Cannot log more than 8 hours in a day.", f"Total work log time today: {total_work_log_time} hours.")

                    # Generate access token and refresh token
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
                        logger.error(f'Invalid role for user {username}: {login_obj.role}')
                        return create_error_response(400, "Invalid role", "")

                    response = create_success_response(response_data)
                    response.set_cookie(key='access_token', value=access_token, httponly=True, secure=True)
                    response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True)

                    logger.info(f'User {username} logged in successfully, redirecting to {response_data["redirect"]}')
                    return response

                except MyUser.DoesNotExist:
                    logger.error(f'User {username} does not exist.')
                    return create_error_response(404, "User does not exist", "")

            else:
                logger.error(f'Authentication failed for user {username}')
                return create_error_response(400, "Incorrect username or password.", "")

        except Exception as e:
            logger.exception(f'An unexpected error occurred during sign-in: {str(e)}')
            return create_error_response(500, "An unexpected error occurred.", str(e))

    logger.warning('Received invalid request method for sign-in')
    return create_error_response(400, "Invalid request", "")


    
    
SECRET_KEY = 'secret'

REFRESH_TOKEN_EXPIRATION = 90  # 1 minute
ACCESS_TOKEN_EXPIRATION = 1  # 1 minute

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
      # Log incoming request
    logger.info("Received request for Manager data.")

    if request.method == "GET":
        try:
            # get data of managers from database
            myuser = MyUser.objects.filter(role='manager')
            myuser_serializer = MyUserSerializer(myuser, many=True)

            logger.info(f"Fetched {len(myuser)} managers.")

            return create_success_response(myuser_serializer.data)

        except Exception as e:
            logger.error(f"Error fetching managers: {str(e)}", exc_info=True)
            return create_error_response(500, "Failed to fetch manager data", str(e))

    # POST to insert data of manager
    elif request.method == "POST":
        try:
            # Parse the incoming JSON data
            user_data = JSONParser().parse(request)
            logger.info(f"Received data for new manager: {user_data}")

            user_id = getattr(request, 'user_id', None)
            logger.info(f"User ID from session: {user_id}")

            password = user_data.get('password')
            username = user_data.get('username')
            email = user_data.get('email')
            role = user_data.get('role')

            if not (password and username and email and role):
                logger.warning(f"Missing required fields: password={password}, username={username}, email={email}, role={role}")
                return create_error_response(400, "Failed to Register", "Missing required fields")

            # Log manager registration attempt
            logger.info(f"Attempting to register new manager: {username} with email: {email}")

            reg_login = MyUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                created_by_id=user_id,
                role=role
            )
            reg_login.save()

            # Log success
            logger.info(f"Manager {username} registered successfully.")

            return create_success_response({}, "Manager registration successful")

        except Exception as e:
            logger.error(f"Error during manager registration: {str(e)}", exc_info=True)
            return create_error_response(500, "Failed to Register", str(e))

    # If the method is neither GET nor POST
    logger.warning(f"Invalid request method: {request.method} for Manager endpoint.")
    return create_error_response(405, "Invalid request method", "Only GET and POST methods are allowed")
    
@csrf_exempt
def Employee(request):
      # Log incoming request
    logger.info("Received request for Employee data.")

    # GET request for employee data
    if request.method == "GET":
        try:
            myuser = MyUser.objects.filter(role='employee')
            myuser_serializer = MyUserSerializer(myuser, many=True)

            logger.info(f"Fetched {len(myuser)} employees.")

            return create_success_response(myuser_serializer.data)

        except Exception as e:
            logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))

    # POST to insert data of employee
    elif request.method == "POST":
        try:
            # Parse the incoming JSON data
            user_data = JSONParser().parse(request)
            logger.info(f"Received data for new employee: {user_data}")

            user_id = getattr(request, 'user_id', None)
            logger.info(f"User ID from session: {user_id}")

            password = user_data.get('password')
            username = user_data.get('username')
            email = user_data.get('email')
            role = user_data.get('role')

            if not (password and username and email and role):
                logger.warning(f"Missing required fields: password={password}, username={username}, email={email}, role={role}")
                return create_error_response(400, "Missing required fields", "Please provide all required fields")

            # Log employee registration attempt
            logger.info(f"Attempting to register new employee: {username} with email: {email}")

            reg_login = MyUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                created_by_id=user_id,
                role=role
            )
            reg_login.save()

            # Log success
            logger.info(f"Employee {username} registered successfully.")

            return create_success_response({}, "Employee registration successful")

        except Exception as e:
            logger.error(f"Error during employee registration: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))

    # If the method is neither GET nor POST
    logger.warning(f"Invalid request method: {request.method} for Employee endpoint.")
    return create_error_response(405, "Invalid request method", "Only GET and POST methods are allowed")
    
    
@csrf_exempt
def Project_Registration(request, id=None):
      # Log incoming request
    logger.info("Received request for Project registration.")

    # GET data of project
    if request.method == 'GET':
        try:
            project = Project.objects.all()
            project_serializer = ProjectSerializer(project, many=True)
            logger.info(f"Fetched {len(project)} projects.")
            return create_success_response(project_serializer.data)

        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))

    # POST to insert data of project
    elif request.method == 'POST':
        project_data = JSONParser().parse(request)
        logger.info(f"Received data for new project: {project_data}")

        project_name = project_data.get('project_name')
        project_description = project_data.get('project_description')
        last_date = project_data.get('last_date')

        if not project_name or not project_description or not last_date:
            logger.warning(f"Missing required fields: project_name={project_name}, project_description={project_description}, last_date={last_date}")
            return create_error_response(400, "Missing required fields", "project_name, project_description and last_date are required")

        try:
            reg_project = Project(
                project_name=project_name,
                project_description=project_description,
                last_date=last_date,
                created_date=date.today()
            )
            reg_project.save()
            logger.info(f"Project '{project_name}' added successfully.")
            return create_success_response({}, "Project Added Successfully")

        except Exception as e:
            logger.error(f"Error adding project: {str(e)}", exc_info=True)
            return create_error_response(500, "Failed to add project", str(e))

    # PUT to update data of project
    elif request.method == 'PUT':
        if id is None:
            logger.warning("Project ID is required for update.")
            return create_error_response(400, "Project ID is required", "Please provide a valid Project ID")

        try:
            project = Project.objects.get(project_id=id)
            logger.info(f"Found project with ID {id} for update.")
        except Project.DoesNotExist:
            logger.warning(f"Project with ID {id} not found.")
            return create_error_response(404, "Project not found", f"No Project found with ID {id}")

        project_data = JSONParser().parse(request)
        logger.info(f"Received data for updating project with ID {id}: {project_data}")

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
        logger.info(f"Project with ID {id} updated successfully.")
        return create_success_response({}, "Project Updated Successfully")

    # DELETE to delete data of a project
    elif request.method == 'DELETE':
        if id is None:
            logger.warning("Project ID is required for deletion.")
            return create_error_response(400, "Project ID is required", "Please provide a valid Project ID")

        try:
            project = Project.objects.get(project_id=id)
            logger.info(f"Found project with ID {id} for deletion.")
        except Project.DoesNotExist:
            logger.warning(f"Project with ID {id} not found.")
            return create_error_response(404, "Project not found", f"No Project found with ID {id}")

        project.delete()
        logger.info(f"Project with ID {id} deleted successfully.")
        return create_success_response({}, "Project Deleted Successfully")

    else:
        logger.warning(f"Invalid request method: {request.method} for Project_Registration endpoint.")
        return create_error_response(405, "Invalid request method", "Only GET, POST, PUT, and DELETE methods are allowed")
        
@csrf_exempt
def Task_Registration(request, id=None):
     # Log incoming request
    logger.info("Received request for Task registration.")

    # GET data of task
    if request.method == 'GET':
        try:
            task = Task.objects.filter(assigned_to__isnull=True)
            task_serializer = TaskSerializer(task, many=True)
            logger.info(f"Fetched {len(task)} tasks with unassigned status.")
            return create_success_response(task_serializer.data)

        except Exception as e:
            logger.error(f"Error fetching tasks: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))

    # POST to insert data of task
    elif request.method == 'POST':
        task_data = JSONParser().parse(request)
        logger.info(f"Received data for new task: {task_data}")

        user_id = getattr(request, 'user_id', None)
        project_name = task_data.get('project_name')
        task_name = task_data.get('task_name')
        task_description = task_data.get('task_description')
        is_high_priority = task_data.get('is_high_priority')
        last_date = task_data.get('last_date')

        if not project_name or not task_name or not task_description or not is_high_priority or not last_date:
            logger.warning(f"Missing required fields: project_name={project_name}, task_name={task_name}, task_description={task_description}, is_high_priority={is_high_priority}, last_date={last_date}")
            return create_error_response(400, "Missing required fields", "project_name, task_name, task_description, is_high_priority and last_date are required")

        try:
            reg_task = Task(
                project=Project.objects.get(project_id=project_name),
                task_name=task_name,
                task_description=task_description,
                task_last_date=last_date,
                created_at=date.today(),
                updated_at=date.today(),
                created_by=MyUser.objects.get(id=user_id),
                is_high_priority=is_high_priority
            )
            reg_task.save()
            logger.info(f"Task '{task_name}' added successfully.")
            return create_success_response({}, "Task Added Successfully")

        except Exception as e:
            logger.error(f"Error adding task: {str(e)}", exc_info=True)
            return create_error_response(500, "Failed to add task", str(e))

    # PUT to update data of task
    elif request.method == 'PUT':
        if id is None:
            logger.warning("Task ID is required for update.")
            return create_error_response(400, "Task ID is required", "Please provide a valid Task ID")

        try:
            task = Task.objects.get(task_id=id)
            logger.info(f"Found task with ID {id} for update.")
        except Task.DoesNotExist:
            logger.warning(f"Task with ID {id} not found.")
            return create_error_response(404, "Task not found", f"No Task found with ID {id}")

        task_data = JSONParser().parse(request)
        logger.info(f"Received data for updating task with ID {id}: {task_data}")

        project_name = task_data.get('project_name')
        task_name = task_data.get('task_name')
        task_description = task_data.get('task_description')
        is_high_priority = task_data.get('is_high_priority')
        last_date = task_data.get('last_date')
        user_id = getattr(request, 'user_id', None)

        if project_name:
            task.project = Project.objects.get(project_id=project_name)
        if task_name:
            task.task_name = task_name
        if task_description:
            task.task_description = task_description
        if last_date:
            task.task_last_date = last_date
            task.updated_at = date.today()
        if user_id:
            task.created_by = MyUser.objects.get(id=user_id)

        task.is_high_priority = is_high_priority

        task.save()
        logger.info(f"Task with ID {id} updated successfully.")
        return create_success_response({}, "Task Updated Successfully")

    # DELETE to delete data of a task
    elif request.method == 'DELETE':
        if id is None:
            logger.warning("Task ID is required for deletion.")
            return create_error_response(400, "Task ID is required", "Please provide a valid Task ID")

        try:
            task = Task.objects.get(task_id=id)
            logger.info(f"Found task with ID {id} for deletion.")
        except Task.DoesNotExist:
            logger.warning(f"Task with ID {id} not found.")
            return create_error_response(404, "Task not found", f"No Task found with ID {id}")

        task.delete()
        logger.info(f"Task with ID {id} deleted successfully.")
        return create_success_response({}, "Task Deleted Successfully")

    else:
        logger.warning(f"Invalid request method: {request.method} for Task_Registration endpoint.")
        return create_error_response(405, "Invalid request method", "Only GET, POST, PUT, and DELETE methods are allowed")
        
        
@csrf_exempt
def All_Employee(request, id=None):
    logger.info("Received request for All Employee data.")

    # GET data of all employees
    if request.method == 'GET':
        try:
            user = MyUser.objects.filter(role="employee")
            myuser_serializer = MyUserSerializer(user, many=True)

            logger.info(f"Found {len(user)} employees with role 'employee'.")

            return create_success_response(myuser_serializer.data)

        except Exception as e:
            logger.error(f"Error fetching employees: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))

    else:
        logger.warning(f"Invalid request method: {request.method} for All_Employee endpoint.")
        return create_error_response(405, "Invalid request method", "Only GET method is allowed")
        
@csrf_exempt
def Task_Assign(request, id):
    # PUT to update data of assigned_to in task
    if request.method == 'PUT':
        if id is None:
            logger.warning("Task ID is missing.")
            return create_error_response(400, "Task ID is required", "Please provide a valid Task ID")

        try:
            task = Task.objects.get(task_id=id)
        except Task.DoesNotExist:
            logger.error(f"Task not found with ID: {id}")
            return create_error_response(404, "Task not found", f"No Task found with ID {id}")

        task_data = JSONParser().parse(request)
        logger.info(f"Task data received for assignment: {task_data}")

        assigned_to = task_data.get('assigned_to')
        is_high_priority = task_data.get('is_high_priority')

        if assigned_to:
            try:
                user = MyUser.objects.get(id=assigned_to)
                logger.info(f"User with ID {assigned_to} found for task assignment.")
            except MyUser.DoesNotExist:
                logger.error(f"No user found with ID {assigned_to}")
                return create_error_response(400, "Invalid assigned_to ID", "No user found with this ID")

            # Check if user has less than 3 high-priority tasks
            if is_high_priority:
                high_priority_count = Task.objects.filter(assigned_to=user, is_high_priority=True).exclude(status='completed').count()
                logger.info(f"User {assigned_to} currently has {high_priority_count} high-priority tasks.")

                if high_priority_count >= 3:
                    logger.warning(f"User {assigned_to} already has 3 high-priority tasks.")
                    return create_error_response(400, "User already has 3 high-priority tasks")

            # Assign task to the user
            task.assigned_to = user
            logger.info(f"Task with ID {id} assigned to user with ID {assigned_to}.")

        if is_high_priority is not None:
            task.is_high_priority = is_high_priority
            logger.info(f"Task with ID {id} high priority status updated to {is_high_priority}.")

        task.save()

        logger.info(f"Task with ID {id} assigned successfully.")
        return create_success_response({}, "Task Assigned Successfully")

    else:
        logger.warning("Invalid HTTP method used for Task_Assign. Only PUT is allowed.")
        return create_error_response(405, "Method Not Allowed", "Only PUT method is allowed")
        
@csrf_exempt
def Task_Without_Assign(request): 
      # Log incoming request
    logger.info('Received request method: %s for Task_Without_Assign view', request.method)

    # GET data of task without assignment
    if request.method == 'GET':
        try:
            logger.info('Fetching tasks without assignment.')
            task = Task.objects.filter(assigned_to__isnull=True)
            task_serializer = TaskSerializer(task, many=True)

            logger.info('Successfully fetched tasks without assignment.')
            return create_success_response(task_serializer.data)

        except Exception as e:
            logger.error('Error occurred while fetching tasks: %s', str(e))
            return create_error_response(500, "Internal Server Error", str(e))

    else:
        logger.warning('Invalid request method: %s', request.method)
        return create_error_response(405, "Invalid request method", "Only GET method is allowed")
        
        
@csrf_exempt
def Task_With_Assign(request): 
      # Log incoming request
    logger.info('Received request method: %s for Task_With_Assign view', request.method)

    # GET data of task with assign
    if request.method == 'GET':
        try:
            logger.info('Fetching tasks with assignment.')
            task = Task.objects.filter(assigned_to__isnull=False)
            task_serializer = TaskSerializer(task, many=True)

            logger.info('Successfully fetched tasks with assignment.')
            return create_success_response(task_serializer.data)

        except Exception as e:
            logger.error('Error occurred while fetching tasks: %s', str(e))
            return create_error_response(500, "Internal Server Error", str(e))

    else:
        logger.warning('Invalid request method: %s', request.method)
        return create_error_response(405, "Invalid request method", "Only GET method is allowed")
        
@csrf_exempt
def User_Task(request): 
    # Log incoming request
    logger.info('Received request method: %s for User_Task view', request.method)

    # GET data of task of the user
    if request.method == 'GET':
        try:
            user_id = getattr(request, 'user_id', None)
            logger.info('User ID retrieved: %s', user_id)

            if not user_id:
                logger.warning('No user ID provided in the request.')
                return create_error_response(400, "User ID is required", "Please provide a valid user ID")

            task = Task.objects.filter(assigned_to=user_id)
            task_serializer = TaskSerializer(task, many=True)

            logger.info('Successfully fetched tasks for user ID: %s', user_id)
            return create_success_response(task_serializer.data)
        
        except Exception as e:
            logger.error('Error occurred while fetching tasks for user ID %s: %s', user_id, str(e))
            return create_error_response(500, "Internal Server Error", str(e))

    else:
        logger.warning('Invalid request method: %s', request.method)
        return create_error_response(405, "Invalid request method", "Only GET method is allowed")
        
@csrf_exempt
def Status_Update(request, id):
      # Log incoming request
    logger.info('Received request method: %s for Status_Update view', request.method)

    # PUT to update data of status in task
    if request.method == 'PUT':
        try:
            task = Task.objects.get(task_id=id)
            logger.info('Task found with ID: %s', id)
        except Task.DoesNotExist:
            logger.error('Task not found with ID: %s', id)
            return create_error_response(404, "Task not found", f"No Task found with ID {id}")
        
        # Parse the incoming JSON data
        task_data = JSONParser().parse(request)
        logger.info('Parsed task data: %s', task_data)

        taskstatus = task_data.get('taskstatus')

        if not taskstatus:
            logger.warning('Task status is missing in the request data for Task ID: %s', id)
            return create_error_response(400, "Task status is required", "Please provide a valid task status")

        task.status = taskstatus
        task.save()
        logger.info('Task status updated to: %s for Task ID: %s', taskstatus, id)

        return create_success_response(None, "Task status updated successfully")

    else:
        logger.warning('Invalid request method: %s', request.method)
        return create_error_response(405, "Method Not Allowed", "Only PUT method is allowed")
        
@csrf_exempt
def Work_Log_Registration(request):
      # Log incoming request
    logger.info('Received request method: %s for Work_Log_Registration view', request.method)

    # GET data of worklog of the user
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)
        logger.info('Fetching work logs for user ID: %s', user_id)

        worklog = WorkLog.objects.filter(created_by=user_id)
        work_log_serializer = WorkLogSerializer(worklog, many=True)

        logger.info('Found %d work logs for user ID: %s', len(worklog), user_id)

        return create_success_response(work_log_serializer.data)

    # POST to insert data of worklog
    elif request.method == 'POST':
        # Parse the incoming JSON data
        work_log_data = JSONParser().parse(request)
        logger.info('Received work log data: %s', work_log_data)
        user_id = getattr(request, 'user_id', None)
        
        work_log_time = work_log_data.get('work_log_time')
        work_log_description = work_log_data.get('work_log_description')


        if not work_log_time or not work_log_description:
            logger.warning('Missing required fields: work_log_time or work_log_description for user ID: %s', user_id)
            return create_error_response(400, "Missing required fields", "work_log_time, work_log_description are required")

        current_date = date.today()
        existing_work_logs = WorkLog.objects.filter(created_by=user_id, created_date=current_date)
        total_work_log_time = sum(log.work_log_time for log in existing_work_logs)

        logger.info('Current total work log time for user ID %s on %s: %s hours', user_id, current_date, total_work_log_time)

        if total_work_log_time + work_log_time > 8:
            logger.warning('Total work log time exceeds 8 hours for user ID: %s on %s. Current total: %s hours, Attempted addition: %s hours',
                           user_id, current_date, total_work_log_time, work_log_time)
            return create_error_response(400, "Total work log time exceeds 8 hours for the current date", 
                                         f"Current total work log time: {total_work_log_time} hours. Cannot exceed 8 hours.")

        reg_work_log = WorkLog()
        reg_work_log.work_log_time = work_log_time
        reg_work_log.work_log_description = work_log_description
        reg_work_log.created_by = MyUser.objects.get(id=user_id)
        reg_work_log.created_date = current_date
        
        reg_work_log.save()
        logger.info('Work log added successfully for user ID: %s on %s. Work log time: %s hours', user_id, current_date, work_log_time)

        return create_success_response(None, "Work Log Added Successfully")

    else:
        logger.warning('Invalid request method: %s for Work_Log_Registration view', request.method)
        return create_error_response(405, "Method Not Allowed", "Only GET and POST methods are allowed")
        
@csrf_exempt
def Project_Assign(request, id):
     # Log incoming request
    logger.info('Received request method: %s for Project_Assign view with Project ID: %s', request.method, id)

    # PUT to update data of assigned_to in project
    if request.method == 'PUT':
        if not id:
            logger.warning('Project ID is missing in the request')
            return create_error_response(400, "Project ID is required", "Please provide a valid Project ID")
        
        try:
            project = Project.objects.get(project_id=id)
            logger.info('Found project with ID: %s', id)
        except Project.DoesNotExist:
            logger.error('Project with ID: %s not found', id)
            return create_error_response(404, "Project not found", f"No Project found with ID {id}")
        
        # Parse the incoming data
        project_data = JSONParser().parse(request)
        logger.info('Received project assignment data: %s', project_data)

        assigned_to = project_data.get('assigned_to')

        if not assigned_to:
            logger.warning('Assigned user ID is missing in the request for project ID: %s', id)
            return create_error_response(400, "'assigned_to' is required", "Please provide the 'assigned_to' field")

        try:
            user = MyUser.objects.get(id=assigned_to)
            logger.info('Found user with ID: %s', assigned_to)
        except MyUser.DoesNotExist:
            logger.error('User with ID: %s not found', assigned_to)
            return create_error_response(404, "User not found", f"No user found with ID {assigned_to}")

        project.assigned_to = user
        project.save()
        logger.info('Successfully assigned project ID: %s to user ID: %s', id, assigned_to)

        return create_success_response(None, "Project Assigned Successfully")

    else:
        logger.warning('Invalid request method: %s for Project_Assign view', request.method)
        return create_error_response(405, "Method Not Allowed", "Only PUT method is allowed")
        
@csrf_exempt
def All_Manager(request, id=None):
     # Log incoming request
    logger.info('Received request method: %s for All_Manager view', request.method)

    # GET data of manager
    if request.method == 'GET':
        try:
            user = MyUser.objects.filter(role="manager")
            logger.info('Found %d managers', user.count()) 
            myuser_serializer = MyUserSerializer(user, many=True)
            return create_success_response(myuser_serializer.data)

        except Exception as e:
            logger.error('Error while fetching manager data: %s', str(e))
            return create_error_response(500, "Internal Server Error", f"Error: {str(e)}")

    else:
        logger.warning('Invalid request method: %s for All_Manager view', request.method)
        return create_error_response(405, "Method Not Allowed", "Only GET method is allowed")

        
@csrf_exempt
def Project_Without_Assign(request): 
    # GET data of  projects not assigned to anyone
    if request.method == 'GET':
        try:
             # Log incoming request
            logger.debug("GET request received in Project_Without_Assign view")

            project = Project.objects.filter(assigned_to__isnull=True)
            project_serializer = ProjectSerializer(project, many=True)

            logger.debug(f"Found {len(project)} projects without assignment.")

            return create_success_response(project_serializer.data)
        
        except Exception as e:
            logger.error(f"Error occurred in Project_Without_Assign view: {str(e)}")

            return create_error_response(1, "An error occurred", str(e))

    else:
        logger.warning("Invalid request method: %s for Project_Without_Assign view", request.method)
        return create_error_response(405, "Method Not Allowed", "Only GET method is allowed")
        
@csrf_exempt
def Project_With_Assign(request):
     # Log incoming request
    logger.info("Received request for Project_With_Assign")
    
    try:
       #  GET data of  projects  assigned 
        if request.method == 'GET':
            logger.info("Processing GET request for projects assigned to someone.")
            
            project = Project.objects.filter(assigned_to__isnull=False)
            project_serializer = ProjectSerializer(project, many=True)
            
            logger.info(f"Found {len(project)} projects with assignments.")
            
            return create_success_response(project_serializer.data)
        
        else:
            logger.warning(f"Received unsupported HTTP method: {request.method}")
            
            return create_error_response(405, "Method Not Allowed", "This API only supports GET requests.")

    except Exception as e:
        logger.error(f"Error occurred while processing the request: {str(e)}", exc_info=True)
        
        return create_error_response(500, "Internal Server Error", str(e))
        
@csrf_exempt
def Manager_Project(request):
    # Log incoming request
    logger.info("Received request for Manager_Project")
    
    try:
       #  GET data of  projects  assigned to user_id
        if request.method == 'GET':
            user_id = getattr(request, 'user_id', None)
            logger.info(f"Processing GET request for user with ID: {user_id}")
            
            if user_id is None:
                logger.warning("No user_id found in the request.")
                return create_error_response(400, "Bad Request", "user_id is required.")
            
            project = Project.objects.filter(assigned_to=user_id)
            project_serializer = ProjectSerializer(project, many=True)
            
            logger.info(f"Found {len(project)} projects assigned to user {user_id}.")
            
            return create_success_response(project_serializer.data)
        
        else:
            logger.warning(f"Received unsupported HTTP method: {request.method}")
            return create_error_response(405, "Method Not Allowed", "This API only supports GET requests.")

    except Exception as e:
        logger.error(f"Error occurred while processing the request: {str(e)}", exc_info=True)
        return create_error_response(500, "Internal Server Error", str(e))
        
        
@csrf_exempt
def Task_Report(request):
     # Log incoming request
    logger.info("Received request for Task_Report")

    # POST request to insert task report 
    if request.method == 'POST':
        if 'taskfile' not in request.FILES:
            logger.warning("No taskfile found in request")
            return create_error_response(400, "No file provided", "Please upload a file")

        uploaded_file = request.FILES['taskfile']
        logger.info(f"Received file: {uploaded_file.name}")

        task_id = request.POST.get('currentTaskId') 
        logger.info(f"Received task_id: {task_id}")

        try:
            task = Task.objects.get(task_id=task_id)
            logger.info(f"Task found: {task_id}")
        except Task.DoesNotExist:
            logger.error(f"Task with task_id {task_id} does not exist")
            return create_error_response(404, "Task not found", f"Task with task_id {task_id} does not exist")

        user_id = getattr(request, 'user_id', None)
        logger.info(f"Received user_id: {user_id}")

        try:
            user = MyUser.objects.get(id=user_id)
            logger.info(f"User found: {user_id}")
        except MyUser.DoesNotExist:
            logger.error(f"User with id {user_id} does not exist")
            return create_error_response(404, "User not found", f"User with id {user_id} does not exist")

        task_report = TaskReport()
        task_report.report_file = uploaded_file
        task_report.task = task
        task_report.user = user
        task_report.report_date = date.today()

        try:
            task_report.save()
            logger.info("Task report saved successfully")
        except Exception as e:
            logger.error(f"Error saving task report: {str(e)}", exc_info=True)
            return create_error_response(500, "Error saving task report", str(e))

        logger.info("Task report file uploaded successfully")
        return create_success_response({}, "File uploaded successfully")
    
    else:
        logger.warning("Received unsupported HTTP method: %s", request.method)
        return create_error_response(405, "Method Not Allowed", "Only POST method is allowed")
        
@csrf_exempt
def Performance_Report(request, id=None):
      # Log incoming request
    logger.info("Received request for Performance_Report")

    # GET request to get performance report
    if request.method == 'GET':
        user_id = getattr(request, 'user_id', None)
        logger.info(f"Received user_id: {user_id}")
        try:
            user = MyUser.objects.get(id=user_id)
            username = user.username
            logger.info(f"User found: {username} (ID: {user_id})")
        except MyUser.DoesNotExist:
            logger.error(f"User with id {user_id} does not exist")
            return create_error_response(404, "User not found", "Invalid user ID")

        tasks = Task.objects.filter(assigned_to=user_id)
        completed_tasks_count = tasks.filter(status='completed').count()
        pending_tasks_count = tasks.filter(status='not_started').count()

        logger.info(f"Completed tasks count: {completed_tasks_count}")
        logger.info(f"Pending tasks count: {pending_tasks_count}")

        performance_report_message = "Employee has completed 5 or more tasks" if completed_tasks_count >= 5 else "Employee has not yet completed 5 tasks"
        
        performance_report_data = {
            "username": username,
            "user_id": user_id,
            "completedTasksCount": completed_tasks_count,
            "pendingTasksCount": pending_tasks_count,
            "performanceReportMessage": performance_report_message
        }

        logger.info(f"Performance report: {performance_report_message}")
        return create_success_response(performance_report_data, "Performance Report Generated")
    else:
        logger.warning(f"Unsupported HTTP method: {request.method}")
        return create_error_response(405, "Method Not Allowed", "Only GET method is allowed")

    
    
@csrf_exempt
def Task_View(request, id=None):
      # Log incoming request
    logger.info("Received request for Task_View")

    # GET request to get data of tasks
    if request.method == 'GET':
        try:
            task = Task.objects.all() 
            logger.info(f"Retrieved {task.count()} tasks")
            
            task_serializer = TaskSerializer(task, many=True)
            return create_success_response(task_serializer.data)
        
        except Exception as e:
            logger.error(f"Error occurred while retrieving tasks: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))
    
    else:
        logger.warning(f"Unsupported HTTP method: {request.method}")
        return create_error_response(405, "Method Not Allowed", "Only GET method is allowed")
        
@csrf_exempt
def Task_Report_View(request, id=None):
       # Log incoming request
    logger.info("Received request for Task_Report_View")

    # GET request to get data of task reports
    if request.method == 'GET':
        try:
            task_reports = TaskReport.objects.all()  # Get all task reports
            logger.info(f"Retrieved {task_reports.count()} task reports")
            
            task_report_serializer = TaskReportSerializer(task_reports, many=True)
            return create_success_response(task_report_serializer.data)
        
        except Exception as e:
            logger.error(f"Error occurred while retrieving task reports: {str(e)}", exc_info=True)
            return create_error_response(500, "Internal Server Error", str(e))
    else:
        logger.warning(f"Unsupported HTTP method: {request.method}")
        return create_error_response(405, "Method Not Allowed", "Only GET method is allowed")