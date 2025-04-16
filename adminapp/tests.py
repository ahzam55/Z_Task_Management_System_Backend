# from django.test import TestCase,RequestFactory,Client
# from rest_framework.test import APIRequestFactory
# from unittest.mock import patch
# import json
# from rest_framework import status
# from django.contrib.auth import get_user_model
# from django.urls import reverse

# from adminapp.views import *
# from adminapp.models import *
# from rest_framework.test import APIClient


# class ManagerViewTests(TestCase):
#     def setUp(self):
#         self.manager_url = reverse('Manager') 
#         self.factory = RequestFactory()

#         # Create and store an admin user
#         self.manager_user = MyUser.objects.create_user(
#             username='mockcreator',
#             email='creator@example.com',
#             password='creatorpass',
#             role='admin'
#         )

#     def test_get_all_managers_success(self):
#         """Test retrieving all managers."""
#         # Log in the admin user
#         self.client.login(username='mockcreator', password='creatorpass')

#         # Create sample manager users
#         MyUser.objects.create_user(
#             username='manager1',
#             email='m1@example.com',
#             password='test123',
#             role='manager'
#         )
#         MyUser.objects.create_user(
#             username='manager2',
#             email='m2@example.com',
#             password='test123',
#             role='manager'
#         )

#         # Make request to the manager URL
#         response = self.client.get(self.manager_url)
#         data = json.loads(response.content)

#         # Assertions
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], 'Success')
#         self.assertGreaterEqual(len(data['data']), 2)

#     def test_get_all_managers_exception(self):
#         """Test handling database exceptions."""
#         # Log in the admin user
#         self.client.login(username='mockcreator', password='creatorpass')

#         # Patch the filter method to raise an exception
#         with patch('adminapp.views.MyUser.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("DB error")

#             response = self.client.get(self.manager_url)
#             data = json.loads(response.content)

#             # Assertions
#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertIn("Failed to fetch manager data", data['message'])
#             self.assertIn("DB error", data['debugMessage'])


#     def test_post_register_manager_success(self):
#         data = {
#             'username': 'newmanager',
#             'email': 'newmanager@example.com',
#             'password': 'pass1234',
#             'role': 'manager'
#         }
#         json_data = json.dumps(data).encode('utf-8')

#         request = self.factory.post('/Manager', data=json_data, content_type='application/json')
#         request.user_id = self.manager_user.id  

#         response = Manager(request)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response_data['hasError'])
#         self.assertEqual(response_data['message'], 'Manager registration successful')
#         self.assertTrue(MyUser.objects.filter(username='newmanager').exists())

#     def test_post_register_manager_missing_fields(self):
#         data = {
#             'username': 'incomplete',
#             'password': 'pass1234'
#             # Missing email and role
#         }
#         json_data = json.dumps(data).encode('utf-8')
#         request = self.factory.post('/Manager', data=json_data, content_type='application/json')
#         request.user_id = self.manager_user.id  # mock authenticated user ID

#         response = Manager(request)

#         data = json.loads(response.content)
#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], 'Failed to Register')
#         self.assertEqual(data['debugMessage'], 'Missing required fields')  # Adjusted to match the actual response


#     def test_post_register_manager_exception(self):
#         with patch('adminapp.views.MyUser.objects.create_user') as mock_create_user:
#             mock_create_user.side_effect = Exception("Create user error")

#             data = {
#                 'username': 'test',
#                 'email': 'test@example.com',
#                 'password': 'test123',
#                 'role': 'manager'
#             }
#             json_data = json.dumps(data).encode('utf-8')
#             request = self.factory.post('/Manager', data=json_data, content_type='application/json')
#             request.user_id = self.manager_user.id

#             response = Manager(request)

#             data = json.loads(response.content)
#             self.assertEqual(response.status_code, 500)
#             self.assertEqual(data['hasError'], True)  # Check for 'hasError' field
#             self.assertEqual(data['message'], 'Failed to Register')
#             self.assertIn("Create user error", data['debugMessage'])  # Check for debugMessage field


#     def test_manager_invalid_method(self):
#         request = self.factory.put('/Manager')
#         response = Manager(request)

