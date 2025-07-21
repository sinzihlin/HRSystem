"""
薪資計算服務
處理薪資相關的業務邏輯和計算
"""
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime, timedelta
from django.db.models import Q, Sum
from django.utils import timezone

from .models import (
    Employee, Salary, SalaryDetail, SalaryItem, 
    PayrollPeriod, Punch, Leave, WorkSchedule, EmployeeSchedule
)


class SalaryCalculationService:
    """薪資計算服務類"""
    
    def __init__(self):
        self.overtime_rate = Decimal('1.33')  # 加班費倍率
        self.holiday_rate = Decimal('2.0')    # 假日加班費倍率
        self.standard_hours = 8               # 標準工作時數
    
    def calculate_salary_for_period(self, employee, period):
        """
        計算員工在指定期間的薪資
        
        Args:
            employee: 員工物件
            period: 薪資期間物件
            
        Returns:
            Salary: 薪資記錄物件
        """
        # 檢查是否已存在薪資記錄
        salary, created = Salary.objects.get_or_create(
            employee=employee,
            period=period,
            defaults={
                'base_amount': Decimal('0'),
                'overtime_hours': Decimal('0'),
                'overtime_amount': Decimal('0'),
                'working_hours': Decimal('0'),
            }
        )
        
        if not created and salary.is_confirmed:
            return salary  # 已確認的薪資不重新計算
        
        # 計算基本薪資
        base_amount = self._calculate_base_salary(employee, period)
        
        # 計算工作時數和加班費
        working_hours, overtime_hours, overtime_amount = self._calculate_work_hours_and_overtime(
            employee, period
        )
        
        # 處理請假扣款（需要在薪資項目計算前處理）
        leave_deduction = self._calculate_leave_deduction(employee, period)
        
        # 更新薪資記錄
        salary.base_amount = base_amount
        salary.working_hours = working_hours
        salary.overtime_hours = overtime_hours
        salary.overtime_amount = overtime_amount
        salary.save()
        
        # 計算薪資項目明細（包含請假扣款）
        self._calculate_salary_details(salary, leave_deduction)
        
        return salary
    
    def _calculate_base_salary(self, employee, period):
        """計算基本薪資"""
        if employee.employment_type == 'FT':
            # 正職員工：月薪制
            return employee.base_salary or Decimal('0')
        else:
            # 兼職員工：時薪制，需要計算實際工作時數
            working_hours = self._get_working_hours(employee, period)
            hourly_rate = employee.hourly_rate or Decimal('0')
            return working_hours * hourly_rate
    
    def _calculate_work_hours_and_overtime(self, employee, period):
        """計算工作時數和加班費"""
        # 獲取期間內的打卡記錄
        punches = Punch.objects.filter(
            employee=employee,
            punch_time__date__range=[period.start_date, period.end_date]
        ).order_by('punch_time')
        
        total_working_hours = Decimal('0')
        total_overtime_hours = Decimal('0')
        total_overtime_amount = Decimal('0')
        
        # 按日期分組處理打卡記錄
        current_date = period.start_date
        while current_date <= period.end_date:
            daily_punches = punches.filter(punch_time__date=current_date)
            
            if daily_punches.exists():
                daily_hours, overtime_hours = self._calculate_daily_hours(
                    employee, current_date, daily_punches
                )
                
                total_working_hours += daily_hours
                
                if overtime_hours > 0:
                    total_overtime_hours += overtime_hours
                    # 計算加班費
                    hourly_rate = self._get_hourly_rate(employee)
                    overtime_rate = self._get_overtime_rate(employee, current_date, True)
                    
                    daily_overtime_amount = overtime_hours * hourly_rate * overtime_rate
                    total_overtime_amount += daily_overtime_amount
            
            current_date += timedelta(days=1)
        
        return total_working_hours, total_overtime_hours, total_overtime_amount
    
    def _calculate_daily_hours(self, employee, date, punches):
        """計算單日工作時數和加班時數"""
        if punches.count() < 2:
            return Decimal('0'), Decimal('0')
        
        # 找到當日的上班和下班打卡
        punch_in = punches.filter(punch_type='IN').first()
        punch_out = punches.filter(punch_type='OUT').last()
        
        if not punch_in or not punch_out:
            return Decimal('0'), Decimal('0')
        
        # 計算總工作時間（小時）
        work_duration = punch_out.punch_time - punch_in.punch_time
        total_hours = Decimal(str(work_duration.total_seconds() / 3600))
        
        # 扣除午休時間（1小時）
        if total_hours > 5:  # 工作超過5小時才扣午休
            total_hours -= Decimal('1')
        
        # 計算加班時數
        standard_hours = Decimal(str(self.standard_hours))
        if total_hours > standard_hours:
            overtime_hours = total_hours - standard_hours
            working_hours = standard_hours
        else:
            overtime_hours = Decimal('0')
            working_hours = total_hours
        
        return working_hours, overtime_hours
    
    def _calculate_leave_deduction(self, employee, period):
        """
        計算請假扣款
        
        Args:
            employee: 員工物件
            period: 薪資期間物件
            
        Returns:
            dict: 包含扣款詳情的字典
        """
        # 獲取期間內已核准的請假記錄
        approved_leaves = Leave.objects.filter(
            employee=employee,
            status='APPROVED',
            start_date__lte=period.end_date,
            end_date__gte=period.start_date
        )
        
        unpaid_leave_types = ['PERSONAL', 'SICK']  # 需要扣薪的假別
        total_unpaid_days = 0
        leave_details = []
        
        for leave in approved_leaves:
            # 計算與薪資期間重疊的天數
            overlap_start = max(leave.start_date, period.start_date)
            overlap_end = min(leave.end_date, period.end_date)
            
            if overlap_start <= overlap_end:
                overlap_days = (overlap_end - overlap_start).days + 1
                
                # 檢查是否為無薪假
                if leave.leave_type in unpaid_leave_types:
                    total_unpaid_days += overlap_days
                    leave_details.append(f"{leave.get_leave_type_display()}{overlap_days}天")
        
        # 計算扣款金額
        total_deduction = Decimal('0')
        if total_unpaid_days > 0:
            daily_rate = self._calculate_daily_rate(employee)
            total_deduction = daily_rate * Decimal(str(total_unpaid_days))
        
        return {
            'total_amount': total_deduction,
            'unpaid_days': total_unpaid_days,
            'details': ', '.join(leave_details) if leave_details else ''
        }
    
    def _calculate_daily_rate(self, employee):
        """計算員工日薪"""
        if employee.employment_type == 'FT' and employee.base_salary:
            # 正職員工：月薪除以30天
            return employee.base_salary / Decimal('30')
        elif employee.hourly_rate:
            # 兼職員工：時薪乘以8小時
            return employee.hourly_rate * Decimal('8')
        else:
            return Decimal('0')
    
    def _calculate_salary_details(self, salary, leave_deduction=None):
        """計算薪資明細項目"""
        # 刪除現有明細
        salary.salarydetail_set.all().delete()
        
        employee = salary.employee
        
        # 獲取適用的薪資項目
        salary_items = SalaryItem.objects.filter(
            Q(apply_to_parttime=True) | Q(apply_to_parttime=False)
        )
        
        if employee.employment_type == 'PT':
            # 兼職員工只適用標記為適用兼職的項目
            salary_items = salary_items.filter(apply_to_parttime=True)
        
        for item in salary_items:
            if item.is_fixed and item.amount:
                # 固定金額
                amount = item.amount
            elif item.percentage:
                # 百分比計算
                base_amount = salary.base_amount + salary.overtime_amount
                amount = base_amount * (item.percentage / Decimal('100'))
            else:
                continue  # 跳過沒有設定金額或百分比的項目
            
            # 創建薪資明細
            SalaryDetail.objects.create(
                salary=salary,
                item=item,
                amount=amount,
                description=f'{item.name} - {salary.period}'
            )
        
        # 添加請假扣款項目
        if leave_deduction and leave_deduction['total_amount'] > 0:
            # 創建或獲取請假扣款項目
            leave_deduction_item, created = SalaryItem.objects.get_or_create(
                name='請假扣款',
                defaults={
                    'item_type': 'DEDUCTION',
                    'is_fixed': False,
                    'apply_to_parttime': True,
                    'description': '無薪假/事假扣款'
                }
            )
            
            SalaryDetail.objects.create(
                salary=salary,
                item=leave_deduction_item,
                amount=leave_deduction['total_amount'],
                description=f"請假扣款 - {leave_deduction['unpaid_days']}天 ({leave_deduction['details']})"
            )
    
    def _get_working_hours(self, employee, period):
        """獲取員工在期間內的工作時數"""
        punches = Punch.objects.filter(
            employee=employee,
            punch_time__date__range=[period.start_date, period.end_date]
        )
        
        total_hours = Decimal('0')
        current_date = period.start_date
        
        while current_date <= period.end_date:
            daily_punches = punches.filter(punch_time__date=current_date)
            daily_hours, _ = self._calculate_daily_hours(employee, current_date, daily_punches)
            total_hours += daily_hours
            current_date += timedelta(days=1)
        
        return total_hours
    
    def _get_hourly_rate(self, employee):
        """獲取員工時薪"""
        if employee.employment_type == 'FT' and employee.base_salary:
            # 正職員工：月薪除以標準工作時數
            monthly_hours = Decimal('168')  # 21天 * 8小時
            return employee.base_salary / monthly_hours
        elif employee.hourly_rate:
            return employee.hourly_rate
        else:
            return Decimal('200')  # 預設時薪
    
    def _is_holiday(self, date):
        """判斷是否為假日"""
        # 週六、週日
        if date.weekday() >= 5:
            return True
        
        # 國定假日（簡化版，可以根據需要擴展）
        holidays = [
            (1, 1),   # 元旦
            (2, 28),  # 和平紀念日
            (4, 4),   # 兒童節
            (4, 5),   # 清明節
            (5, 1),   # 勞動節
            (10, 10), # 國慶日
        ]
        
        for month, day in holidays:
            if date.month == month and date.day == day:
                return True
        
        return False
    
    def _get_overtime_rate(self, employee, work_date, is_overtime):
        """
        獲取加班費倍率
        
        Args:
            employee: 員工物件
            work_date: 工作日期
            is_overtime: 是否為加班時數
            
        Returns:
            Decimal: 加班費倍率
        """
        if not is_overtime:
            return Decimal('1.0')  # 正常工時
        
        if self._is_holiday(work_date):
            return self.holiday_rate  # 假日加班 2.0 倍
        else:
            return self.overtime_rate  # 平日加班 1.33 倍
    
    def create_payroll_period(self, start_date, end_date, pay_date):
        """創建薪資期間"""
        period = PayrollPeriod.objects.create(
            start_date=start_date,
            end_date=end_date,
            pay_date=pay_date
        )
        return period
    
    def process_payroll_for_period(self, period):
        """處理指定期間的所有員工薪資"""
        if period.is_processed:
            raise ValueError("此薪資期間已經處理過了")
        
        active_employees = Employee.objects.filter(active=True)
        processed_count = 0
        
        for employee in active_employees:
            salary = self.calculate_salary_for_period(employee, period)
            processed_count += 1
        
        # 標記期間為已處理
        period.is_processed = True
        period.processed_date = timezone.now()
        period.save()
        
        return processed_count
    
    def get_salary_summary(self, employee, year=None, month=None):
        """獲取員工薪資摘要"""
        salaries = employee.salary_set.all()
        
        if year:
            salaries = salaries.filter(period__start_date__year=year)
        if month:
            salaries = salaries.filter(period__start_date__month=month)
        
        summary = {
            'total_salaries': salaries.count(),
            'total_amount': sum(s.total_salary for s in salaries),
            'average_amount': 0,
            'latest_salary': salaries.order_by('-period__start_date').first()
        }
        
        if summary['total_salaries'] > 0:
            summary['average_amount'] = summary['total_amount'] / summary['total_salaries']
        
        return summary
    
    def create_default_salary_items(self):
        """創建預設薪資項目"""
        default_items = [
            # 勞健保扣除項目
            {
                'name': '勞保費',
                'item_type': 'DEDUCTION',
                'percentage': Decimal('10.50'),
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '勞工保險費（依勞保費率計算）'
            },
            {
                'name': '健保費',
                'item_type': 'DEDUCTION',
                'percentage': Decimal('5.17'),
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '全民健康保險費（依健保費率計算）'
            },
            {
                'name': '所得稅',
                'item_type': 'DEDUCTION',
                'percentage': Decimal('5.00'),
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '個人所得稅（依所得稅率計算）'
            },
            # 津貼項目
            {
                'name': '全勤獎金',
                'item_type': 'BONUS',
                'amount': Decimal('1000.00'),
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '當月全勤獎勵'
            },
            {
                'name': '交通津貼',
                'item_type': 'ALLOWANCE',
                'amount': Decimal('2000.00'),
                'is_fixed': True,
                'apply_to_parttime': True,
                'description': '交通費補助'
            }
        ]
        
        created_items = []
        for item_data in default_items:
            salary_item, created = SalaryItem.objects.get_or_create(
                name=item_data['name'],
                defaults=item_data
            )
            if created:
                created_items.append(salary_item)
        
        return created_items
