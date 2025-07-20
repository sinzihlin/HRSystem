# Gemini 自訂檔案

此檔案可幫助 Gemini 了解您專案的特定慣例、技術和需求。透過提供這些資訊，您可以獲得更準確、更相關的協助。

## 專案概觀

這是一個使用 Python 和 Django 建置的人力資源薪資管理系統，包含員工資料管理、打卡、請假申請與審核、以及員工詳細資料查看功能。系統提供了友好的用戶界面，包括員工列表視圖、詳細資料頁面和側邊導航，方便在員工之間快速切換。

## 使用的技術

- 語言：Python 3.11+
- 框架：Django 5.2.4
- 前端：HTML, CSS, JavaScript (原生)
- 資料庫：SQLite
- AJAX：處理非同步請求
- 互動式 UI：模態視窗、表單處理、實時搜尋功能

## 編碼風格與慣例

- Python 程式碼遵循 PEP 8 規範
- Django 模板使用 Django 模板語言 (DTL)
- CSS 使用類選擇器，遵循 BEM 命名方式
- JavaScript 使用 ES6+ 語法
- 變數和函數名稱使用駝峰式命名法 (camelCase)
- 資料庫模型採用單數名稱

## 重要指令

- **安裝相依套件:** `pip install -r requirements.txt`
- **套用資料庫遷移:** `python manage.py migrate`
- **建立管理員帳號 (非互動式):** `python manage.py createsuperuser --noinput --username admin --email admin@example.com`
- **設定管理員密碼:** `echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('admin'); user.save()" | python manage.py shell`
- **啟動開發伺服器：** `python manage.py runserver 8002` (目前運行在 8002 埠)
- **執行測試：** `python manage.py test`
- **匯入員工資料 (CLI):** `python manage.py import_employees <您的CSV檔案路徑>`
- **生成測試資料:** `python create_fake_data.py`
- **訪問員工列表 (前端):** `http://127.0.0.1:8002/employees/`
- **訪問管理後台:** `http://127.0.0.1:8002/admin`

## 功能特性

- **員工管理:** 新增、編輯、刪除和檢視員工資料
- **CSV匯入:** 批次匯入員工資料
- **打卡功能:** 記錄上下班時間，支援自訂日期時間
- **請假系統:** 申請與審核多種類型的請假
- **薪資計算:** 根據設定的規則計算員工薪資
- **員工詳細資料:** 完整展示員工基本資料、打卡記錄、請假歷史
- **側邊導航:** 在員工詳細資料頁面提供側邊員工列表，便於快速切換
- **搜尋功能:** 在側邊列表中實時搜尋員工名稱

## 資料模型結構

- **Employee:** 員工基本資料 (姓名、郵件、電話、部門、到職日期)
- **Department:** 部門資訊 (名稱)
- **Salary:** 薪資資料 (基本薪資、獎金、扣除額、支付日期)
- **Punch:** 打卡記錄 (員工、時間、類型)
- **Leave:** 請假記錄 (員工、類型、開始日期、結束日期、原因、狀態)

## 使用者偏好

- 請用繁體中文提供說明。
- 代碼示例請提供詳細註解。
- 優先考慮易於維護和擴展的解決方案。
