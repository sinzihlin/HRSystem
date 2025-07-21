"""
薪資相關視圖
處理薪資計算、薪資單查看等功能
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db import transaction
from django.db.models import Q
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
import csv
import io

from .models import Employee, Salary, PayrollPeriod, SalaryItem, WorkSchedule
from .services import SalaryCalculationService


class SalaryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """薪資列表視圖"""
    model = Salary
    template_name = 'employee/salary_list.html'
    context_object_name = 'salaries'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = Salary.objects.select_related('employee', 'period').order_by('-period__start_date')
        
        # 篩選條件
        employee_id = self.request.GET.get('employee')
        period_id = self.request.GET.get('period')
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        status = self.request.GET.get('status')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        if year:
            queryset = queryset.filter(period__start_date__year=year)
        if month:
            queryset = queryset.filter(period__start_date__month=month)
        if status == 'confirmed':
            queryset = queryset.filter(is_confirmed=True)
        elif status == 'pending':
            queryset = queryset.filter(is_confirmed=False)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = Employee.objects.filter(active=True).order_by('name')
        context['periods'] = PayrollPeriod.objects.order_by('-start_date')
        
        # 獲取可用的年份（從薪資期間中提取）
        available_years = PayrollPeriod.objects.dates('start_date', 'year', order='DESC')
        context['available_years'] = [date.year for date in available_years]
        
        # 月份選項
        context['months'] = [
            {'value': 1, 'label': '1月'}, {'value': 2, 'label': '2月'}, 
            {'value': 3, 'label': '3月'}, {'value': 4, 'label': '4月'},
            {'value': 5, 'label': '5月'}, {'value': 6, 'label': '6月'},
            {'value': 7, 'label': '7月'}, {'value': 8, 'label': '8月'},
            {'value': 9, 'label': '9月'}, {'value': 10, 'label': '10月'},
            {'value': 11, 'label': '11月'}, {'value': 12, 'label': '12月'},
        ]
        
        # 當前選中的員工
        selected_employee_id = self.request.GET.get('employee')
        context['selected_employee'] = None
        if selected_employee_id:
            try:
                context['selected_employee'] = Employee.objects.get(id=selected_employee_id, active=True)
            except Employee.DoesNotExist:
                pass
        
        # 統計資訊
        queryset = self.get_queryset()
        if queryset.exists():
            context['total_records'] = queryset.count()
            context['total_amount'] = sum(salary.total_salary for salary in queryset)
            context['average_amount'] = context['total_amount'] / context['total_records']
        else:
            context['total_records'] = 0
            context['total_amount'] = 0
            context['average_amount'] = 0
        
        return context


class SalaryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """薪資詳細視圖"""
    model = Salary
    template_name = 'employee/salary_detail.html'
    context_object_name = 'salary'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        salary = self.get_object()
        context['salary_details'] = salary.salarydetail_set.select_related('item').all()
        return context


class PayrollManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """薪資管理視圖"""
    template_name = 'employee/payroll_management.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periods'] = PayrollPeriod.objects.order_by('-start_date')[:10]
        context['salary_items'] = SalaryItem.objects.all()
        context['work_schedules'] = WorkSchedule.objects.all()
        return context


class SalaryItemManagementView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """薪資項目管理視圖"""
    template_name = 'employee/salary_item_management.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary_items'] = SalaryItem.objects.all().order_by('item_type', 'name')
        return context


@require_POST
@login_required
def create_payroll_period(request):
    """創建薪資期間 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        pay_date = datetime.strptime(data['pay_date'], '%Y-%m-%d').date()
        
        if start_date >= end_date:
            return JsonResponse({
                'status': 'error', 
                'message': '結束日期必須晚於開始日期'
            })
        
        if pay_date < end_date:
            return JsonResponse({
                'status': 'error', 
                'message': '發薪日不能早於期間結束日'
            })
        
        # 檢查是否有重疊的期間
        overlapping = PayrollPeriod.objects.filter(
            start_date__lt=end_date,
            end_date__gt=start_date
        ).exists()
        
        if overlapping:
            return JsonResponse({
                'status': 'error', 
                'message': '期間與現有薪資期間重疊'
            })
        
        service = SalaryCalculationService()
        period = service.create_payroll_period(start_date, end_date, pay_date)
        
        return JsonResponse({
            'status': 'success',
            'message': '薪資期間創建成功',
            'period_id': period.id
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'創建失敗：{str(e)}'
        })


