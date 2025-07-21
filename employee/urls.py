from django.urls import path
from django.views.generic.base import RedirectView
from . import views
from . import salary_views

urlpatterns = [
    path('', RedirectView.as_view(url='salary/', permanent=False), name='index'),
    
    # 認證相關
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # 薪資系統相關
    path('salary/', salary_views.SalaryListView.as_view(), name='salary_list'),
    path('salary/<int:pk>/', salary_views.SalaryDetailView.as_view(), name='salary_detail'),
    path('salary/export/', salary_views.salary_export, name='salary_export'),
    path('payroll/', salary_views.PayrollManagementView.as_view(), name='payroll_management'),
    path('salary-items/', salary_views.SalaryItemManagementView.as_view(), name='salary_item_management'),
    
    # 員工相關 API
    path('api/employees/import/', views.import_employees_api, name='import_employees_api'),
    path('api/punch/', views.punch_api, name='punch_api'),
    path('api/leave/', views.leave_api, name='leave_api'),
    path('api/leaves/pending/', views.get_pending_leaves_api, name='get_pending_leaves_api'),
    path('api/leaves/update_status/', views.update_leave_status_api, name='update_leave_status_api'),
    path('employees/<int:employee_id>/punches/', views.employee_punches_view, name='employee_punches'),
    
    # 薪資相關 API
    path('api/payroll/periods/create/', salary_views.create_payroll_period, name='create_payroll_period'),
    path('api/payroll/process/', salary_views.process_payroll, name='process_payroll'),
    path('api/salary/calculate/', salary_views.calculate_single_salary, name='calculate_single_salary'),
    path('api/salary/preview/', salary_views.salary_calculation_preview, name='salary_calculation_preview'),
    path('api/salary/chart-data/', salary_views.salary_chart_data, name='salary_chart_data'),
    path('api/salary/summary/<int:employee_id>/', salary_views.salary_summary_api, name='salary_summary_api'),
    path('api/salary/employee-data/', salary_views.get_employee_salary_data, name='get_employee_salary_data'),
    path('api/salary-items/create/', salary_views.create_salary_item, name='create_salary_item'),
    
    # 系統相關
    path('api/health/', views.health_check, name='health_check'),
]