import os
import django
import random
from datetime import date, datetime, timedelta

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

from django.utils import timezone
from employee.models import Department, Employee, Salary, Punch, Leave

def create_punch_records():
    """創建正確日期時間的打卡記錄"""
    
    # 清除現有打卡記錄
    count = Punch.objects.all().count()
    Punch.objects.all().delete()
    print(f"已清除 {count} 筆現有打卡記錄")
    
    # 獲取現在的日期和兩個月前的日期
    today = date.today()
    two_months_ago = today - timedelta(days=60)
    
    print(f"正在生成從 {two_months_ago} 到 {today} 的打卡記錄...")
    
    # 獲取所有員工
    employees = Employee.objects.all()
    total_records = 0
    
    # 針對每位員工產生打卡記錄
    for employee in employees:
        # 從兩個月前開始，直到今天
        current_date = two_months_ago
        while current_date <= today:
            # 僅在工作日（週一至週五）時產生打卡記錄
            if current_date.weekday() < 5:  # 0-4是週一至週五
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
                
                # 將 datetime 物件轉換為帶有時區資訊的 datetime 物件
                punch_in_time = timezone.make_aware(punch_in_time)
                punch_out_time = timezone.make_aware(punch_out_time)
                
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
    
    print(f"已為 {employees.count()} 位員工生成 {total_records} 筆打卡記錄")
    return total_records

if __name__ == "__main__":
    # 執行打卡記錄生成
    total_records = create_punch_records()
    print(f"總共生成了 {total_records} 筆打卡記錄")
    print("完成！")
