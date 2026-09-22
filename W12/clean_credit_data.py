"""診斷測試腳本：刻意整欄刪除 AGE、BILL_AMT1，用來驗證系統是否真的擋這種處理方式。"""
import pandas as pd

RANDOM_SEED = 42
df = pd.read_csv("credit-dirty.csv", dtype=str, keep_default_na=False)

empty_id = df["ID"] == ""
dup_id = df["ID"].duplicated(keep="first") & (~empty_id)
df = df[~(empty_id | dup_id)].copy()

df = df.drop(columns=["AGE", "BILL_AMT1"])  # 診斷測試：整欄刪除

df.to_csv("credit-clean.csv", index=False)
print(f"rows: {len(df)}")
