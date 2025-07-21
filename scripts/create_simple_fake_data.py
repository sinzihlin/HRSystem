import os
import sys
import django

# 將專案根目錄加入 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

from employee.models import Department, Employee
from datetime import date

# 建立部門
departments = [
    '研發部',
    '行銷部',
    '人資部',
    '財務部',
    '客服部'
]

created_departments = []
for dept_name in departments:
    department, created = Department.objects.get_or_create(name=dept_name)
    if created:
        print(f"已建立部門: {dept_name}")
    else:
        print(f"{dept_name} 已存在")
    created_departments.append(department)

# 建立員工資料
employees_data = [
    {
        'name': '王小明',
        'email': 'xiaoming.wang@example.com',
        'phone': '0912345678',
        'department': created_departments[0],  # 研發部
        'hire_date': date(2023, 1, 15),
        'base_salary': 50000.00,
        'employment_type': 'FT'
    },
    {
        'name': '張大偉',
        'email': 'dawei.zhang@example.com',
        'phone': '0934567890',
        'department': created_departments[1],  # 行銷部
        'hire_date': date(2022, 11, 5),
        'base_salary': 52000.00,
        'employment_type': 'FT'
    },
    {
        'name': '陳美玲',
        'email': 'meiling.chen@example.com',
        'phone': '0945678901',
        'department': created_departments[2],  # 人資部
        'hire_date': date(2022, 8, 10),
        'base_salary': 55000.00,
        'employment_type': 'FT'
    },
    {
        'name': '林志明',
        'email': 'zhiming.lin@example.com',
        'phone': '0956789012',
        'department': created_departments[3],  # 財務部
        'hire_date': date(2022, 5, 20),
        'base_salary': 60000.00,
        'employment_type': 'FT'
    },
    {
        'name': '黃小華',
        'email': 'xiaohua.huang@example.com',
        'phone': '0967890123',
        'department': created_departments[4],  # 客服部
        'hire_date': date(2023, 3, 8),
        'hourly_rate': 200.00,
        'employment_type': 'PT'
    },
]

created_employees = []
for emp_data in employees_data:
    # 檢查該員工是否已存在
    if not Employee.objects.filter(email=emp_data['email']).exists():
        employee = Employee.objects.create(
            name=emp_data['name'],
            email=emp_data['email'],
            phone=emp_data['phone'],
            department=emp_data['department'],
            hire_date=emp_data['hire_date'],
            employment_type=emp_data['employment_type'],
            base_salary=emp_data.get('base_salary'),
            hourly_rate=emp_data.get('hourly_rate')
        )
        print(f"已建立員工: {employee.name} ({employee.get_employment_type_display()})")
        created_employees.append(employee)
    else:
        existing_employee = Employee.objects.get(email=emp_data['email'])
        print(f"{existing_employee.name} 已存在")
        created_employees.append(existing_employee)

print(f"總共處理了 {len(created_employees)} 名員工")
