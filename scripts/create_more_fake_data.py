import os
import sys
import django
import random
from datetime import date, datetime, timedelta

# 將專案根目錄加入 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

from employee.models import Department, Employee, Salary, Punch, Leave

def create_more_fake_employees():
    """創建更多假員工資料"""
    
    # 確保部門存在
    departments = {
        '研發部': None,
        '行銷部': None,
        '人資部': None,
        '財務部': None,
        '客服部': None,
        '產品部': None,
        '設計部': None,
    }
    
    for dept_name in departments:
        department, created = Department.objects.get_or_create(name=dept_name)
        departments[dept_name] = department
        if created:
            print(f"已建立部門: {dept_name}")
        else:
            print(f"使用現有部門: {dept_name}")
    
    # 新員工資料
    new_employees = [
        {
            'name': '王大明',
            'email': 'daming.wang@example.com',
            'phone': '0987654321',
            'department': departments['研發部'],
            'hire_date': date(2024, 1, 15),
            'base_salary': 52000.00,
            'bonus': 5000.00
        },
        {
            'name': '張美麗',
            'email': 'meili.zhang@example.com',
            'phone': '0976543210',
            'department': departments['行銷部'],
            'hire_date': date(2024, 2, 1),
            'base_salary': 48000.00,
            'bonus': 4000.00
        },
        {
            'name': '李志豪',
            'email': 'zhihao.li@example.com',
            'phone': '0965432109',
            'department': departments['設計部'],
            'hire_date': date(2023, 12, 10),
            'base_salary': 50000.00,
            'bonus': 4500.00
        },
        {
            'name': '陳雅婷',
            'email': 'yating.chen@example.com',
            'phone': '0954321098',
            'department': departments['人資部'],
            'hire_date': date(2024, 3, 5),
            'base_salary': 46000.00,
            'bonus': 3800.00
        },
        {
            'name': '林建國',
            'email': 'jianguo.lin@example.com',
            'phone': '0943210987',
            'department': departments['財務部'],
            'hire_date': date(2023, 11, 20),
            'base_salary': 55000.00,
            'bonus': 6000.00
        },
        {
            'name': '黃小琳',
            'email': 'xiaolin.huang@example.com',
            'phone': '0932109876',
            'department': departments['客服部'],
            'hire_date': date(2024, 4, 1),
            'base_salary': 42000.00,
            'bonus': 3000.00
        },
        {
            'name': '吳俊宏',
            'email': 'junhong.wu@example.com',
            'phone': '0921098765',
            'department': departments['產品部'],
            'hire_date': date(2023, 10, 15),
            'base_salary': 53000.00,
            'bonus': 5500.00
        },
        {
            'name': '趙雨晴',
            'email': 'yuqing.zhao@example.com',
            'phone': '0910987654',
            'department': departments['設計部'],
            'hire_date': date(2024, 5, 2),
            'base_salary': 47000.00,
            'bonus': 4200.00
        },
        {
            'name': '郭偉誠',
            'email': 'weicheng.guo@example.com',
            'phone': '0909876543',
            'department': departments['研發部'],
            'hire_date': date(2023, 9, 25),
            'base_salary': 54000.00,
            'bonus': 5800.00
        },
        {
            'name': '許芳瑜',
            'email': 'fangyu.xu@example.com',
            'phone': '0898765432',
            'department': departments['行銷部'],
            'hire_date': date(2024, 6, 10),
            'base_salary': 45000.00,
            'bonus': 3500.00
        }
    ]
    
    created_employees = []
    
    for emp_data in new_employees:
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
    
    return created_employees

def is_workday(day):
    """判斷是否為工作日（星期一至星期五）"""
    return day.weekday() < 5  # 0-4是週一至週五

def is_holiday(day):
    """判斷是否為台灣法定假日（簡易版本，僅考慮主要假日）"""
    holidays = [
        # 2025年假日
        date(2025, 1, 1),    # 元旦
        date(2025, 2, 28),   # 和平紀念日
        date(2025, 4, 4),    # 兒童節
        date(2025, 5, 1),    # 勞動節
        date(2025, 6, 19),   # 端午節
        date(2025, 9, 9),    # 中秋節
        date(2025, 10, 10),  # 國慶日
    ]
    return day in holidays

