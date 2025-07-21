from django.contrib import admin
from .models import (
    Department, Employee, Salary, Punch, Leave, 
    PayrollPeriod, SalaryItem, SalaryDetail, 
    WorkSchedule, EmployeeSchedule
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'employee_count')
    search_fields = ('name',)
    
    def employee_count(self, obj):
        return obj.employee_set.count()
    employee_count.short_description = '員工數量'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department', 'employment_type', 'hire_date', 'active')
    list_filter = ('department', 'employment_type', 'active', 'hire_date')
    search_fields = ('name', 'email')
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('基本資料', {
            'fields': ('name', 'email', 'phone', 'department', 'hire_date', 'active')
        }),
        ('僱用資訊', {
            'fields': ('employment_type', 'base_salary', 'hourly_rate')
        }),
    )

@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'pay_date', 'is_processed', 'processed_date')
    list_filter = ('is_processed', 'pay_date')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

@admin.register(SalaryItem)
class SalaryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'is_fixed', 'amount', 'percentage', 'apply_to_parttime')
    list_filter = ('item_type', 'is_fixed', 'apply_to_parttime')
    search_fields = ('name', 'description')

class SalaryDetailInline(admin.TabularInline):
    model = SalaryDetail
    extra = 0

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'period', 'base_amount', 'overtime_amount', 'total_salary', 'is_confirmed')
    list_filter = ('is_confirmed', 'period')
    search_fields = ('employee__name',)
    inlines = [SalaryDetailInline]
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_confirmed:
            return ('employee', 'period', 'base_amount', 'overtime_hours', 'overtime_amount', 'working_hours')
        return ()

@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'schedule_type', 'start_time', 'end_time', 'is_night_shift')
    list_filter = ('schedule_type', 'is_night_shift')
    search_fields = ('name', 'description')



@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ('employee', 'work_schedule', 'start_date', 'end_date', 'is_primary')
    list_filter = ('is_primary', 'work_schedule__schedule_type')
    search_fields = ('employee__name', 'work_schedule__name')
    date_hierarchy = 'start_date'

@admin.register(Punch)
class PunchAdmin(admin.ModelAdmin):
    list_display = ('employee', 'punch_time', 'punch_type')
    list_filter = ('punch_type', 'punch_time')
    search_fields = ('employee__name',)
    date_hierarchy = 'punch_time'

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_date')
    list_filter = ('leave_type', 'status', 'applied_date')
    search_fields = ('employee__name', 'reason')
    date_hierarchy = 'start_date'