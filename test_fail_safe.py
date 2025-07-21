#!/usr/bin/env python3
"""
HR 系統防呆測試腳本
用於測試各種故障場景並驗證錯誤處理機制
"""
import os
import sys
import django
import shutil
from datetime import datetime

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HRSystem.settings')
django.setup()

def test_database_scenarios():
    """測試不同的資料庫場景"""
    print("🧪 開始進行防呆測試...")
    print("=" * 50)
    
    # 1. 備份原始資料庫
    db_path = 'db.sqlite3'
    backup_path = 'db.sqlite3.test_backup'
    
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print("✅ 已備份原始資料庫")
    
    # 測試場景
    scenarios = [
        {
            'name': '正常情況',
            'action': lambda: print("   資料庫正常運作"),
            'restore': False
        },
        {
            'name': '資料庫檔案不存在',
            'action': lambda: os.remove(db_path) if os.path.exists(db_path) else None,
            'restore': True
        },
        {
            'name': '資料庫檔案損毀（模擬）',
            'action': lambda: create_corrupted_db(db_path),
            'restore': True
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. 測試場景：{scenario['name']}")
        print("-" * 30)
        
        try:
            # 執行測試動作
            scenario['action']()
            
            # 測試資料庫連線
            from employee.views import check_database_connection
            connection_ok = check_database_connection()
            
            if connection_ok:
                print("   ✅ 資料庫連線正常")
                
                # 測試基本查詢
                from employee.models import Employee
                try:
                    count = Employee.objects.count()
                    print(f"   📊 員工資料筆數：{count}")
                except Exception as e:
                    print(f"   ❌ 查詢員工資料失敗：{e}")
            else:
                print("   ❌ 資料庫連線失敗")
                print("   ℹ️  防呆機制應該會顯示錯誤頁面")
        
        except Exception as e:
            print(f"   ❌ 測試過程中發生錯誤：{e}")
        
        # 恢復資料庫（如果需要）
        if scenario['restore'] and os.path.exists(backup_path):
            shutil.copy2(backup_path, db_path)
            print("   🔄 已恢復資料庫")
    
    # 清理備份檔案
    if os.path.exists(backup_path):
        os.remove(backup_path)
        print("\n🧹 已清理測試備份檔案")
    
    print("\n" + "=" * 50)
    print("🎯 防呆測試完成！")
    print("\n建議測試項目：")
    print("1. 在瀏覽器中訪問 http://127.0.0.1:8001/api/health/ 檢查健康狀態")
    print("2. 在資料庫問題時訪問員工列表頁面，確認是否顯示友善錯誤訊息")
    print("3. 測試沒有員工資料時的友善提示訊息")

def create_corrupted_db(db_path):
    """建立一個損毀的資料庫檔案（僅用於測試）"""
    with open(db_path, 'w') as f:
        f.write("這不是一個有效的 SQLite 檔案")

def test_empty_database():
    """測試空資料庫的情況"""
    print("\n🗑️  測試空資料庫場景...")
    
    try:
        from employee.models import Employee, Department
        
        # 清空所有資料（但保持表格結構）
        Employee.objects.all().delete()
        Department.objects.all().delete()
        
        print("   🧹 已清空所有員工和部門資料")
        print("   ℹ️  頁面應該顯示「還沒有員工資料」的友善訊息")
        
        # 重新創建測試資料
        os.system('python create_simple_fake_data.py')
        print("   ✅ 已重新創建測試資料")
        
    except Exception as e:
        print(f"   ❌ 測試空資料庫時發生錯誤：{e}")

if __name__ == "__main__":
    test_database_scenarios()
    test_empty_database()
