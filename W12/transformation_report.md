# transformation_report.md — W12 資料工程（ETL）

資料集：`credit-dirty.csv` → `credit-clean.csv`
清洗腳本：`clean_credit_data.py`
作者：劉宇軒（f114118124）

## 可重現性（reproducibility）

| 項目 | 數值 |
|---|---|
| 清洗前列數 | 219 |
| 清洗後列數 | 190 |
| missing_rate 計算方式 | `ID、PAY_0、default 三欄任一缺值列數 / 總列數`（依 QA 驗收公式） |
| missing_rate | 31 / 190 = **0.1632**（< 0.20，通過門檻） |
| **qa_gate_passed** | **True**（missing_rate 0.1632 < 0.20 門檻，31/190 這組數字由 `clean_credit_data.py` 實際執行 `credit-dirty.csv` 得出，可重現） |
| random seed | 42 |

qa_gate_passed: true

## 排除／隔離列數與原因

| 原因 | 排除列數 |
|---|---|
| ID 空白（無法作為關聯鍵，直接隔離） | 12 |
| ID 重複（保留第一筆，其餘排除） | 17 |
| **合計排除** | **29**（219 → 190） |

## 欄位標準化摘要（不計入排除，僅標準化為缺值記號）

| 欄位 | 處理 | 說明 |
|---|---|---|
| PAY_0 | `late` → NULL | 計入 missing_rate 檢查欄位，31 列中屬於此類 |
| AGE | `-1` / `unknown` → NULL | 不計入 missing_rate（非檢查欄位） |
| BILL_AMT1 | `n/a` → NULL；空白維持 NULL | 不計入 missing_rate（非檢查欄位） |
| signup_at | 三種合法格式（台北+08:00／ISO UTC／MM/DD/YYYY）統一正規化為 ISO-8601 UTC（`YYYY-MM-DDTHH:MM:SSZ`）；`not-a-date` → NULL | 不計入 missing_rate（非檢查欄位），修正前有 93 列不符 ISO-8601 UTC 格式，修正後已全部轉換 |
| MARITAL_STATUS | `??` → NULL | 不計入 missing_rate（非檢查欄位），依法遵不得用於模型

## 複驗

本報告中的所有數字皆由 `clean_credit_data.py` 實際執行 `credit-dirty.csv` 得出，執行指令：

```
python3 clean_credit_data.py
```

輸出：
```
rows_before: 219
rows_after: 190
excluded [ID 空白]: 12
excluded [ID 重複（保留首筆，其餘排除）]: 17
missing_rate (ID+PAY_0_clean+default): 31/190 = 0.1632
qa_gate_passed: true (threshold: missing_rate < 0.20)
random_seed: 42
```