#         data = json.loads(response.content)
#         # Adjust the expected error message to match what your view returns
#         self.assertEqual(data['message'], 'Invalid request method')        
    
    



# class EmployeeViewTests(TestCase):
#     def setUp(self):
#         self.employee_url = reverse('Employee')
#         self.factory = RequestFactory()

#         self.admin_user = MyUser.objects.create_user(
#             username='adminuser',
#             email='admin@example.com',
#             password='adminpass',
#             role='admin'
#         )

#     def test_get_all_employees_success(self):
#         self.client.force_login(self.admin_user)

#         MyUser.objects.create_user(
#             username='employee1',
#             email='e1@example.com',
#             password='test123',
#             role='employee'
#         )
#         MyUser.objects.create_user(
#             username='employee2',
#             email='e2@example.com',
#             password='test123',
#             role='employee'
#         )

#         response = self.client.get(self.employee_url)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], 'Success')
#         self.assertGreaterEqual(len(data['data']), 2)

#     def test_get_all_employees_exception(self):
#         self.client.force_login(self.admin_user)

#         with patch('adminapp.views.MyUser.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("DB error")

#             response = self.client.get(self.employee_url)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], 'Internal Server Error')  # Adjusted
#             self.assertIn("DB error", data['debugMessage'])

#     def test_post_register_employee_success(self):
#         data = {
#             'username': 'newemployee',
#             'email': 'newemployee@example.com',
#             'password': 'pass1234',
#             'role': 'employee'
#         }
#         json_data = json.dumps(data).encode('utf-8')

#         request = self.factory.post('/Employee', data=json_data, content_type='application/json')
#         request.user_id = self.admin_user.id

#         response = Employee(request)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response_data['hasError'])
#         self.assertEqual(response_data['message'], 'Employee registration successful')
#         self.assertTrue(MyUser.objects.filter(username='newemployee').exists())

#     def test_post_register_employee_missing_fields(self):
#         data = {
#             'username': 'incompleteemp',
#             'password': 'pass1234'
#         }
#         json_data = json.dumps(data).encode('utf-8')
#         request = self.factory.post('/Employee', data=json_data, content_type='application/json')
#         request.user_id = self.admin_user.id

#         response = Employee(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], 'Missing required fields')  # Adjusted

#     def test_post_register_employee_exception(self):
#         with patch('adminapp.views.MyUser.objects.create_user') as mock_create_user:
#             mock_create_user.side_effect = Exception("Create employee error")

#             data = {
#                 'username': 'emp_test',
#                 'email': 'emp@example.com',
#                 'password': 'test123',
#                 'role': 'employee'
#             }
#             json_data = json.dumps(data).encode('utf-8')
#             request = self.factory.post('/Employee', data=json_data, content_type='application/json')
#             request.user_id = self.admin_user.id

#             response = Employee(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], 'Internal Server Error')  # Adjusted
#             self.assertIn("Create employee error", data['debugMessage'])

#     def test_employee_invalid_method(self):
#         request = self.factory.put('/Employee')
#         response = Employee(request)
#         data = json.loads(response.content)

#         self.assertEqual(data['message'], 'Invalid request method')





    
    
    
    
    
# class ProjectRegistrationTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.project = Project.objects.create(
#             project_name="Test Project",
#             project_description="Test Description",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#     def test_get_projects_success(self):
#         request = self.factory.get('/Project')
#         response = Project_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], 'Success')
#         self.assertGreaterEqual(len(data['data']), 1)

#     def test_get_projects_exception(self):
#         with patch('adminapp.views.Project.objects.all') as mock_all:
#             mock_all.side_effect = Exception("DB error")
#             request = self.factory.get('/Project')
#             response = Project_Registration(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], 'Internal Server Error')
#             self.assertIn("DB error", data['debugMessage'])

#     def test_post_project_success(self):
#         data = {
#             "project_name": "New Project",
#             "project_description": "Description here",
#             "last_date": str(date.today())
#         }
#         json_data = json.dumps(data)
#         request = self.factory.post('/Project', data=json_data, content_type='application/json')
#         response = Project_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], 'Project Added Successfully')
#         self.assertTrue(Project.objects.filter(project_name="New Project").exists())

