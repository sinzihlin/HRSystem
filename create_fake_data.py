import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

from employee.models import Department, Employee, Salary, Punch, Leave
from datetime import date, datetime, timedelta
import random

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
        'bonus': 5000.00
    },
    {
        'name': '李小花',
        'email': 'xiaohua.li@example.com',
        'phone': '0923456789',
        'department': created_departments[0],  # 研發部
        'hire_date': date(2023, 3, 1),
        'base_salary': 48000.00,
        'bonus': 4800.00
    },
    {
        'name': '張大為',
        'email': 'dawei.zhang@example.com',
        'phone': '0934567890',
        'department': created_departments[1],  # 行銷部
        'hire_date': date(2022, 11, 5),
        'base_salary': 52000.00,
        'bonus': 5200.00
    },
    {
        'name': '陳美玲',
        'email': 'meiling.chen@example.com',
        'phone': '0945678901',
        'department': created_departments[2],  # 人資部
        'hire_date': date(2022, 8, 10),
        'base_salary': 55000.00,
        'bonus': 5500.00
    },
    {
        'name': '林志明',
        'email': 'zhiming.lin@example.com',
        'phone': '0956789012',
        'department': created_departments[3],  # 財務部
        'hire_date': date(2022, 5, 20),
        'base_salary': 60000.00,
        'bonus': 6000.00
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
            hire_date=emp_data['hire_date']
        )
        print(f"已建立員工: {employee.name}")

        # 為員工新增薪資紀錄
        salary = Salary.objects.create(
            employee=employee,
            base_salary=emp_data['base_salary'],
            bonus=emp_data['bonus'],
            deductions=emp_data['base_salary'] * 0.02,  # 假設扣除2%作為扣款
            pay_date=date.today()
        )
        print(f"已為 {employee.name} 新增薪資紀錄，總薪資: {salary.total_salary}")
        
        created_employees.append(employee)
    else:
        employee = Employee.objects.get(email=emp_data['email'])
        print(f"員工 {emp_data['name']} 已存在，跳過建立")
        created_employees.append(employee)

# 產生兩個月的打卡紀錄
def generate_punch_records():
    # 清空現有的打卡記錄，以避免重複
    Punch.objects.all().delete()
    print("已清空現有打卡記錄")
    
    # 獲取目前日期並計算兩個月前的日期
    today = date.today()
    two_months_ago = today - timedelta(days=60)
    
    total_records = 0
    
    # 針對每位員工產生打卡記錄
    for employee in created_employees:
        # 從兩個月前開始，直到今天
        current_date = two_months_ago
        while current_date <= today:
            # 跳過週末 (週六=5, 週日=6)
            if current_date.weekday() < 5:  # 只有工作日才打卡
                # 上班打卡時間：08:30 到 09:30 之間的隨機時間
                punch_in_hour = 8
                punch_in_minute = random.randint(30, 59) if punch_in_hour == 8 else random.randint(0, 30)
                punch_in_time = datetime.combine(
                    current_date, 
                    datetime.min.time()
                ).replace(hour=punch_in_hour, minute=punch_in_minute)
                
                # 創建上班打卡記錄
                Punch.objects.create(
                    employee=employee,
                    punch_time=punch_in_time,
                    punch_type='IN'
                )
                total_records += 1
                
                # 下班打卡時間：17:30 到 19:00 之間的隨機時間
                punch_out_hour = random.randint(17, 18)
                punch_out_minute = random.randint(30, 59)
                punch_out_time = datetime.combine(
                    current_date, 
                    datetime.min.time()
                ).replace(hour=punch_out_hour, minute=punch_out_minute)
                
                # 創建下班打卡記錄
                Punch.objects.create(
                    employee=employee,
                    punch_time=punch_out_time,
                    punch_type='OUT'
                )
                total_records += 1
                
            # 前進一天
            current_date += timedelta(days=1)
    
    print(f"已為所有員工生成 {total_records} 筆打卡記錄")

# 產生請假記錄
def generate_leave_records():
    # 清空現有的請假記錄，以避免重複
    Leave.objects.all().delete()
    print("已清空現有請假記錄")
    
    # 請假類型
    leave_types = [
        'ANNUAL', 'SICK', 'PERSONAL', 'COMPENSATORY'
    ]
    
    # 請假狀態
    statuses = ['PENDING', 'APPROVED', 'REJECTED']
    
    total_leaves = 0
    
    # 針對每位員工產生1-3筆請假記錄
    for employee in created_employees:
        # 隨機決定請假次數 (1-3次)
        num_leaves = random.randint(1, 3)
        
        for _ in range(num_leaves):
            # 隨機挑選請假類型
            leave_type = random.choice(leave_types)
            
            # 隨機決定請假開始日期 (最近30天內)
            days_ago = random.randint(1, 30)
            start_date = date.today() - timedelta(days=days_ago)
            
            # 隨機決定請假天數 (1-5天)
            leave_days = random.randint(1, 5)
            end_date = start_date + timedelta(days=leave_days - 1)
            
            # 隨機決定請假狀態，根據開始日期自動決定
            if start_date > date.today():  # 未來的請假通常是待審核
                status = 'PENDING'
            else:  # 過去的請假可能已審核
                status = random.choice(statuses)
            
            # 請假原因
            reasons = [
                '身體不適，需要休息',
                '家中有事需要處理',
                '個人休假',
                '參加家人婚禮',
                '外地旅行',
                ''  # 空白原因
            ]
            reason = random.choice(reasons)
            
            # 建立請假記錄
            Leave.objects.create(
                employee=employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                status=status,
                applied_date=start_date - timedelta(days=random.randint(1, 5))  # 請假日期前1-5天申請
            )
            total_leaves += 1
    
    print(f"已為所有員工生成 {total_leaves} 筆請假記錄")

# 執行產生打卡記錄和請假記錄的函數
generate_punch_records()
generate_leave_records()

print("資料生成完成！")
