import re
from datetime import datetime, timedelta, timezone

import pandas as pd
import numpy as np

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

df = pd.read_csv("credit-dirty.csv", dtype=str, keep_default_na=False)
rows_before = len(df)

empty_id = df["ID"] == ""
duplicate_id = df["ID"].duplicated(keep="first") & (~empty_id)
reject_mask = empty_id | duplicate_id
df = df[~reject_mask].copy()

def clean_age(v):
    if v in ("", "unknown"):
        return ""
    try:
        age = int(v)
    except ValueError:
        return ""
    return "" if age < 0 else v

def normalize_signup_at(v):
    if v in ("", "not-a-date"):
        return ""
    m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", v)
    if m:
        mm, dd, yyyy = (int(x) for x in m.groups())
        dt = datetime(yyyy, mm, dd, tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    m = re.match(r"^(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2})([+-])(\d{2}):(\d{2})$", v)
    if m:
        yyyy, mm, dd, hh, mi = (int(x) for x in m.groups()[:5])
        sign = 1 if m.group(6) == "+" else -1
        offset = timedelta(hours=int(m.group(7)), minutes=int(m.group(8))) * sign
        local_dt = datetime(yyyy, mm, dd, hh, mi)
        utc_dt = (local_dt - offset).replace(tzinfo=timezone.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", v):
        return v
    return ""

def clean_bill_amt1(v):
    return "" if v in ("", "n/a") else v

df["AGE"] = df["AGE"].apply(clean_age)
df["signup_at"] = df["signup_at"].apply(normalize_signup_at)
df["BILL_AMT1"] = df["BILL_AMT1"].apply(clean_bill_amt1)

df.to_csv("credit-clean.csv", index=False)

rows_after = len(df)
print(f"處理前總列數：{rows_before}")
print(f"處理後總列數：{rows_after}")
print(f"被拒絕列數：{rows_before - rows_after}（空值 ID：{empty_id.sum()}，重複 ID：{duplicate_id.sum()}）")