@require_POST
@login_required
def process_payroll(request):
    """處理薪資計算 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        period_id = data.get('period_id')
        
        if not period_id:
            return JsonResponse({
                'status': 'error', 
                'message': '請指定薪資期間'
            })
        
        period = get_object_or_404(PayrollPeriod, id=period_id)
        
        if period.is_processed:
            return JsonResponse({
                'status': 'error', 
                'message': '此薪資期間已經處理過了'
            })
        
        service = SalaryCalculationService()
        
        with transaction.atomic():
            processed_count = service.process_payroll_for_period(period)
        
        return JsonResponse({
            'status': 'success',
            'message': f'薪資處理完成，共處理 {processed_count} 名員工',
            'processed_count': processed_count
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'處理失敗：{str(e)}'
        })


@require_POST
@login_required
def calculate_single_salary(request):
    """計算單一員工薪資 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        period_id = data.get('period_id')
        
        if not employee_id or not period_id:
            return JsonResponse({
                'status': 'error', 
                'message': '請指定員工和薪資期間'
            })
        
        employee = get_object_or_404(Employee, id=employee_id)
        period = get_object_or_404(PayrollPeriod, id=period_id)
        
        service = SalaryCalculationService()
        salary = service.calculate_salary_for_period(employee, period)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{employee.name} 的薪資計算完成',
            'salary_id': salary.id,
            'total_salary': float(salary.total_salary)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'計算失敗：{str(e)}'
        })


@login_required
def salary_summary_api(request, employee_id):
    """員工薪資摘要 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        if year:
            year = int(year)
        if month:
            month = int(month)
        
        service = SalaryCalculationService()
        summary = service.get_salary_summary(employee, year, month)
        
        # 轉換 Decimal 為 float 以便 JSON 序列化
        summary['total_amount'] = float(summary['total_amount'])
        summary['average_amount'] = float(summary['average_amount'])
        
        if summary['latest_salary']:
            summary['latest_salary'] = {
                'period': str(summary['latest_salary'].period),
                'total_salary': float(summary['latest_salary'].total_salary),
                'pay_date': summary['latest_salary'].period.pay_date.isoformat()
            }
        
        return JsonResponse({
            'status': 'success',
            'employee': employee.name,
            'summary': summary
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'獲取摘要失敗：{str(e)}'
        })


@require_POST
@login_required
def create_salary_item(request):
    """創建薪資項目 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # 驗證必要欄位
        required_fields = ['name', 'item_type']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'status': 'error',
                    'message': f'缺少必要欄位: {field}'
                })
        
        # 創建薪資項目
        salary_item = SalaryItem.objects.create(
            name=data['name'],
            item_type=data['item_type'],
            amount=data.get('amount'),
            percentage=data.get('percentage'),
            is_fixed=data.get('is_fixed', True),
            apply_to_parttime=data.get('apply_to_parttime', False),
            description=data.get('description', '')
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'薪資項目 "{salary_item.name}" 創建成功',
            'item_id': salary_item.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '無效的 JSON 格式'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'創建失敗：{str(e)}'})