#     def test_post_project_missing_fields(self):
#         data = {
#             "project_description": "No name or date"
#         }
#         json_data = json.dumps(data)
#         request = self.factory.post('/Project', data=json_data, content_type='application/json')
#         response = Project_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], 'Missing required fields')

#     def test_post_project_exception(self):
#         with patch('adminapp.views.Project.save') as mock_save:
#             mock_save.side_effect = Exception("Save error")

#             data = {
#                 "project_name": "Exception Project",
#                 "project_description": "Oops",
#                 "last_date": str(date.today())
#             }
#             json_data = json.dumps(data)
#             request = self.factory.post('/Project', data=json_data, content_type='application/json')
#             response = Project_Registration(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertEqual(data['message'], 'Failed to add project')
#             self.assertIn("Save error", data['debugMessage'])

#     def test_put_project_success(self):
#         update_data = {
#             "project_name": "Updated Name",
#             "project_description": "Updated Description",
#             "last_date": str(date.today())
#         }
#         json_data = json.dumps(update_data)
#         request = self.factory.put(f'/Project/{self.project.project_id}', data=json_data, content_type='application/json')
#         response = Project_Registration(request, id=self.project.project_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['message'], 'Project Updated Successfully')
#         updated_project = Project.objects.get(project_id=self.project.project_id)
#         self.assertEqual(updated_project.project_name, "Updated Name")

#     def test_put_project_no_id(self):
#         json_data = json.dumps({"project_name": "Should Fail"})
#         request = self.factory.put('/Project', data=json_data, content_type='application/json')
#         response = Project_Registration(request)  # No ID
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(data['message'], 'Project ID is required')

#     def test_put_project_not_found(self):
#         request = self.factory.put('/Project/999', data=json.dumps({}), content_type='application/json')
#         response = Project_Registration(request, id=999)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(data['message'], 'Project not found')

#     def test_delete_project_success(self):
#         request = self.factory.delete(f'/Project/{self.project.project_id}')
#         response = Project_Registration(request, id=self.project.project_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['message'], 'Project Deleted Successfully')
#         self.assertFalse(Project.objects.filter(project_id=self.project.project_id).exists())

#     def test_delete_project_no_id(self):
#         request = self.factory.delete('/Project')
#         response = Project_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(data['message'], 'Project ID is required')

#     def test_delete_project_not_found(self):
#         request = self.factory.delete('/Project/999')
#         response = Project_Registration(request, id=999)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(data['message'], 'Project not found')

#     def test_invalid_method(self):
#         request = self.factory.patch('/Project')
#         response = Project_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertEqual(data['message'], 'Invalid request method')
    
    
    
    
    
    
# class TaskRegistrationTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create a user and project
#         self.user = MyUser.objects.create_user(username='tester', email='tester@example.com', password='test123', role='admin')
#         self.project = Project.objects.create(
#             project_name="Demo Project",
#             project_description="A test project",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#         self.task = Task.objects.create(
#             task_name="Sample Task",
#             task_description="Do something important",
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             created_by=self.user,
#             project=self.project,
#             is_high_priority=True
#         )

#     def test_get_tasks_success(self):
#         request = self.factory.get('/Task')
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], 'Success')

#     def test_get_tasks_exception(self):
#         with patch('adminapp.views.Task.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("DB error")
#             request = self.factory.get('/Task')
#             response = Task_Registration(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertEqual(data['message'], 'Internal Server Error')
#             self.assertTrue(data['hasError'])

#     def test_post_task_success(self):
#         payload = {
#             "project_name": self.project.project_id,
#             "task_name": "New Task",
#             "task_description": "A new task to test",
#             "is_high_priority": True,
#             "last_date": str(date.today())
#         }

#         request = self.factory.post('/Task', data=json.dumps(payload), content_type='application/json')
#         request.user_id = self.user.id
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['message'], "Task Added Successfully")
#         self.assertFalse(data['hasError'])

#     def test_post_task_missing_fields(self):
#         payload = {
#             "task_name": "Missing Fields"
#         }

#         request = self.factory.post('/Task', data=json.dumps(payload), content_type='application/json')
#         request.user_id = self.user.id
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(data['message'], "Missing required fields")
#         self.assertTrue(data['hasError'])