def generate_detailed_punch_records(employees):
    """為指定的員工生成詳細的兩個月打卡記錄，使用正常的上下班時間"""
    
    # 獲取現在的日期和兩個月前的日期
    today = date.today()
    two_months_ago = today - timedelta(days=60)
    
    print(f"正在生成從 {two_months_ago} 到 {today} 的打卡記錄...")
    
    total_records = 0
    
    # 針對每位員工產生打卡記錄
    for employee in employees:
        # 從兩個月前開始，直到今天
        current_date = two_months_ago
        while current_date <= today:
            # 僅在工作日（週一至週五）且非法定假日時產生打卡記錄
            if is_workday(current_date) and not is_holiday(current_date):
                # 一般情況 (80%) - 正常上下班時間
                if random.random() < 0.8:
                    # 上班時間：08:30 - 09:00
                    punch_in_hour = 8
                    punch_in_minute = random.randint(30, 59)
                    
                    # 下班時間：17:30 - 18:30
                    punch_out_hour = random.choice([17, 18])
                    punch_out_minute = random.randint(30, 59) if punch_out_hour == 17 else random.randint(0, 30)
                    
                # 特殊情況 (20%) - 可能稍晚到或提早走
                else:
                    # 上班時間：有10%機率遲到 (9:00-9:30)，90%正常 (8:30-9:00)
                    is_late = random.random() < 0.1
                    if is_late:
                        punch_in_hour = 9
                        punch_in_minute = random.randint(0, 30)
                    else:
                        punch_in_hour = 8
                        punch_in_minute = random.randint(30, 59)
                    
                    # 下班時間：有15%機率早退 (16:30-17:30)，85%正常或加班 (17:30-19:00)
                    leaves_early = random.random() < 0.15
                    if leaves_early:
                        punch_out_hour = random.choice([16, 17])
                        punch_out_minute = random.randint(30, 59) if punch_out_hour == 16 else random.randint(0, 30)
                    else:
                        punch_out_hour = random.choice([17, 18])
                        punch_out_minute = random.randint(30, 59)
                
                # 創建上班打卡時間
                punch_in_time = datetime.combine(
                    current_date,
                    datetime.min.time()
                ).replace(hour=punch_in_hour, minute=punch_in_minute)
                
                # 創建下班打卡時間
                punch_out_time = datetime.combine(
                    current_date,
                    datetime.min.time()
                ).replace(hour=punch_out_hour, minute=punch_out_minute)
                
                # 偶爾有員工可能會忘記打卡 (約5%的機率)
                forgot_to_punch = random.random() < 0.05
                
                if not forgot_to_punch:
                    # 創建上班打卡記錄
                    Punch.objects.create(
                        employee=employee,
                        punch_time=punch_in_time,
                        punch_type='IN'
                    )
                    total_records += 1
                    
                    # 創建下班打卡記錄
                    Punch.objects.create(
                        employee=employee,
                        punch_time=punch_out_time,
                        punch_type='OUT'
                    )
                    total_records += 1
            
            # 進入下一天
            current_date += timedelta(days=1)
    
    print(f"已為 {len(employees)} 位員工生成 {total_records} 筆打卡記錄")

if __name__ == "__main__":
    # 1. 建立更多員工資料
    new_employees = create_more_fake_employees()
    
    # 2. 為這些員工生成詳細的打卡記錄
    # 首先獲取所有員工
    all_employees = Employee.objects.all()
    
    # 檢查是否要清除現有打卡記錄
    clear_existing = input("是否清除現有打卡記錄？(y/n): ").strip().lower() == 'y'
    
    if clear_existing:
        count = Punch.objects.all().count()
        Punch.objects.all().delete()
        print(f"已清除 {count} 筆現有打卡記錄")
    
    # 生成打卡記錄
    generate_detailed_punch_records(all_employees)
    
    print("假資料生成完成！")