@require_POST
@login_required
def salary_calculation_preview(request):
    """薪資計算預覽 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        data = json.loads(request.body)
        employee_id = data.get('employee_id')
        period_id = data.get('period_id')
        
        if not employee_id or not period_id:
            return JsonResponse({
                'status': 'error', 
                'message': '請指定員工和薪資期間'
            })
        
        employee = get_object_or_404(Employee, id=employee_id)
        period = get_object_or_404(PayrollPeriod, id=period_id)
        
        service = SalaryCalculationService()
        
        # 計算預覽數據
        base_amount = service._calculate_base_salary(employee, period)
        working_hours, overtime_hours, overtime_amount = service._calculate_work_hours_and_overtime(employee, period)
        leave_deduction = service._calculate_leave_deduction(employee, period)
        
        # 獲取適用的薪資項目
        salary_items = SalaryItem.objects.filter(
            Q(apply_to_parttime=True) | Q(apply_to_parttime=False)
        )
        
        if employee.employment_type == 'PT':
            salary_items = salary_items.filter(apply_to_parttime=True)
        
        items_preview = []
        total_allowances = 0
        total_deductions = 0
        
        for item in salary_items:
            if item.is_fixed and item.amount:
                amount = item.amount
            elif item.percentage:
                amount = (base_amount + overtime_amount) * (item.percentage / Decimal('100'))
            else:
                continue
                
            items_preview.append({
                'name': item.name,
                'type': item.get_item_type_display(),
                'amount': float(amount)
            })
            
            if item.item_type in ['ALLOWANCE', 'BONUS']:
                total_allowances += amount
            else:
                total_deductions += amount
        
        # 添加請假扣款
        if leave_deduction['total_amount'] > 0:
            items_preview.append({
                'name': '請假扣款',
                'type': '扣除',
                'amount': float(leave_deduction['total_amount'])
            })
            total_deductions += leave_deduction['total_amount']
        
        gross_salary = base_amount + overtime_amount + total_allowances
        net_salary = gross_salary - total_deductions
        
        return JsonResponse({
            'status': 'success',
            'preview': {
                'employee_name': employee.name,
                'period': f"{period.start_date} ~ {period.end_date}",
                'base_amount': float(base_amount),
                'working_hours': float(working_hours),
                'overtime_hours': float(overtime_hours),
                'overtime_amount': float(overtime_amount),
                'leave_deduction': {
                    'amount': float(leave_deduction['total_amount']),
                    'days': leave_deduction['unpaid_days'],
                    'details': leave_deduction['details']
                },
                'salary_items': items_preview,
                'total_allowances': float(total_allowances),
                'total_deductions': float(total_deductions),
                'gross_salary': float(gross_salary),
                'net_salary': float(net_salary)
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '無效的 JSON 格式'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'預覽失敗：{str(e)}'})


@login_required
def salary_chart_data(request):
    """薪資圖表數據 API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        chart_type = request.GET.get('type', 'monthly')
        
        if chart_type == 'monthly':
            # 月度趨勢數據
            from django.db.models import Avg
            from django.utils import timezone
            
            # 獲取過去12個月的數據
            end_date = timezone.now().date()
            start_date = end_date.replace(day=1) - timedelta(days=365)
            
            monthly_data = (
                Salary.objects
                .filter(period__start_date__gte=start_date)
                .extra({'month': "strftime('%%Y-%%m', period.start_date)"})
                .values('month')
                .annotate(avg_salary=Avg('total_salary'))
                .order_by('month')
            )
            
            labels = []
            data = []
            for item in monthly_data:
                year, month = item['month'].split('-')
                labels.append(f"{month}月")
                data.append(float(item['avg_salary'] or 0))
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': '平均薪資',
                        'data': data,
                        'borderColor': 'rgb(75, 192, 192)',
                        'backgroundColor': 'rgba(75, 192, 192, 0.1)',
                        'tension': 0.4
                    }]
                }
            })
        
        elif chart_type == 'department':
            # 部門分析數據
            from django.db.models import Avg, Count
            
            dept_data = (
                Salary.objects
                .select_related('employee__department')
                .values('employee__department__name')
                .annotate(
                    avg_salary=Avg('total_salary'),
                    employee_count=Count('employee', distinct=True)
                )
                .order_by('-avg_salary')
            )
            
            labels = []
            data = []
            colors = [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 205, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ]
            
            for i, item in enumerate(dept_data):
                labels.append(item['employee__department__name'] or '未設定部門')
                data.append(float(item['avg_salary'] or 0))
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': '平均薪資',
                        'data': data,
                        'backgroundColor': colors[:len(labels)],
                        'borderColor': [color.replace('0.6', '1') for color in colors[:len(labels)]],
                        'borderWidth': 1
                    }]
                }
            })
        
        elif chart_type == 'salary_range':
            # 薪資分布數據
            ranges = [
                (0, 30000, '30K以下'),
                (30000, 40000, '30-40K'),
                (40000, 50000, '40-50K'),
                (50000, 60000, '50-60K'),
                (60000, 999999, '60K以上')
            ]
            
            labels = []
            data = []
            
            for min_val, max_val, label in ranges:
                count = Salary.objects.filter(
                    total_salary__gte=min_val,
                    total_salary__lt=max_val
                ).values('employee').distinct().count()
                
                labels.append(label)
                data.append(count)
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': '員工人數',
                        'data': data,
                        'backgroundColor': [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 205, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)'
                        ]
                    }]
                }
            })
        
        else:
            return JsonResponse({'status': 'error', 'message': '不支援的圖表類型'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'獲取圖表數據失敗：{str(e)}'})