#     def test_post_task_exception(self):
#         with patch('adminapp.views.Task.save') as mock_save:
#             mock_save.side_effect = Exception("Save error")

#             payload = {
#                 "project_name": self.project.project_id,
#                 "task_name": "Boom",
#                 "task_description": "Crash",
#                 "is_high_priority": True,
#                 "last_date": str(date.today())
#             }

#             request = self.factory.post('/Task', data=json.dumps(payload), content_type='application/json')
#             request.user_id = self.user.id
#             response = Task_Registration(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertEqual(data['message'], "Failed to add task")
#             self.assertTrue(data['hasError'])

#     def test_put_task_success(self):
#         payload = {
#             "task_name": "Updated Task",
#             "task_description": "Updated description",
#             "is_high_priority": False,
#             "last_date": str(date.today()),
#             "project_name": self.project.project_id
#         }

#         request = self.factory.put(f'/Task/{self.task.task_id}', data=json.dumps(payload), content_type='application/json')
#         request.user_id = self.user.id
#         response = Task_Registration(request, id=self.task.task_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['message'], "Task Updated Successfully")

#     def test_put_task_no_id(self):
#         payload = {
#             "task_name": "No ID"
#         }

#         request = self.factory.put('/Task', data=json.dumps(payload), content_type='application/json')
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(data['message'], "Task ID is required")

#     def test_put_task_not_found(self):
#         request = self.factory.put('/Task/9999', data=json.dumps({}), content_type='application/json')
#         response = Task_Registration(request, id=9999)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(data['message'], "Task not found")

#     def test_delete_task_success(self):
#         request = self.factory.delete(f'/Task/{self.task.task_id}')
#         response = Task_Registration(request, id=self.task.task_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data['message'], "Task Deleted Successfully")
#         self.assertFalse(Task.objects.filter(task_id=self.task.task_id).exists())

#     def test_delete_task_no_id(self):
#         request = self.factory.delete('/Task')
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(data['message'], "Task ID is required")

#     def test_delete_task_not_found(self):
#         request = self.factory.delete('/Task/9999')
#         response = Task_Registration(request, id=9999)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(data['message'], "Task not found")

#     def test_invalid_method(self):
#         request = self.factory.patch('/Task')
#         response = Task_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertEqual(data['message'], "Invalid request method")
    
    
    
    
    
    
    
# class AllEmployeeViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         # Create some users
#         MyUser.objects.create_user(username="emp1", email="emp1@test.com", password="pass", role="employee")
#         MyUser.objects.create_user(username="emp2", email="emp2@test.com", password="pass", role="employee")
#         MyUser.objects.create_user(username="manager1", email="manager1@test.com", password="pass", role="manager")

#     def test_get_all_employees_success(self):
#         """Should return only users with role=employee"""
#         request = self.factory.get('/All_Employee')
#         response = All_Employee(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Success")
#         self.assertEqual(len(data['data']), 2)  # Only emp1 and emp2

#     def test_get_all_employees_exception(self):
#         """Should return 500 if DB query fails"""
#         with patch('adminapp.views.MyUser.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("DB error")
#             request = self.factory.get('/All_Employee')
#             response = All_Employee(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], "Internal Server Error")
#             self.assertIn("DB error", data['debugMessage'])

#     def test_all_employees_invalid_method(self):
#         """Should return 405 for unsupported methods"""
#         request = self.factory.post('/All_Employee', data={})
#         response = All_Employee(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Invalid request method")
    
    
    
    
    
    
# class TaskWithoutAssignViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create mock project and user if needed
#         self.project = Project.objects.create(
#             project_name="Project X",
#             project_description="Some description",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#         self.creator = MyUser.objects.create_user(
#             username="admin1",
#             email="admin1@example.com",
#             password="adminpass",
#             role="admin"
#         )

#         # Create tasks
#         Task.objects.create(
#             task_name="Task 1",
#             task_description="Description 1",
#             assigned_to=None,
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             project=self.project,
#             created_by=self.creator,
#             is_high_priority=False
#         )

