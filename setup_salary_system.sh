#!/bin/bash
# 薪資系統初始化腳本

set -e  # 出錯時停止執行

echo "🏢 HR 薪資系統初始化"
echo "================================"
echo ""

# 檢查是否在正確的目錄
if [[ ! -f "manage.py" ]]; then
    echo "❌ 錯誤：請在專案根目錄下執行此腳本"
    exit 1
fi

# 檢查虛擬環境
if [[ -z "$VIRTUAL_ENV" ]] && [[ ! -d "venv" ]]; then
    echo "❌ 錯誤：找不到虛擬環境"
    echo "請先創建虛擬環境或啟用現有的虛擬環境"
    exit 1
fi

# 啟用虛擬環境（如果還沒啟用）
if [[ -z "$VIRTUAL_ENV" ]] && [[ -d "venv" ]]; then
    echo "🔄 啟用虛擬環境..."
    source venv/bin/activate
fi

echo "第一階段：資料庫遷移"
echo "================================"

# 建立新的遷移檔案
echo "🔄 建立資料庫遷移檔案..."
python manage.py makemigrations

# 套用遷移
echo "🔄 套用資料庫遷移..."
python manage.py migrate

echo "✅ 資料庫遷移完成"
echo ""

echo "第二階段：薪資系統設定"
echo "================================"

# 初始化薪資系統
echo "🔄 初始化薪資系統基本設定..."
python manage.py setup_salary_system

echo "✅ 薪資系統設定完成"
echo ""

echo "第三階段：建立測試資料"
echo "================================"

read -p "是否要建立測試資料？(y/n): " create_test_data

if [[ $create_test_data == "y" || $create_test_data == "Y" ]]; then
    echo "🔄 建立基本測試資料..."
    python scripts/create_simple_fake_data.py
    
    echo "🔄 建立打卡記錄..."
    python scripts/create_punch_records.py
    
    echo "✅ 測試資料建立完成"
else
    echo "⏭️  跳過測試資料建立"
fi

echo ""
echo "🎉 薪資系統初始化完成！"
echo ""
echo "接下來您可以："
echo "1. 啟動開發伺服器：python manage.py runserver"
echo "2. 訪問系統：http://127.0.0.1:8000"
echo "3. 管理後台：http://127.0.0.1:8000/admin"
echo "4. 薪資管理：http://127.0.0.1:8000/salary/"
echo ""
echo "預設管理員帳號："
echo "  用戶名：admin"
echo "  密碼：admin"
echo ""
echo "如需建立新的管理員帳號，請執行："
echo "  python manage.py createsuperuser"
