# W12 轉換摘要

> 由 clean_credit_data.py 實際執行產生（Python 3、pandas 2.3.3），以下數字取自腳本輸出，可重跑得到相同結果。

## 轉換摘要 － 對應評分：reproducibility
- 處理前總列數：219　處理後總列數：190
- 被排除／隔離的列數：29　原因：ID 空白 12 列（無法與還款紀錄對帳，不能補號）；與同 ID 列完全相同的重複 17 列（保留第一筆）。排除與隔離的列存成 excluded_rows.csv 留作稽核，不放進清洗後資料。
- 做了哪些轉換（逐步寫，至少三個步驟或三個欄位各自的處理）：
  1. ID：排除空白 12 列 → 207 列；隔離完全重複 17 列 → 190 列。
  2. AGE：-1、unknown、空白與超出 18–100 的值設 NULL，共 141 列；其餘轉成整數。
  3. PAY_0：late 設 NULL，共 31 列；其餘轉成整數（範圍 -2–2，符合規格 -2–9）。
  4. BILL_AMT1：空白補 0（68 列，新戶尚未出帳）；n/a 設 NULL（59 列，帳務同步失敗）。
  5. signup_at：三種格式統一成 ISO-8601 UTC；not-a-date 設 NULL，共 50 列。
  6. 移除 MARITAL_STATUS（受限特徵）與 LEAK_FUTURE_DEFAULT（資料洩漏）兩欄。
  7. 輸出前執行 validate()：必要欄位存在、ID 非空且唯一、AGE／PAY_0／default 範圍、signup_at 格式、missing_rate < 0.20，全部通過才寫出檔案。
- missing_rate：0.1632（門檻 < 20%；計算方式與範圍：與 AI QA 確認的定義，必要欄位 ID、PAY_0、default 任一缺值的列數 ÷ 清洗後總列數 = 31 ÷ 190。缺值全部來自 PAY_0 的 late）
- random seed：42（固定值，確保重跑結果一致；本腳本沒有隨機步驟）

## 清洗後各欄空值（腳本輸出）
| 欄位 | 空值列數 | 比例 |
|---|---|---|
| ID | 0 | 0% |
| AGE | 141 | 74.2% |
| PAY_0 | 31 | 16.3% |
| BILL_AMT1 | 59 | 31.1% |
| default | 0 | 0% |
| signup_at | 50 | 26.3% |

## 重跑方式
```
python clean_credit_data.py credit-dirty.csv credit-clean.csv
```