@login_required
def salary_export(request):
    """薪資資料匯出功能"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    try:
        # 獲取篩選參數（與 SalaryListView 相同的邏輯）
        queryset = Salary.objects.select_related('employee', 'period').order_by('-period__start_date')
        
        employee_id = request.GET.get('employee')
        period_id = request.GET.get('period')
        year = request.GET.get('year')
        month = request.GET.get('month')
        status = request.GET.get('status')
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if period_id:
            queryset = queryset.filter(period_id=period_id)
        if year:
            queryset = queryset.filter(period__start_date__year=year)
        if month:
            queryset = queryset.filter(period__start_date__month=month)
        if status == 'confirmed':
            queryset = queryset.filter(is_confirmed=True)
        elif status == 'pending':
            queryset = queryset.filter(is_confirmed=False)
        
        # 獲取匯出格式和選項
        export_format = request.GET.get('format', 'csv')
        include_details = request.GET.get('include_details', 'true') == 'true'
        
        if export_format == 'csv':
            return _export_csv(queryset, include_details)
        else:
            return JsonResponse({'status': 'error', 'message': '不支援的匯出格式'})
    
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'匯出失敗：{str(e)}'})


def _export_csv(queryset, include_details=True):
    """匯出 CSV 格式"""
    output = io.StringIO()
    
    if include_details:
        # 詳細匯出
        fieldnames = [
            '員工姓名', '員工編號', '部門', '僱用類型',
            '薪資期間開始', '薪資期間結束', '發薪日期',
            '基本薪資', '工作時數', '加班時數', '加班費',
            '總薪資', '狀態', '最後更新時間'
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for salary in queryset:
            writer.writerow({
                '員工姓名': salary.employee.name,
                '員工編號': salary.employee.employee_id or '',
                '部門': salary.employee.department.name if salary.employee.department else '',
                '僱用類型': salary.employee.get_employment_type_display(),
                '薪資期間開始': salary.period.start_date.strftime('%Y-%m-%d'),
                '薪資期間結束': salary.period.end_date.strftime('%Y-%m-%d'),
                '發薪日期': salary.period.pay_date.strftime('%Y-%m-%d'),
                '基本薪資': float(salary.base_amount),
                '工作時數': float(salary.working_hours),
                '加班時數': float(salary.overtime_hours),
                '加班費': float(salary.overtime_amount),
                '總薪資': float(salary.total_salary),
                '狀態': '已確認' if salary.is_confirmed else '待確認',
                '最後更新時間': salary.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
    else:
        # 簡要匯出
        fieldnames = ['員工姓名', '薪資期間', '總薪資', '狀態']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for salary in queryset:
            writer.writerow({
                '員工姓名': salary.employee.name,
                '薪資期間': f"{salary.period.start_date} ~ {salary.period.end_date}",
                '總薪資': float(salary.total_salary),
                '狀態': '已確認' if salary.is_confirmed else '待確認',
            })
    
    # 創建 HTTP 響應
    response = HttpResponse(output.getvalue(), content_type='text/csv; charset=utf-8')
    
    # 設定檔案名
    from urllib.parse import quote
    filename = f"salary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'
    response['Content-Type'] = 'text/csv; charset=utf-8'
    
    return response


@login_required
def get_employee_salary_data(request):
    """獲取特定員工的薪資數據 - AJAX API"""
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': '權限不足'}, status=403)
    
    employee_id = request.GET.get('employee_id')
    if not employee_id:
        return JsonResponse({'status': 'error', 'message': '請提供員工ID'}, status=400)
    
    try:
        employee = Employee.objects.get(id=employee_id, active=True)
        
        # 獲取該員工的薪資記錄
        salaries = Salary.objects.filter(employee=employee).select_related('period').order_by('-period__start_date')
        
        # 應用其他篩選條件
        period_id = request.GET.get('period')
        year = request.GET.get('year')
        month = request.GET.get('month')
        status = request.GET.get('status')
        
        if period_id:
            salaries = salaries.filter(period_id=period_id)
        if year:
            salaries = salaries.filter(period__start_date__year=year)
        if month:
            salaries = salaries.filter(period__start_date__month=month)
        if status == 'confirmed':
            salaries = salaries.filter(is_confirmed=True)
        elif status == 'pending':
            salaries = salaries.filter(is_confirmed=False)
        
        # 構建薪資數據
        salary_data = []
        for salary in salaries:
            salary_data.append({
                'id': salary.id,
                'employee_name': salary.employee.name,
                'department_name': salary.employee.department.name if salary.employee.department else '',
                'period_start': salary.period.start_date.strftime('%Y-%m-%d'),
                'period_end': salary.period.end_date.strftime('%Y-%m-%d'),
                'pay_date': salary.period.pay_date.strftime('%Y-%m-%d'),
                'base_amount': float(salary.base_amount),
                'overtime_hours': float(salary.overtime_hours),
                'overtime_amount': float(salary.overtime_amount),
                'total_salary': float(salary.total_salary),
                'is_confirmed': salary.is_confirmed,
                'status_display': '已確認' if salary.is_confirmed else '待確認',
            })
        
        # 計算統計資訊
        total_records = len(salary_data)
        total_amount = sum(item['total_salary'] for item in salary_data)
        average_amount = total_amount / total_records if total_records > 0 else 0
        
        return JsonResponse({
            'status': 'success',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'department': employee.department.name if employee.department else ''
            },
            'salaries': salary_data,
            'statistics': {
                'total_records': total_records,
                'total_amount': total_amount,
                'average_amount': average_amount
            }
        })
        
    except Employee.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '找不到該員工'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'查詢失敗：{str(e)}'}, status=500)
    filename = f"salary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # 添加 BOM 以確保 Excel 正確顯示中文
    response.write('\ufeff')
    response.write(output.getvalue())
    
    return response