#         Task.objects.create(
#             task_name="Task 2",
#             task_description="Description 2",
#             assigned_to=None,
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             project=self.project,
#             created_by=self.creator,
#             is_high_priority=True
#         )

#         Task.objects.create(
#             task_name="Task 3",
#             task_description="Description 3",
#             assigned_to=self.creator,
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             project=self.project,
#             created_by=self.creator,
#             is_high_priority=False
#         )

#     def test_get_task_without_assign_success(self):
#         """Test GET request for tasks without assignment"""
#         request = self.factory.get('/Task_Without_Assign')
#         response = Task_Without_Assign(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Success")
#         self.assertEqual(len(data['data']), 2)  # Only Task 1 and Task 2

#     def test_get_task_without_assign_exception(self):
#         """Test exception handling during task fetching"""
#         with patch('adminapp.views.Task.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("DB error")
#             request = self.factory.get('/Task_Without_Assign')
#             response = Task_Without_Assign(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], "Internal Server Error")
#             self.assertIn("DB error", data['debugMessage'])

#     def test_task_without_assign_invalid_method(self):
#         """Test invalid method (POST instead of GET)"""
#         request = self.factory.post('/Task_Without_Assign', data={})
#         response = Task_Without_Assign(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Invalid request method")
    
    
    
    
    
    
    
    
# class TaskWithAssignViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create project and user
#         self.project = Project.objects.create(
#             project_name="Alpha Project",
#             project_description="Test project description",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#         self.user = MyUser.objects.create_user(
#             username="employee1",
#             email="emp1@example.com",
#             password="testpass123",
#             role="employee"
#         )

#         self.creator = MyUser.objects.create_user(
#             username="admin1",
#             email="admin1@example.com",
#             password="adminpass",
#             role="admin"
#         )

#         # Create assigned task
#         Task.objects.create(
#             task_name="Assigned Task 1",
#             task_description="Important task",
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             project=self.project,
#             created_by=self.creator,
#             assigned_to=self.user,
#             is_high_priority=False
#         )

#         # Create unassigned task (should not show in result)
#         Task.objects.create(
#             task_name="Unassigned Task",
#             task_description="Free task",
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             project=self.project,
#             created_by=self.creator,
#             assigned_to=None,
#             is_high_priority=True
#         )

#     def test_get_task_with_assign_success(self):
#         """Test successful GET request for assigned tasks."""
#         request = self.factory.get('/Task_With_Assign')
#         response = Task_With_Assign(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Success")
#         self.assertEqual(len(data['data']), 1)  # Only 1 task is assigned
#         self.assertEqual(data['data'][0]['task_name'], "Assigned Task 1")

#     def test_get_task_with_assign_exception(self):
#         """Test DB error on GET request."""
#         with patch('adminapp.views.Task.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("Simulated DB error")

#             request = self.factory.get('/Task_With_Assign')
#             response = Task_With_Assign(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], "Internal Server Error")
#             self.assertIn("Simulated DB error", data['debugMessage'])

#     def test_task_with_assign_invalid_method(self):
#         """Test POST request (invalid method)."""
#         request = self.factory.post('/Task_With_Assign', data={})
#         response = Task_With_Assign(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Invalid request method")
    
    
    
    
    
    
    
    
    
    
# class UserTaskViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create test project and user
#         self.project = Project.objects.create(
#             project_name="Project X",
#             project_description="Some description",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#         self.employee = MyUser.objects.create_user(
#             username='testemployee',
#             email='employee@example.com',
#             password='testpass',
#             role='employee'
#         )

#         self.creator = MyUser.objects.create_user(
#             username='admin',
#             email='admin@example.com',
#             password='adminpass',
#             role='admin'
#         )

#         # Create a task assigned to the user
#         Task.objects.create(
#             project=self.project,
#             task_name="Task A",
#             task_description="Description A",
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             created_by=self.creator,
#             assigned_to=self.employee,
#             is_high_priority=False
#         )

#     def test_get_user_tasks_success(self):
#         """Test successful retrieval of user tasks."""
#         request = self.factory.get('/User_Task')
#         request.user_id = self.employee.id  # Mocked user_id

