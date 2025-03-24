# LeetCode Discord Bot

這是一個功能豐富的 Discord 機器人，專為 LeetCode 使用者設計。它能夠自動抽取 LeetCode 題目、發送每日挑戰，並支援多種互動命令。

## 功能特點

- **隨機抽題**：根據難度等級（簡單、中等、困難）隨機抽取 LeetCode 題目
- **每日挑戰**：自動或手動發送 LeetCode 官方每日挑戰題目
- **定時提醒**：每天早上 10:00（台灣時間）自動發送每日挑戰到指定頻道
- **防卷保護**：凌晨 2:00-6:00 期間會提醒使用者休息，不提供題目

## 使用指南

### 基本命令

- `抽` - 隨機抽取任意難度的 LeetCode 題目
- `抽e` - 隨機抽取簡單 (Easy) 難度的題目
- `抽m` - 隨機抽取中等 (Medium) 難度的題目
- `抽h` - 隨機抽取困難 (Hard) 難度的題目
- `每日挑戰` - 取得今天的 LeetCode 官方每日挑戰題目
- `發送每日挑戰` - 管理員專用命令，手動將每日挑戰發送到指定頻道

### 設定頻道

機器人會在指定的頻道自動發送每日挑戰。您可以透過修改程式碼中的 `DAILY_CHALLENGE_CHANNEL_ID` 變數來設定目標頻道：

```python
DAILY_CHALLENGE_CHANNEL_ID = 您的頻道ID
```

## 安裝步驟

1. 確保您已安裝 Python 3.8 或更高版本
2. Clone 此專案或下載源碼
3. 安裝所需依賴：
   ```
   pip install discord requests beautifulsoup4 pytz
   ```
4. 在 [Discord Developer Portal](https://discord.com/developers/applications) 建立新的應用程式並獲取機器人 Token
5. 將機器人 Token 設置在環境變數或配置文件中（推薦使用 `.env` 文件）
6. 啟動機器人：
   ```
   python leetcode_DC_bot.py
   ```

## 環境變數設定

創建一個 `.env` 檔案，並添加以下內容：

```
DISCORD_BOT_TOKEN="您的機器人Token"
DAILY_CHALLENGE_CHANNEL_ID = 你的頻道ID
```

請勿直接在代碼中硬編碼 Token，這會造成安全風險。

## 技術細節

- 使用 Discord.py 庫與 Discord API 連接
- 透過 LeetCode API 和 GraphQL 查詢獲取題目資訊
- 使用 BeautifulSoup 解析 HTML 內容
- 使用 asyncio 實現定時任務
- 使用 pytz 處理時區問題

## 自定義與擴展

您可以根據需求修改以下部分：

- 調整定時發送的時間（目前設為早上 10:00）
- 更改防卷保護的時間範圍（目前為凌晨 2:00-6:00）
- 自定義嵌入訊息的顏色和格式
- 增加更多指令或功能

## 注意事項

- 請妥善保管您的 Discord Bot Token，不要將其公開
- LeetCode API 可能會有變更，需要定期檢查程式碼是否需要更新
- 機器人運行需要持續的網絡連接
- 如遇到連接問題，機器人會自動嘗試重新連接

## 故障排除

### 常見問題

1. **無法獲取題目** - 檢查網絡連接和 LeetCode API 狀態
2. **機器人無法發送訊息** - 確認機器人擁有正確的權限
3. **定時發送失敗** - 檢查時區設置和系統時間是否正確
4. **機器人離線** - 檢查 Token 是否有效，以及網絡連接是否穩定

### 日誌分析

程式會輸出詳細的日誌，包括：
- 連接狀態
- 定時任務執行情況
- 錯誤訊息

請根據錯誤信息進行故障診斷。

## 貢獻與反饋

歡迎提出建議、報告問題或貢獻代碼。您可以通過 GitHub 聯繫我們。
