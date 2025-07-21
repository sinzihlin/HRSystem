# Scripts 資料夾

這個資料夾包含所有用於創建測試資料的腳本檔案。

## 檔案說明

### 1. `create_simple_fake_data.py`
- **用途**: 創建基本的測試資料（部門和員工）
- **特點**: 簡單易用，適合初始化系統
- **包含**: 5個部門、5名員工（4名正職、1名兼職）
- **使用**: `python scripts/create_simple_fake_data.py`

### 2. `create_fake_data.py`
- **用途**: 創建完整的測試資料
- **特點**: 包含員工、薪資記錄、打卡記錄和請假記錄
- **包含**: 基本員工資料 + 兩個月的打卡記錄 + 請假記錄
- **使用**: `python scripts/create_fake_data.py`

### 3. `create_more_fake_data.py`
- **用途**: 創建更多員工資料和詳細打卡記錄
- **特點**: 增加員工數量，模擬更真實的工作場景
- **包含**: 額外10名員工 + 詳細的上下班打卡模式
- **使用**: `python scripts/create_more_fake_data.py`

### 4. `create_punch_records.py`
- **用途**: 專門用於創建打卡記錄
- **特點**: 生成現實化的打卡時間模式
- **包含**: 兩個月的詳細打卡記錄（工作日）
- **使用**: `python scripts/create_punch_records.py`

## 使用順序建議

1. **初次設置**: 使用 `create_simple_fake_data.py`
2. **需要完整資料**: 使用 `create_fake_data.py`
3. **需要更多員工**: 使用 `create_more_fake_data.py`
4. **只需打卡記錄**: 使用 `create_punch_records.py`

## 執行方式

所有腳本都需要在專案根目錄下執行：

```bash
# 啟用虛擬環境
source venv/bin/activate

# 執行腳本
python scripts/create_simple_fake_data.py
python scripts/create_fake_data.py
python scripts/create_more_fake_data.py
python scripts/create_punch_records.py
```

## 注意事項

- 執行腳本前請確保已經完成資料庫遷移 (`python manage.py migrate`)
- 部分腳本會清除現有資料，請謹慎使用
- 建議在開發環境中使用，避免在正式環境執行