#         response = User_Task(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Success")
#         self.assertEqual(len(data['data']), 1)
#         self.assertEqual(data['data'][0]['task_name'], "Task A")

#     def test_get_user_tasks_missing_user_id(self):
#         """Test GET request without user_id in request."""
#         request = self.factory.get('/User_Task')

#         response = User_Task(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "User ID is required")

#     def test_get_user_tasks_exception(self):
#         """Test GET request with simulated DB error."""
#         with patch('adminapp.views.Task.objects.filter') as mock_filter:
#             mock_filter.side_effect = Exception("Simulated DB failure")

#             request = self.factory.get('/User_Task')
#             request.user_id = self.employee.id

#             response = User_Task(request)
#             data = json.loads(response.content)

#             self.assertEqual(response.status_code, 500)
#             self.assertTrue(data['hasError'])
#             self.assertEqual(data['message'], "Internal Server Error")
#             self.assertIn("Simulated DB failure", data['debugMessage'])

#     def test_invalid_request_method(self):
#         """Test POST method returns 405 error."""
#         request = self.factory.post('/User_Task', data={})
#         response = User_Task(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Invalid request method")
    
    
    
    
    
# class StatusUpdateViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create mock user and project
#         self.creator = MyUser.objects.create_user(
#             username='creator',
#             email='creator@example.com',
#             password='testpass',
#             role='admin'
#         )

#         self.project = Project.objects.create(
#             project_name='Project Alpha',
#             project_description='Testing project',
#             last_date=date.today(),
#             created_date=date.today()
#         )

#         # Create a task to update
#         self.task = Task.objects.create(
#             project=self.project,
#             task_name='Initial Task',
#             task_description='Task to be updated',
#             task_last_date=date.today(),
#             created_at=date.today(),
#             updated_at=date.today(),
#             created_by=self.creator,
#             assigned_to=None,
#             is_high_priority=False,
#             status='Pending'
#         )

#     def test_status_update_success(self):
#         """Test successful task status update."""
#         data = json.dumps({'taskstatus': 'Completed'}).encode('utf-8')
#         request = self.factory.put(f'/Status_Update/{self.task.task_id}', data=data, content_type='application/json')

#         response = Status_Update(request, self.task.task_id)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response_data['hasError'])
#         self.assertEqual(response_data['message'], "Task status updated successfully")

#         self.task.refresh_from_db()
#         self.assertEqual(self.task.status, 'Completed')

#     def test_status_update_task_not_found(self):
#         """Test task not found with given ID."""
#         fake_id = 999
#         data = json.dumps({'taskstatus': 'Completed'}).encode('utf-8')
#         request = self.factory.put(f'/Status_Update/{fake_id}', data=data, content_type='application/json')

#         response = Status_Update(request, fake_id)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertTrue(response_data['hasError'])
#         self.assertEqual(response_data['message'], "Task not found")

#     def test_status_update_missing_status(self):
#         """Test missing taskstatus field in request."""
#         data = json.dumps({}).encode('utf-8')
#         request = self.factory.put(f'/Status_Update/{self.task.task_id}', data=data, content_type='application/json')

#         response = Status_Update(request, self.task.task_id)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(response_data['hasError'])
#         self.assertEqual(response_data['message'], "Task status is required")

#     def test_status_update_invalid_method(self):
#         """Test using unsupported HTTP method (GET)."""
#         request = self.factory.get(f'/Status_Update/{self.task.task_id}')
#         response = Status_Update(request, self.task.task_id)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(response_data['hasError'])
#         self.assertEqual(response_data['message'], "Method Not Allowed")
    
    

# class WorkLogRegistrationTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         self.user = MyUser.objects.create_user(
#             username='employee',
#             email='employee@example.com',
#             password='pass123',
#             role='employee'
#         )

#         self.user_id = self.user.id

#     def test_get_work_logs_success(self):
#         """Test fetching work logs for a user."""
#         WorkLog.objects.create(
#             work_log_time=2,
#             work_log_description="Worked on module A",
#             created_by=self.user,
#             created_date=date.today()
#         )

#         request = self.factory.get('/Work_Log_Registration')
#         request.user_id = self.user_id

#         response = Work_Log_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Success")
#         self.assertGreaterEqual(len(data['data']), 1)

