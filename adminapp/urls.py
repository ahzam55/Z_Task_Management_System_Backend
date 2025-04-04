from django.urls import path
from adminapp import views






urlpatterns =[

    path('Signin/', views.Signin, name='Signin'),
    path('Manager/', views.Manager, name='Manager'),
    path('Employee/', views.Employee, name='Employee'),
    # path('api/token/refresh/',refresh_token, name='token_refresh'),
    # path('student/<int:id>', views.student, name='student'),
    # path('student/<id>', views.student, name='student'),  
    path('Project_Registration/', views.Project_Registration, name='Project_Registration'),
    path('Project_Registration/<int:id>', views.Project_Registration, name='Project_Registration'),
    path('Project_Registration/<id>', views.Project_Registration, name='Project_Registration'),
    path('Task_Registration/', views.Task_Registration, name='Task_Registration'),
    path('Task_Registration/<int:id>', views.Task_Registration, name='Task_Registration'),
    path('Task_Registration/<id>', views.Task_Registration, name='Task_Registration'),
    path('All_Employee/', views.All_Employee, name='All_Employee'),
    path('Task_Assign/<id>', views.Task_Assign, name='Task_Assign'),
    path('Task_Without_Assign/', views.Task_Without_Assign, name='Task_Without_Assign'),
    path('Task_With_Assign/', views.Task_With_Assign, name='Task_With_Assign'),
    path('User_Task/', views.User_Task, name='User_Task'),
    path('Status_Update/<id>', views.Status_Update, name='Status_Update'),
    path('Work_Log_Registration/', views.Work_Log_Registration, name='Work_Log_Registration'),
    path('Project_Assign/<id>', views.Project_Assign, name='Project_Assign'),
    path('All_Manager/', views.All_Manager, name='All_Manager'),
    path('Project_Without_Assign/', views.Project_Without_Assign, name='Project_Without_Assign'),
    path('Project_With_Assign/', views.Project_With_Assign, name='Project_With_Assign'),
    path('Manager_Project/', views.Manager_Project, name='Manager_Project'),
    path('Task_Report/', views.Task_Report, name='Task_Report'),
    path('Performance_Report/', views.Performance_Report, name='Performance_Report'),
    path('Task_View/', views.Task_View, name='Task_View'),
    path('Task_Report_View/', views.Task_Report_View, name='Task_Report_View'),
] 