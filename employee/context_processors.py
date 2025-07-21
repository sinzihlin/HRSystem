from .models import Employee

def employee_context(request):
    employee_id = request.session.get('employee_id')
    employee = None
    if employee_id:
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            pass
    return {'current_employee': employee}