#     def test_post_work_log_success(self):
#         """Test successful creation of a work log."""
#         payload = {
#             "work_log_time": 3,
#             "work_log_description": "Worked on UI design"
#         }

#         json_data = json.dumps(payload).encode('utf-8')
#         request = self.factory.post('/Work_Log_Registration', data=json_data, content_type='application/json')
#         request.user_id = self.user_id

#         response = Work_Log_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(data['hasError'])
#         self.assertEqual(data['message'], "Work Log Added Successfully")
#         self.assertTrue(WorkLog.objects.filter(created_by=self.user).exists())

#     def test_post_missing_fields(self):
#         """Test missing fields in POST request."""
#         payload = {
#             "work_log_description": "Only description provided"
#         }

#         json_data = json.dumps(payload).encode('utf-8')
#         request = self.factory.post('/Work_Log_Registration', data=json_data, content_type='application/json')
#         request.user_id = self.user_id

#         response = Work_Log_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Missing required fields")

#     def test_post_exceeding_work_log_limit(self):
#         """Test when adding work log exceeds 8-hour daily limit."""
#         # Existing log with 7 hours
#         WorkLog.objects.create(
#             work_log_time=7,
#             work_log_description="Previous work",
#             created_by=self.user,
#             created_date=date.today()
#         )

#         payload = {
#             "work_log_time": 2,
#             "work_log_description": "Trying to exceed limit"
#         }

#         json_data = json.dumps(payload).encode('utf-8')
#         request = self.factory.post('/Work_Log_Registration', data=json_data, content_type='application/json')
#         request.user_id = self.user_id

#         response = Work_Log_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertIn("exceeds 8 hours", data['message'])

#     def test_invalid_method(self):
#         """Test using unsupported HTTP method."""
#         request = self.factory.put('/Work_Log_Registration')
#         request.user_id = self.user_id

#         response = Work_Log_Registration(request)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Method Not Allowed")






# class ProjectAssignTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create a user and a project
#         self.user = MyUser.objects.create_user(
#             username="testuser",
#             email="test@example.com",
#             password="testpass",
#             role="employee"
#         )
#         self.project = Project.objects.create(
#             project_name="Test Project",
#             project_description="A test project",
#             last_date=date.today(),
#             created_date=date.today()
#         )

#     def test_successful_project_assignment(self):
#         """Test successful assignment of a project to a user."""
#         data = {
#             "assigned_to": self.user.id
#         }
#         request = self.factory.put(
#             f"/Project_Assign/{self.project.project_id}",
#             data=json.dumps(data),
#             content_type="application/json"
#         )
#         response = Project_Assign(request, id=self.project.project_id)
#         response_data = json.loads(response.content)

#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(response_data['hasError'])
#         self.assertEqual(response_data['message'], "Project Assigned Successfully")

#     def test_missing_assigned_to(self):
#         """Test PUT request missing 'assigned_to' field."""
#         request = self.factory.put(
#             f"/Project_Assign/{self.project.project_id}",
#             data=json.dumps({}),
#             content_type="application/json"
#         )
#         response = Project_Assign(request, id=self.project.project_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 400)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "'assigned_to' is required")

#     def test_project_not_found(self):
#         """Test assignment to a non-existent project."""
#         request = self.factory.put(
#             "/Project_Assign/999",
#             data=json.dumps({"assigned_to": self.user.id}),
#             content_type="application/json"
#         )
#         response = Project_Assign(request, id=999)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Project not found")

#     def test_user_not_found(self):
#         """Test assignment with a non-existent user ID."""
#         request = self.factory.put(
#             f"/Project_Assign/{self.project.project_id}",
#             data=json.dumps({"assigned_to": 9999}),
#             content_type="application/json"
#         )
#         response = Project_Assign(request, id=self.project.project_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 404)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "User not found")

#     def test_invalid_method(self):
#         """Test using an unsupported HTTP method (GET)."""
#         request = self.factory.get(f"/Project_Assign/{self.project.project_id}")
#         response = Project_Assign(request, id=self.project.project_id)
#         data = json.loads(response.content)

