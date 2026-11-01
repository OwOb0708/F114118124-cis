"""W12 信用卡申請資料清洗（F114118124）。

讀 credit-dirty.csv，依 decision_log.md 的規則清洗，輸出 credit-clean.csv。
排除與隔離的列另存 excluded_rows.csv（不交、不進模型），每一步都印出筆數，
最後跑 validate() 自我檢查輸出是否符合欄位規格；任何一項不符就丟出例外。

用法：python clean_credit_data.py [輸入檔] [輸出檔]
"""
import sys

import numpy as np
import pandas as pd

RANDOM_SEED = 42  # 本腳本沒有隨機步驟；保留固定 seed，日後加入抽樣時沿用
np.random.seed(RANDOM_SEED)

SRC = sys.argv[1] if len(sys.argv) > 1 else "credit-dirty.csv"
DST = sys.argv[2] if len(sys.argv) > 2 else "credit-clean.csv"
REQUIRED = ["ID", "PAY_0", "default"]


def log(step, n, note=""):
    print(f"[{step}] {n} 列 {note}".rstrip())


def to_utc_iso(raw):
    """signup_at 三種格式統一成 ISO-8601 UTC；無法解析回傳 None。

    - 2024-01-02T10:00:00Z：已是 UTC。
    - 2024/01/02 18:00+08:00：帶時區，換算成 UTC。
    - 01/02/2024：舊系統 MM/DD/YYYY、台北時間、只有日期（Client 確認），以當日 00:00 台北時間換算。
    """
    s = (raw or "").strip()
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y/%m/%d %H:%M%z"):
        t = pd.to_datetime(s, format=fmt, errors="coerce", utc=True)
        if not pd.isna(t):
            return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    t = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    if not pd.isna(t):
        return t.tz_localize("Asia/Taipei").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def clean(df):
    excluded = []
    log("讀入", len(df))

    # 1. ID 空白：申請編號是之後與還款紀錄對帳的鍵，不能補號（Client、PM 確認）→ 排除
    blank = df["ID"].str.strip() == ""
    excluded.append(df[blank].assign(reason="ID 空白，無法與還款紀錄對帳"))
    df = df[~blank].copy()
    log("排除空白 ID", int(blank.sum()), f"→ 剩 {len(df)}")

    # 2. 重複 ID：17 組全是整列完全相同的重複，保留第一筆，其餘隔離
    dup = df.duplicated(keep="first")
    conflict = df[~dup]["ID"].duplicated(keep=False)
    if conflict.any():  # 同 ID 但內容不同：無法判斷哪筆正確，全部隔離
        bad_ids = set(df[~dup][conflict]["ID"])
        excluded.append(df[df["ID"].isin(bad_ids)].assign(reason="同 ID 內容衝突"))
        df = df[~df["ID"].isin(bad_ids)].copy()
    excluded.append(df[dup].assign(reason="與同 ID 列完全相同的重複"))
    df = df[~dup].copy()
    log("隔離完全重複列", int(dup.sum()), f"→ 剩 {len(df)}")

    # 3. AGE：-1（舊系統預設）、unknown（紙本無法辨識）、空白（漏填）都是「不知道」→ NULL；超出 18–100 也設 NULL
    age = pd.to_numeric(df["AGE"], errors="coerce")
    age = age.where(age.between(18, 100))
    log("AGE 設為 NULL", int(age.isna().sum()))
    df["AGE"] = age.astype("Int64")

    # 4. PAY_0：late 表示已逾期但沒記錄月數（Client），硬補成 1 會低估嚴重程度 → NULL
    pay = pd.to_numeric(df["PAY_0"], errors="coerce")
    pay = pay.where(pay.between(-2, 9))
    log("PAY_0 設為 NULL", int(pay.isna().sum()), "（late）")
    df["PAY_0"] = pay.astype("Int64")

    # 5. BILL_AMT1：空白＝新戶尚未出帳，金額真的是 0；n/a＝帳務同步失敗，金額存在但未知 → NULL
    bill_raw = df["BILL_AMT1"].str.strip()
    bill = pd.to_numeric(bill_raw, errors="coerce")
    bill[bill_raw == ""] = 0
    log("BILL_AMT1 空白補 0", int((bill_raw == "").sum()), f"；n/a 設 NULL {int((bill_raw.str.lower() == 'n/a').sum())}")
    df["BILL_AMT1"] = bill

    # 6. signup_at：統一成 ISO-8601 UTC；not-a-date 無法還原 → NULL
    df["signup_at"] = df["signup_at"].map(to_utc_iso)
    log("signup_at 無法解析設 NULL", int(df["signup_at"].isna().sum()))

    # 7. default：目標變數，檢查只有 0／1
    df["default"] = pd.to_numeric(df["default"], errors="coerce").astype("Int64")

    # 8. 拿掉的欄位：MARITAL_STATUS 是受限特徵、Client 說依法不得用於授信，且 ??／NULL 是拒答；
    #    LEAK_FUTURE_DEFAULT 與 default 100% 相同，是申請當下拿不到的未來資訊（資料洩漏）
    df = df.drop(columns=["MARITAL_STATUS", "LEAK_FUTURE_DEFAULT"])
    log("移除欄位", 2, "MARITAL_STATUS、LEAK_FUTURE_DEFAULT")

    return df[["ID", "AGE", "PAY_0", "BILL_AMT1", "default", "signup_at"]], pd.concat(excluded, ignore_index=True)


def missing_rate(df):
    """與 AI QA 確認的定義：ID、PAY_0、default 任一缺值的列數 ÷ 總列數。"""
    return float(df[REQUIRED].isna().any(axis=1).mean())


def validate(df):
    """輸出自我檢查：欄位、主鍵、範圍與 missing_rate。"""
    assert all(c in df.columns for c in REQUIRED), "缺少必要欄位"
    assert df["ID"].notna().all() and df["ID"].is_unique, "ID 必須非空且不重複"
    assert df["AGE"].dropna().between(18, 100).all(), "AGE 超出 18–100"
    assert df["PAY_0"].dropna().between(-2, 9).all(), "PAY_0 超出 -2–9"
    assert set(df["default"].dropna().unique()) <= {0, 1}, "default 只能是 0／1"
    assert df["signup_at"].dropna().str.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z").all(), "signup_at 不是 ISO-8601 UTC"
    rate = missing_rate(df)
    assert rate < 0.20, f"missing_rate {rate:.3f} 未低於 0.20"
    return rate


if __name__ == "__main__":
    raw = pd.read_csv(SRC, dtype=str, keep_default_na=False)
    out, excluded = clean(raw)
    rate = validate(out)
    out.to_csv(DST, index=False)
    excluded.to_csv("excluded_rows.csv", index=False)
    print(f"[輸出] {DST}：{len(out)} 列；排除／隔離 {len(excluded)} 列；missing_rate = {rate:.4f}")
    print("[各欄空值]", out.isna().sum().to_dict())
