import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from employee.models import Department, Employee

class Command(BaseCommand):
    help = 'Imports employee data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import.')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    department_name = row['department_name']
                    department, created = Department.objects.get_or_create(name=department_name)

                    hire_date_str = row['hire_date']
                    hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()

                    employee, created = Employee.objects.update_or_create(
                        email=row['email'], # 使用 email 作為唯一識別碼
                        defaults={
                            'name': row['name'],
                            'phone': row['phone'],
                            'department': department,
                            'hire_date': hire_date,
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f'成功建立員工: {employee.name}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'成功更新員工: {employee.name}'))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f'錯誤: 檔案未找到 - {csv_file_path}'))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f'錯誤: CSV 檔案缺少必要的欄位 - {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'匯入時發生錯誤: {e}'))