#         self.assertEqual(response.status_code, 405)
#         self.assertTrue(data['hasError'])
#         self.assertEqual(data['message'], "Method Not Allowed")







# class AllManagerViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create sample users
#         MyUser.objects.create_user(username="manager1", email="manager1@example.com", password="testpass", role="manager")
#         MyUser.objects.create_user(username="manager2", email="manager2@example.com", password="testpass", role="manager")
#         MyUser.objects.create_user(username="employee1", email="employee1@example.com", password="testpass", role="employee")

#     def test_get_all_managers_success(self):
#         """Should return only users with role 'manager'"""
#         request = self.factory.get("/All_Manager/")
#         response = All_Manager(request)

#         self.assertEqual(response.status_code, 200)

#         data = json.loads(response.content)
#         self.assertFalse(data["hasError"])
#         self.assertEqual(len(data["data"]), 2)  # Only manager1 and manager2
#         self.assertEqual(data["message"], "Success")

#     def test_invalid_method(self):
#         """Should return 405 for unsupported methods like POST"""
#         request = self.factory.post("/All_Manager/")
#         response = All_Manager(request)

#         self.assertEqual(response.status_code, 405)

#         data = json.loads(response.content)
#         self.assertTrue(data["hasError"])
#         self.assertEqual(data["message"], "Method Not Allowed")







# class ProjectWithoutAssignViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create a user for testing
#         self.manager = MyUser.objects.create_user(username="manager1", email="manager@example.com", password="testpass", role="manager")

#         # Create some projects - assigned and unassigned
#         Project.objects.create(project_name="Unassigned Project 1", project_description="Desc 1", last_date="2025-05-01")
#         Project.objects.create(project_name="Unassigned Project 2", project_description="Desc 2", last_date="2025-05-02")
#         Project.objects.create(project_name="Assigned Project", project_description="Desc 3", last_date="2025-05-03", assigned_to=self.manager)

#     def test_get_unassigned_projects_success(self):
#         """Should return only unassigned projects"""
#         request = self.factory.get('/Project_Without_Assign/')
#         response = Project_Without_Assign(request)

#         self.assertEqual(response.status_code, 200)

#         data = json.loads(response.content)
#         self.assertFalse(data["hasError"])
#         self.assertEqual(len(data["data"]), 2)  # 2 unassigned projects
#         self.assertEqual(data["message"], "Success")

#     def test_invalid_method_returns_405(self):
#         """Should return 405 for methods other than GET"""
#         request = self.factory.post('/Project_Without_Assign/')
#         response = Project_Without_Assign(request)

#         self.assertEqual(response.status_code, 405)

#         data = json.loads(response.content)
#         self.assertTrue(data["hasError"])
#         self.assertEqual(data["message"], "Method Not Allowed")








# class ProjectWithAssignViewTests(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()

#         # Create test user
#         self.manager = MyUser.objects.create_user(
#             username="manager1", email="manager@example.com", password="pass123", role="manager"
#         )

#         # Create assigned and unassigned projects
#         Project.objects.create(
#             project_name="Assigned Project 1",
#             project_description="Assigned Description 1",
#             last_date="2025-05-01",
#             assigned_to=self.manager
#         )
#         Project.objects.create(
#             project_name="Unassigned Project",
#             project_description="Unassigned Description",
#             last_date="2025-05-02"
#         )

#     def test_get_projects_with_assign_success(self):
#         """Test GET request returns only assigned projects."""
#         request = self.factory.get('/Project_With_Assign/')
#         response = Project_With_Assign(request)

#         self.assertEqual(response.status_code, 200)

#         data = json.loads(response.content)
#         self.assertFalse(data["hasError"])
#         self.assertEqual(data["message"], "Success")
#         self.assertEqual(len(data["data"]), 1)  # Only one assigned project

#     def test_invalid_method_returns_405(self):
#         """Test that non-GET method returns 405 Method Not Allowed."""
#         request = self.factory.post('/Project_With_Assign/')
#         response = Project_With_Assign(request)

#         self.assertEqual(response.status_code, 405)

#         data = json.loads(response.content)
#         self.assertTrue(data["hasError"])
#         self.assertEqual(data["message"], "Method Not Allowed")
