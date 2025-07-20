FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案文件
COPY . .

# 收集靜態文件
RUN python manage.py collectstatic --noinput

# 暴露端口
EXPOSE 8000

# 運行指令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
