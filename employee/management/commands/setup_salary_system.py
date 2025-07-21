from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from employee.models import SalaryItem, WorkSchedule
from employee.services import SalaryCalculationService

class Command(BaseCommand):
    help = '初始化薪資系統基本設定'

    def handle(self, *args, **options):
        self.stdout.write('🏢 開始初始化薪資系統...')
        
        # 創建基本薪資項目
        self.create_salary_items()
        
        # 創建基本工作班別
        self.create_work_schedules()
        
        # 使用新的薪資計算服務創建預設項目
        service = SalaryCalculationService()
        created_items = service.create_default_salary_items()
        
        if created_items:
            self.stdout.write(f'📋 新增了 {len(created_items)} 個預設薪資項目')
        
        self.stdout.write(
            self.style.SUCCESS('✅ 薪資系統初始化完成！')
        )

    def create_salary_items(self):
        """創建基本薪資項目"""
        self.stdout.write('📋 創建基本薪資項目...')
        
        salary_items = [
            # 加給項目
            {
                'name': '主管加給',
                'item_type': 'ALLOWANCE',
                'amount': 5000.00,
                'is_fixed': True,
                'apply_to_parttime': False,
                'description': '管理職務加給'
            },
            {
                'name': '專業加給',
                'item_type': 'ALLOWANCE',
                'amount': 3000.00,
                'is_fixed': True,
                'apply_to_parttime': False,
                'description': '專業技能加給'
            },
            {
                'name': '交通津貼',
                'item_type': 'ALLOWANCE',
                'amount': 2000.00,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '交通費補助'
            },
            {
                'name': '餐費補助',
                'item_type': 'ALLOWANCE',
                'amount': 3000.00,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '午餐費補助'
            },
            {
                'name': '全勤獎金',
                'item_type': 'BONUS',
                'amount': 1000.00,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '當月全勤獎勵'
            },
            {
                'name': '績效獎金',
                'item_type': 'BONUS',
                'amount': None,
                'percentage': 10.00,
                'is_fixed': False,
                'apply_to_parttime': False,
                'description': '依據績效評核發放'
            },
            
            # 扣除項目
            {
                'name': '勞保費',
                'item_type': 'DEDUCTION',
                'amount': None,
                'percentage': 10.50,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '勞工保險費'
            },
            {
                'name': '健保費',
                'item_type': 'DEDUCTION',
                'amount': None,
                'percentage': 5.17,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '全民健康保險費'
            },
            {
                'name': '所得稅',
                'item_type': 'DEDUCTION',
                'amount': None,
                'percentage': 5.00,
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '個人所得稅'
            },
            {
                'name': '遲到扣款',
                'item_type': 'DEDUCTION',
                'amount': 100.00,
                'is_fixed': False,
                'apply_to_parttime': True,
                'description': '遲到罰款'
            },
        ]
        
        created_count = 0
        for item_data in salary_items:
            salary_item, created = SalaryItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ 創建薪資項目: {item_data["name"]}')
            else:
                self.stdout.write(f'  - 薪資項目已存在: {item_data["name"]}')
        
        self.stdout.write(f'📋 完成薪資項目設定，新增 {created_count} 個項目')

    def create_work_schedules(self):
        """創建基本工作班別"""
        self.stdout.write('⏰ 創建基本工作班別...')
        
        schedules = [
            {
                'name': '標準日班',
                'schedule_type': 'REGULAR',
                'start_time': '09:00:00',
                'end_time': '18:00:00',
                'break_start': '12:00:00',
                'break_end': '13:00:00',
                'is_night_shift': False,
                'description': '標準工作時間 9:00-18:00，含午休一小時'
            },
            {
                'name': '彈性上班',
                'schedule_type': 'FLEX',
                'start_time': '09:30:00',
                'end_time': '18:30:00',
                'flex_time_start': '08:00:00',
                'flex_time_end': '10:00:00',
                'break_start': '12:00:00',
                'break_end': '13:00:00',
                'is_night_shift': False,
                'description': '彈性上班時間 8:00-10:00 之間，工作8小時'
            },
            {
                'name': '早班',
                'schedule_type': 'SHIFT',
                'start_time': '06:00:00',
                'end_time': '15:00:00',
                'break_start': '11:00:00',
                'break_end': '12:00:00',
                'is_night_shift': False,
                'description': '早班 6:00-15:00'
            },
            {
                'name': '夜班',
                'schedule_type': 'SHIFT',
                'start_time': '22:00:00',
                'end_time': '07:00:00',
                'break_start': '02:00:00',
                'break_end': '03:00:00',
                'is_night_shift': True,
                'description': '夜班 22:00-07:00（跨日）'
            },
            {
                'name': '兼職彈性',
                'schedule_type': 'PT',
                'start_time': '10:00:00',
                'end_time': '16:00:00',
                'is_night_shift': False,
                'description': '兼職人員彈性時段'
            },
        ]
        
        created_count = 0
        for schedule_data in schedules:
            work_schedule, created = WorkSchedule.objects.get_or_create(
                name=schedule_data['name'],
                defaults=schedule_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ 創建工作班別: {schedule_data["name"]}')
            else:
                self.stdout.write(f'  - 工作班別已存在: {schedule_data["name"]}')
        
        self.stdout.write(f'⏰ 完成工作班別設定，新增 {created_count} 個班別')
