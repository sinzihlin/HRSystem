# Gemini 自訂檔案

此檔案可幫助 Gemini 了解您專案的特定慣例、技術和需求。透過提供這些資訊，您可以獲得更準確、更相關的協助。

## 專案概觀

這是一個使用 Python 和 Django 建置的現代化人力資源薪資管理系統，提供完整的員工資料管理、智能薪資計算、打卡記錄、請假申請與審核流程等功能。特別針對中小型企業的人事管理需求設計，具備高度自動化和智能化特色。

### ✨ 最新亮點 (v2.2.0)
- **進階薪資篩選**: 新增年份、月份、狀態等多重篩選條件
- **統計資訊面板**: 即時顯示薪資記錄總數、總薪資和平均薪資
- **互動式圖表系統**: 月度薪資趨勢圖、部門薪資分析圖、薪資分布圖
- **資料匯出功能**: 支援 CSV 格式匯出，包含詳細和簡要兩種模式
- **響應式設計**: 完整的行動裝置適配

## 使用的技術

- 語言：Python 3.11+
- 框架：Django 5.2.4
- 前端：HTML, CSS, JavaScript (ES6+), Bootstrap 5, jQuery 3.6+, Chart.js, DataTables, Font Awesome
- 資料庫：PostgreSQL 13+ (Docker 環境), SQLite 3 (開發環境)
- API：RESTful JSON API
- 計算引擎：`SalaryCalculationService`, `Decimal`
- 快取：Django 內建快取系統
- 任務佇列：Celery (用於排程任務)
- 互動式 UI：模態視窗、表單處理、實時搜尋功能, AJAX

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
- **啟動開發伺服器：** `python manage.py runserver`
- **執行測試：** `python manage.py test`
- **匯入員工資料 (CLI):** `python manage.py import_employees <您的CSV檔案路徑>`
- **生成測試資料:**
    - **快速設置 (推薦):** `./setup_data.sh`
    - **手動執行 (可選):**
        - `python scripts/create_simple_fake_data.py`
        - `python scripts/create_fake_data.py`
        - `python scripts/create_more_fake_data.py`
        - `python scripts/create_punch_records.py`
- **訪問員工列表 (前端):** `http://127.0.0.1:8000/employees/`
- **訪問管理後台:** `http://127.0.0.1:8000/admin`
- **訪問登入頁面:** `http://127.0.0.1:8000/login/`

## 功能特性

- **員工管理:** 新增、編輯、刪除和檢視員工資料，支援 CSV 批次匯入功能，部門管理，員工詳細資料頁面（含側邊欄快速切換）
- **智能薪資計算系統:**
    - 彈性薪資結構（正職月薪制、兼職時薪制）
    - 自動薪資計算（底薪、獎金、扣除額）
    - 請假扣款自動化（事假、病假等無薪假）
    - 精確加班費計算（平日1.33倍、假日2.0倍，自動識別國定假日和週末）
    - 自動稅務計算（勞保費、健保費、所得稅）
    - 薪資計算預覽（即時預覽，詳細計算明細）
    - 薪資單生成
- **出勤管理:** 記錄員工的上下班打卡時間，包含日期與時間自訂，工時統計，班別管理
- **請假管理:** 申請與審核多種類型的請假，HR 審核機制，請假通知，請假歷史
- **系統安全與管理:** 管理後台，前端互動（模態視窗，無刷新操作），安全認證（登入驗證，CSRF 保護），權限控制

## 資料模型結構

- **Employee:** 員工基本資料 (姓名、郵件、電話、部門、到職日期)
- **Department:** 部門資訊 (名稱)
- **Salary:** 薪資資料 (基本薪資、獎金、扣除額、支付日期)
- **Punch:** 打卡記錄 (員工、時間、類型)
- **Leave:** 請假記錄 (員工、類型、開始日期、結束日期、原因、狀態)
- **PayrollPeriod:** 薪資週期
- **SalaryItem:** 薪資項目
- **WorkSchedule:** 工作排程

## 使用者偏好

- 請用繁體中文提供說明。
- 代碼示例請提供詳細註解。
- 優先考慮易於維護和擴展的解決方案。