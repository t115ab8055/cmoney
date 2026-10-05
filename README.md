# CMoney 股市爆料同學會爬蟲

使用 Python `requests` 直接呼叫 CMoney 個股文章 API，透過時間 cursor 與多執行緒擷取文章，依文章 ID 合併去重後匯出 CSV。目前 `thread` branch 的主流程不使用 Playwright，也不需要安裝瀏覽器。

## 安裝與執行

環境需求：Python 3.14 以上與 uv。在專案根目錄執行：

```bash
uv sync
mkdir -p output
uv run python main.py
```

預設執行 `main(code="2317")`，年份固定為 `2026`。如需更換股票，修改 `main.py` 最下方的呼叫，例如：

```python
main(code="6214")
```

目前沒有命令列參數。年份分別寫在 `main()` 的 cursor 產生呼叫、`get_cmoney_monthly_records()` 的日期邊界及訊息中，修改時需一併調整。

## 擷取流程

1. 呼叫 `https://www.cmoney.tw/api/mach/api/Article/Stocks/{code}/AllLatest`，每次請求設定 `limit=20`、逾時 30 秒。
2. 使用 `cursor.py` 將指定的臺北時間轉成數值 cursor；後續分頁使用 API 回傳的 `nextCursor`。
3. `get_yearly_cursors(2026)` 以 `range(1, 12)` 產生 1 月至 11 月月初的 cursor，再反轉清單。
4. 使用 `ThreadPoolExecutor` 啟動 10 個任務，以 11 月至 2 月月初的 cursor 作為起點，並以各自同一個月的月初作為停止邊界。
5. 各任務在 cursor 為空、解析不到文章，或遇到建立時間小於等於日期邊界時停止。主流程收集結果，以文章 ID 合併去重，再匯出 CSV。

## 輸出資料

主流程寫入 `output/{股票代碼}.csv`，例如 `output/2317.csv`。使用 UTF-8 BOM 編碼，方便以 Excel 開啟；重跑會覆寫同名檔案，不會讀取舊檔續抓，也未額外依日期排序。

| CSV 欄位 | 內容 |
| --- | --- |
| 文章 ID、創建者 ID | 文章與作者識別碼 |
| 創建時間 | `YYYY/MM/DD HH:MM:SS`，由毫秒 timestamp 轉換 |
| 標題、文章內容 | 文章標題與文字內文 |
| 標記的股票 | 股票代碼與名稱欄位組成的清單字串，例如 `[['2317', 0]]`；名稱目前固定為 `0` |
| 被donate P點 | 文章收到的贊助 P 點 |
| 評論數 | 僅有數量，不包含評論內文 |
| 回應表情 讚／哈／賺／哇／嗚嗚／真的嗎／怒 | 七種表情的回應數，缺少時填 `0` |

`export.py` 仍保留 `export_json()`，但主流程未呼叫。解析結果含有 `datetime` 型別的 `create_time`，現有 JSON 匯出函式未處理此型別，不能直接將目前結果交給它匯出。目錄內既有 JSON 或 CSV 不代表本次執行結果或完整年度資料。

## 檔案結構

| 檔案 | 用途 |
| --- | --- |
| `main.py` | API 請求、分頁、日期邊界判斷、多執行緒及主流程 |
| `cursor.py` | 以 `Asia/Taipei` 時區計算起始 cursor |
| `parse.py` | 解析文章欄位、建立時間與表情統計 |
| `export.py` | CSV 匯出及未啟用的 JSON 匯出函式 |
| `pyproject.toml`、`uv.lock` | Python 版本、相依套件與鎖定版本 |

## 目前限制

- `main.py` 的 `get_parameter()` 使用寫在程式中的 Bearer token，沒有自動取得或更新機制；執行需要有效的授權標頭。
- API 請求目前使用 `verify=False` 並停用相關警告，未驗證 HTTPS 憑證。
- 回應解析只接受完全符合 `application/json; charset=utf-8` 的 Content-Type；其他格式可能造成未定義變數錯誤，也沒有 HTTP 狀態碼檢查、重試或個別任務失敗後繼續匯出的處理。
- 尚未設定請求間隔、最大頁數或重複 cursor 停止條件；若 API 持續回傳相同頁面且未觸及日期邊界，可能持續請求。
- cursor 以臺北時區計算，但文章時間使用執行電腦的本地時區，日期比較也未帶時區；在不同時區執行可能產生邊界差異。文章缺少有效建立時間時也可能導致比較失敗。
- 擷取依賴 API 格式與 cursor 行為；目前的月份及批次邊界處理不保證指定期間資料完整或精確。
