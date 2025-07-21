from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '部門'
        verbose_name_plural = '部門'

class Employee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('FT', '正職'),
        ('PT', '兼職'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='姓名')
    email = models.EmailField(verbose_name='電子郵件')
    phone = models.CharField(max_length=20, verbose_name='電話')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='部門')
    hire_date = models.DateField(verbose_name='到職日期')
    employment_type = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='FT',
        verbose_name='僱用類型'
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='時薪',
        help_text='僅適用於兼職員工'
    )
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='基本薪資',
        help_text='僅適用於正職員工'
    )
    active = models.BooleanField(default=True, verbose_name='在職狀態')

    def __str__(self):
        return f"{self.name} ({self.get_employment_type_display()})"
    
    class Meta:
        verbose_name = '員工'
        verbose_name_plural = '員工'

class PayrollPeriod(models.Model):
    start_date = models.DateField(verbose_name='起始日期')
    end_date = models.DateField(verbose_name='結束日期')
    pay_date = models.DateField(verbose_name='發薪日')
    is_processed = models.BooleanField(default=False, verbose_name='已處理')
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name='處理日期')
    
    def __str__(self):
        return f"{self.start_date} ~ {self.end_date}"
    
    class Meta:
        verbose_name = '薪資期間'
        verbose_name_plural = '薪資期間'

class Salary(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='員工'
    )
    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        verbose_name='薪資期間'
    )
    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='基本薪資/時薪總額'
    )
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name='加班時數'
    )
    overtime_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='加班費'
    )
    working_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name='工作時數',
        help_text='兼職人員使用'
    )
    is_confirmed = models.BooleanField(default=False, verbose_name='已確認')
    
    def __str__(self):
        return f"{self.employee.name} - {self.period}"

    @property
    def formatted_overtime(self):
        """將加班時數格式化為 X 小 Y 分鐘"""
        if self.overtime_hours is None:
            return "0 小 0 分"
        
        hours = int(self.overtime_hours)
        minutes = int((self.overtime_hours - hours) * 60)
        
        return f"{hours} 小 {minutes} 分"

    @property
    def total_salary(self):
        salary_items = self.salarydetail_set.all()
        total = self.base_amount + self.overtime_amount
        for item in salary_items:
            if item.item.item_type in ['ALLOWANCE', 'BONUS']:
                total += item.amount
            else:
                total -= item.amount
        return total

    @property
    def base_amount_int(self):
        return int(round(self.base_amount, 0))

    @property
    def overtime_amount_int(self):
        return int(round(self.overtime_amount, 0))

    @property
    def total_salary_int(self):
        return int(round(self.total_salary, 0))
    
    class Meta:
        verbose_name = '薪資紀錄'
        verbose_name_plural = '薪資紀錄'
        unique_together = ['employee', 'period']

class SalaryDetail(models.Model):
    salary = models.ForeignKey(
        Salary,
        on_delete=models.CASCADE,
        verbose_name='薪資紀錄'
    )
    item = models.ForeignKey(
        'SalaryItem',
        on_delete=models.PROTECT,
        verbose_name='薪資項目'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='金額'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='說明'
    )

    def __str__(self):
        return f"{self.salary.employee.name} - {self.item.name}"
    
    class Meta:
        verbose_name = '薪資明細'
        verbose_name_plural = '薪資明細'

class Punch(models.Model):
    PUNCH_TYPES = [
        ('IN', '上班'),
        ('OUT', '下班'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    punch_time = models.DateTimeField()
    punch_type = models.CharField(max_length=3, choices=PUNCH_TYPES)

    def __str__(self):
        return f"{self.employee.name} - {self.get_punch_type_display()} at {self.punch_time.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        verbose_name = '打卡記錄'
        verbose_name_plural = '打卡記錄'

class WorkSchedule(models.Model):
    SCHEDULE_TYPE_CHOICES = [
        ('REGULAR', '固定班'),
        ('FLEX', '彈性班'),
        ('SHIFT', '輪班'),
        ('PT', '兼職班')
    ]

    name = models.CharField(max_length=100, verbose_name='班別名稱')
    schedule_type = models.CharField(
        max_length=10,
        choices=SCHEDULE_TYPE_CHOICES,
        verbose_name='班別類型'
    )
    start_time = models.TimeField(verbose_name='預設上班時間')
    end_time = models.TimeField(verbose_name='預設下班時間')
    break_start = models.TimeField(verbose_name='休息開始時間', null=True, blank=True)
    break_end = models.TimeField(verbose_name='休息結束時間', null=True, blank=True)
    is_night_shift = models.BooleanField(default=False, verbose_name='夜班')
    flex_time_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name='彈性上班時間起始',
        help_text='彈性班別可設定彈性上下班時間區間'
    )
    flex_time_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name='彈性上班時間結束'
    )
    description = models.TextField(blank=True, verbose_name='說明')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '工作班別'
        verbose_name_plural = '工作班別'

def get_default_work_schedule():
    from .models import WorkSchedule
    schedule, created = WorkSchedule.objects.get_or_create(
        name='標準日班',
        defaults={
            'schedule_type': 'REGULAR',
            'start_time': '09:00:00',
            'end_time': '18:00:00',
            'description': '預設標準日班'
        }
    )
    return schedule

class EmployeeSchedule(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='員工'
    )
    work_schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE,
        verbose_name='班別',
        default=get_default_work_schedule
    )
    start_date = models.DateField(verbose_name='生效日期')
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='結束日期'
    )
    is_primary = models.BooleanField(
        default=True,
        verbose_name='主要班別',
        help_text='員工的預設班別'
    )

    def __str__(self):
        return f"{self.employee.name} - {self.work_schedule.name}"

    class Meta:
        verbose_name = '員工班別'
        verbose_name_plural = '員工班別'

class SalaryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('ALLOWANCE', '加給'),
        ('DEDUCTION', '扣除'),
        ('BONUS', '獎金'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='項目名稱')
    item_type = models.CharField(
        max_length=10,
        choices=ITEM_TYPE_CHOICES,
        verbose_name='項目類型'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='固定金額'
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='百分比',
        help_text='如果是百分比計算，請填入百分比數值'
    )
    is_fixed = models.BooleanField(default=True, verbose_name='固定項目')
    apply_to_parttime = models.BooleanField(
        default=False,
        verbose_name='適用兼職',
        help_text='此項目是否適用於兼職人員'
    )
    description = models.TextField(blank=True, verbose_name='說明')

    def __str__(self):
        return f"{self.name} ({self.get_item_type_display()})"

    class Meta:
        verbose_name = '薪資項目'
        verbose_name_plural = '薪資項目'

class Leave(models.Model):
    LEAVE_TYPES = [
        ('ANNUAL', '特休'),
        ('SICK', '病假'),
        ('PERSONAL', '事假'),
        ('MARRIAGE', '婚假'),
        ('FUNERAL', '喪假'),
        ('MATERNITY', '產假'),
        ('PATERNITY', '陪產假'),
        ('PUBLIC', '公假'),
        ('COMPENSATORY', '補休'),
        # 可以根據需要添加更多假別
    ]
    STATUS_CHOICES = [
        ('PENDING', '待審核'),
        ('APPROVED', '已核准'),
        ('REJECTED', '已拒絕'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    applied_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date}) - {self.get_status_display()}"

    class Meta:
        verbose_name = '請假記錄'
        verbose_name_plural = '請假記錄'
