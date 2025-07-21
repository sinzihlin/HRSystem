#!/bin/bash
# HR 系統測試資料生成工具

set -e  # 出錯時停止執行

echo "🏢 HR 系統測試資料生成工具"
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

echo "請選擇要執行的腳本："
echo ""
echo "1. 基本測試資料 (推薦新手)"
echo "   - 創建 5 個部門和 5 名員工"
echo "   - 適合初次設置系統"
echo ""
echo "2. 完整測試資料"
echo "   - 包含員工、薪資、打卡和請假記錄"
echo "   - 適合完整功能測試"
echo ""
echo "3. 擴充員工資料"
echo "   - 增加更多員工（共15名）"
echo "   - 適合測試大量資料"
echo ""
echo "4. 打卡記錄"
echo "   - 只生成打卡記錄（兩個月）"
echo "   - 適合測試考勤功能"
echo ""
echo "5. 全部執行 (1+4)"
echo "   - 基本資料 + 打卡記錄"
echo "   - 推薦完整設置"
echo ""
echo "6. 資料庫健康檢查"
echo "   - 檢查系統狀態"
echo ""
echo "0. 退出"
echo ""

read -p "請選擇 (0-6): " choice

case $choice in
    1)
        echo "🔄 創建基本測試資料..."
        python scripts/create_simple_fake_data.py
        echo "✅ 基本測試資料創建完成！"
        ;;
    2)
        echo "🔄 創建完整測試資料..."
        python scripts/create_fake_data.py
        echo "✅ 完整測試資料創建完成！"
        ;;
    3)
        echo "🔄 創建擴充員工資料..."
        python scripts/create_more_fake_data.py
        echo "✅ 擴充員工資料創建完成！"
        ;;
    4)
        echo "🔄 創建打卡記錄..."
        python scripts/create_punch_records.py
        echo "✅ 打卡記錄創建完成！"
        ;;
    5)
        echo "🔄 執行完整設置..."
        echo "步驟 1/2: 創建基本測試資料..."
        python scripts/create_simple_fake_data.py
        echo "步驟 2/2: 創建打卡記錄..."
        python scripts/create_punch_records.py
        echo "✅ 完整設置完成！"
        ;;
    6)
        echo "🔄 執行資料庫健康檢查..."
        python manage.py db_health_check
        echo "✅ 健康檢查完成！"
        ;;
    0)
        echo "👋 再見！"
        exit 0
        ;;
    *)
        echo "❌ 無效選擇，請重新執行腳本"
        exit 1
        ;;
esac

echo ""
echo "🎉 完成！您現在可以："
echo "   - 啟動開發伺服器：python manage.py runserver"
echo "   - 訪問系統：http://127.0.0.1:8000"
echo "   - 管理後台：http://127.0.0.1:8000/admin"
echo "   - 健康檢查：http://127.0.0.1:8000/api/health/"
