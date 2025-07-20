from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    hire_date = models.DateField()

    def __str__(self):
        return self.name

class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pay_date = models.DateField()

    def __str__(self):
        return f"{self.employee.name} - {self.pay_date}"

    @property
    def total_salary(self):
        return self.base_salary + self.bonus - self.deductions

class Punch(models.Model):
    PUNCH_TYPES = [
        ('IN', '上班打卡'),
        ('OUT', '下班打卡'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    punch_time = models.DateTimeField()
    punch_type = models.CharField(max_length=3, choices=PUNCH_TYPES)

    def __str__(self):
        return f"{self.employee.name} - {self.get_punch_type_display()} at {self.punch_time.strftime('%Y-%m-%d %H:%M:%S')}"

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
