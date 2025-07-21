from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import DatabaseError, OperationalError
from employee.models import Employee, Department
import os

class Command(BaseCommand):
    help = 'HR 系統資料庫健康檢查和維護工具'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='只檢查資料庫狀態，不執行修復'
        )
        parser.add_argument(
            '--restore-backup',
            action='store_true',
            help='從備份恢復資料庫'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🏥 HR 系統資料庫健康檢查工具')
        )
        self.stdout.write('=' * 50)

        # 檢查資料庫連線
        if self.check_database_connection():
            self.stdout.write(
                self.style.SUCCESS('✅ 資料庫連線正常')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ 資料庫連線失敗')
            )
            return

        # 檢查資料表
        if self.check_tables():
            self.stdout.write(
                self.style.SUCCESS('✅ 所有必要資料表都存在')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ 部分資料表可能有問題')
            )

        # 檢查資料完整性
        self.check_data_integrity()

        # 執行修復（如果不是只檢查模式）
        if not options['check_only']:
            if options['restore_backup']:
                self.restore_from_backup()
            else:
                self.auto_repair()

        self.stdout.write('=' * 50)
        self.stdout.write(
            self.style.SUCCESS('🎯 檢查完成！')
        )

    def check_database_connection(self):
        """檢查資料庫連線"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except (DatabaseError, OperationalError):
            return False

    def check_tables(self):
        """檢查重要資料表是否存在"""
        try:
            Employee.objects.exists()
            Department.objects.exists()
            return True
        except (DatabaseError, OperationalError) as e:
            self.stdout.write(
                self.style.ERROR(f'資料表檢查失敗: {e}')
            )
            return False

    def check_data_integrity(self):
        """檢查資料完整性"""
        try:
            employee_count = Employee.objects.count()
            department_count = Department.objects.count()
            
            self.stdout.write(f'📊 員工數量: {employee_count}')
            self.stdout.write(f'📊 部門數量: {department_count}')
            
            if employee_count == 0:
                self.stdout.write(
                    self.style.WARNING('⚠️ 沒有員工資料')
                )
            
            if department_count == 0:
                self.stdout.write(
                    self.style.WARNING('⚠️ 沒有部門資料')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'資料完整性檢查失敗: {e}')
            )

    def restore_from_backup(self):
        """從備份恢復資料庫"""
        backup_files = [
            'db.sqlite3.backup',
            'db.sqlite3.bak',
            'database_backup.sqlite3'
        ]
        
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                self.stdout.write(
                    self.style.SUCCESS(f'🔄 找到備份檔案: {backup_file}')
                )
                # 這裡可以加入實際的恢復邏輯
                return
        
        self.stdout.write(
            self.style.WARNING('⚠️ 沒有找到備份檔案')
        )

    def auto_repair(self):
        """自動修復常見問題"""
        self.stdout.write('🔧 執行自動修復...')
        
        # 檢查是否需要執行遷移
        try:
            from django.core.management import call_command
            self.stdout.write('檢查是否需要資料庫遷移...')
            call_command('migrate', verbosity=0)
            self.stdout.write(
                self.style.SUCCESS('✅ 資料庫遷移檢查完成')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'遷移檢查失敗: {e}')
            )
