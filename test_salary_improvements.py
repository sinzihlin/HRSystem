#!/usr/bin/env python
"""
測試薪資系統改進功能
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

from employee.models import Employee, PayrollPeriod, Leave, SalaryItem
from employee.services import SalaryCalculationService

def test_salary_improvements():
    print("🧪 開始測試薪資系統改進功能...")
    
    # 1. 測試薪資項目創建
    print("\n1️⃣ 測試薪資項目創建...")
    service = SalaryCalculationService()
    created_items = service.create_default_salary_items()
    print(f"   ✓ 成功創建 {len(created_items)} 個預設薪資項目")
    
    # 2. 檢查薪資項目
    print("\n2️⃣ 檢查薪資項目...")
    items = SalaryItem.objects.all()
    for item in items:
        print(f"   📋 {item.name} ({item.get_item_type_display()}) - {item.description}")
    
    # 3. 測試請假扣款計算
    print("\n3️⃣ 測試請假扣款計算...")
    
    # 創建測試期間
    period, created = PayrollPeriod.objects.get_or_create(
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 31),
        defaults={'pay_date': date(2025, 8, 5)}
    )
    print(f"   📅 薪資期間: {period}")
    
    # 獲取員工進行測試
    employees = Employee.objects.filter(active=True)[:2]
    
    for employee in employees:
        print(f"\n   👤 測試員工: {employee.name}")
        
        # 創建測試請假記錄
        Leave.objects.filter(employee=employee).delete()  # 清除舊記錄
        
        # 創建事假記錄（需要扣薪）
        leave = Leave.objects.create(
            employee=employee,
            leave_type='PERSONAL',
            start_date=date(2025, 7, 15),
            end_date=date(2025, 7, 16),
            status='APPROVED',
            reason='個人事務'
        )
        print(f"   📝 創建請假記錄: {leave}")
        
        # 測試請假扣款計算
        leave_deduction = service._calculate_leave_deduction(employee, period)
        print(f"   💰 請假扣款: NT$ {leave_deduction['total_amount']}")
        print(f"   📊 扣薪天數: {leave_deduction['unpaid_days']} 天")
        print(f"   📋 扣款詳情: {leave_deduction['details']}")
        
        # 測試完整薪資計算
        salary = service.calculate_salary_for_period(employee, period)
        print(f"   🧮 薪資計算完成:")
        print(f"      基本薪資: NT$ {salary.base_amount}")
        print(f"      加班費: NT$ {salary.overtime_amount}")
        print(f"      總薪資: NT$ {salary.total_salary}")
        
        # 顯示薪資明細
        details = salary.salarydetail_set.all()
        if details:
            print(f"   📄 薪資明細:")
            for detail in details:
                print(f"      {detail.item.name}: NT$ {detail.amount}")
    
    # 4. 測試假日加班費計算
    print("\n4️⃣ 測試假日加班費計算...")
    test_dates = [
        date(2025, 7, 5),   # 週六
        date(2025, 7, 6),   # 週日
        date(2025, 1, 1),   # 元旦
        date(2025, 7, 15),  # 平日
    ]
    
    for test_date in test_dates:
        is_holiday = service._is_holiday(test_date)
        overtime_rate = service._get_overtime_rate(employees[0], test_date, True)
        print(f"   📅 {test_date}: 假日={is_holiday}, 加班倍率={overtime_rate}")
    
    print("\n✅ 薪資系統改進功能測試完成！")

def test_calculation_preview():
    print("\n🔍 測試薪資計算預覽功能...")
    
    service = SalaryCalculationService()
    employees = Employee.objects.filter(active=True).first()
    period = PayrollPeriod.objects.first()
    
    if employees and period:
        # 模擬預覽計算
        base_amount = service._calculate_base_salary(employees, period)
        working_hours, overtime_hours, overtime_amount = service._calculate_work_hours_and_overtime(employees, period)
        leave_deduction = service._calculate_leave_deduction(employees, period)
        
        print(f"   👤 員工: {employees.name}")
        print(f"   📅 期間: {period}")
        print(f"   💰 基本薪資: NT$ {base_amount}")
        print(f"   ⏰ 工作時數: {working_hours} 小時")
        print(f"   🕒 加班時數: {overtime_hours} 小時")
        print(f"   💸 加班費: NT$ {overtime_amount}")
        print(f"   📉 請假扣款: NT$ {leave_deduction['total_amount']}")
        
        print("   ✓ 預覽功能正常運作")
    else:
        print("   ⚠️ 沒有找到測試數據")

if __name__ == '__main__':
    test_salary_improvements()
    test_calculation_preview()
