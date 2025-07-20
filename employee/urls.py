from django.urls import path
from . import views

urlpatterns = [
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('api/employees/import/', views.import_employees_api, name='import_employees_api'),
    path('api/punch/', views.punch_api, name='punch_api'),
    path('api/leave/', views.leave_api, name='leave_api'),
    path('api/leaves/pending/', views.get_pending_leaves_api, name='get_pending_leaves_api'),
    path('api/leaves/update_status/', views.update_leave_status_api, name='update_leave_status_api'),
]