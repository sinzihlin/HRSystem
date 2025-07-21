#!/usr/bin/env python
"""
HR 薪資系統功能展示腳本
展示最新版本的智能薪資管理功能
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

def show_system_overview():
    """展示系統概況"""
    print("🏢 HR 薪資管理系統 v2.1.0")
    print("=" * 50)
    
    # 統計資料
    employees_count = Employee.objects.filter(active=True).count()
    periods_count = PayrollPeriod.objects.count()
    salary_items_count = SalaryItem.objects.count()
    
    print(f"👥 活躍員工數量: {employees_count}")
    print(f"📅 薪資期間數量: {periods_count}")
    print(f"💰 薪資項目數量: {salary_items_count}")
    print()

def demo_salary_calculation():
    """展示薪資計算功能"""
    print("🧮 智能薪資計算展示")
    print("-" * 30)
    
    service = SalaryCalculationService()
    
    # 獲取測試員工
    employee = Employee.objects.filter(active=True).first()
    if not employee:
        print("❌ 沒有找到測試員工")
        return
    
    # 獲取或創建測試期間
    period, created = PayrollPeriod.objects.get_or_create(
        start_date=date(2025, 7, 1),
        end_date=date(2025, 7, 31),
        defaults={'pay_date': date(2025, 8, 5)}
    )
    
    print(f"👤 員工: {employee.name}")
    print(f"📅 期間: {period.start_date} ~ {period.end_date}")
    print(f"💼 職類: {'正職' if employee.employment_type == 'FT' else '兼職'}")
    print()
    
    # 計算薪資
    salary = service.calculate_salary_for_period(employee, period)
    
    print("💰 薪資計算結果:")
    print(f"   基本薪資: NT$ {salary.base_amount:,.0f}")
    print(f"   工作時數: {salary.working_hours:.1f} 小時")
    print(f"   加班時數: {salary.overtime_hours:.1f} 小時")
    print(f"   加班費: NT$ {salary.overtime_amount:,.0f}")
    print(f"   總薪資: NT$ {salary.total_salary:,.0f}")
    print()

def demo_leave_deduction():
    """展示請假扣款功能"""
    print("📉 請假扣款功能展示")
    print("-" * 30)
    
    service = SalaryCalculationService()
    employee = Employee.objects.filter(active=True).first()
    
    if not employee:
        return
    
    # 創建測試請假記錄
    period = PayrollPeriod.objects.first()
    if not period:
        return
    
    # 清除舊的測試請假記錄
    Leave.objects.filter(employee=employee, leave_type='PERSONAL').delete()
    
    # 創建事假記錄
    leave = Leave.objects.create(
        employee=employee,
        leave_type='PERSONAL',
        start_date=date(2025, 7, 10),
        end_date=date(2025, 7, 11),
        status='APPROVED',
        reason='個人事務處理'
    )
    
    # 計算請假扣款
    deduction = service._calculate_leave_deduction(employee, period)
    
    print(f"📝 請假記錄: {leave.get_leave_type_display()}")
    print(f"📅 請假日期: {leave.start_date} ~ {leave.end_date}")
    print(f"📊 扣薪天數: {deduction['unpaid_days']} 天")
    print(f"💸 扣款金額: NT$ {deduction['total_amount']:,.0f}")
    print(f"📋 詳細說明: {deduction['details']}")
    print()

def demo_overtime_calculation():
    """展示加班費計算功能"""
    print("🕒 加班費計算功能展示")
    print("-" * 30)
    
    service = SalaryCalculationService()
    employee = Employee.objects.filter(active=True).first()
    
    if not employee:
        return
    
    # 測試不同日期的加班費倍率
    test_dates = [
        (date(2025, 7, 15), "平日"),  # 週二
        (date(2025, 7, 19), "週末"),  # 週六
        (date(2025, 1, 1), "國定假日"),   # 元旦
    ]
    
    for test_date, date_type in test_dates:
        is_holiday = service._is_holiday(test_date)
        overtime_rate = service._get_overtime_rate(employee, test_date, True)
        
        print(f"📅 {test_date} ({date_type})")
        print(f"   假日判定: {'是' if is_holiday else '否'}")
        print(f"   加班倍率: {overtime_rate}倍")
        print()

def demo_salary_items():
    """展示薪資項目功能"""
    print("📋 薪資項目管理展示")
    print("-" * 30)
    
    # 顯示各類薪資項目
    categories = {
        'ALLOWANCE': '加給項目',
        'BONUS': '獎金項目', 
        'DEDUCTION': '扣除項目'
    }
    
    for item_type, type_name in categories.items():
        items = SalaryItem.objects.filter(item_type=item_type)
        print(f"💼 {type_name}:")
        
        for item in items:
            if item.amount:
                amount_str = f"NT$ {item.amount:,.0f}"
            elif item.percentage:
                amount_str = f"{item.percentage}%"
            else:
                amount_str = "未設定"
            
            print(f"   • {item.name}: {amount_str}")
        print()

def main():
    """主程序"""
    print("🚀 HR 薪資管理系統 - 功能展示")
    print("=" * 50)
    print()
    
    try:
        show_system_overview()
        demo_salary_calculation()
        demo_leave_deduction()
        demo_overtime_calculation() 
        demo_salary_items()
        
        print("✅ 功能展示完成！")
        print()
        print("🌟 系統特色:")
        print("   • 全自動請假扣款計算")
        print("   • 精確的加班費計算")
        print("   • 智能稅務處理")
        print("   • 即時薪資預覽")
        print("   • 直觀的管理介面")
        
    except Exception as e:
        print(f"❌ 執行過程中發生錯誤: {e}")

if __name__ == '__main__':
    main()
