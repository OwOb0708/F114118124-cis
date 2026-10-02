"""
W12 ETL - credit-dirty.csv 清洗腳本
作者：劉宇軒 (f114118124)
依據 decision_log.md 中記錄的規則，對 credit-dirty.csv 進行清洗，
產出 credit-clean.csv，並計算可重現性所需的統計量。
"""

import pandas as pd
import numpy as np

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

INPUT_PATH = "credit-dirty.csv"
OUTPUT_PATH = "credit-clean.csv"

def main():
    df = pd.read_csv(INPUT_PATH, dtype=str)
    rows_before = len(df)

    excluded_log = []

    # 規則 1：ID 是申請案編號，之後要用來跟還款紀錄依 ID 對帳，
    # 不能自行補值或產生假編號 —— ID 空白的列直接排除（隔離），不清洗。
    blank_id_mask = df["ID"].isna()
    excluded_log.append(("ID 空白", int(blank_id_mask.sum())))
    df = df[~blank_id_mask].copy()

    # 規則 2：ID 理論上應唯一（申請案編號），重複 ID 視為同一申請案的
    # 重複上傳，保留第一筆、其餘隔離排除，避免同一筆申請案被重複計入
    # missing_rate 與後續 W13/W14 的分析。
    dup_mask = df.duplicated(subset="ID", keep="first")
    excluded_log.append(("ID 重複（保留首筆，其餘排除）", int(dup_mask.sum())))
    df = df[~dup_mask].copy()

    rows_after_exclusion = len(df)

    # 規則 3：AGE 的 -1 是舊系統「未填」的預設值、unknown 是同義的缺值標記。
    # 業務上只核卡給 18 歲以上，但年齡本身不是 missing_rate 檢查欄位，
    # 這裡只做標準化，不做數值填補（避免誤導 W14 建模）。
    df["AGE_clean"] = df["AGE"].replace({"unknown": pd.NA, "-1": pd.NA})

    # 規則 4：PAY_0 的 "late" 是舊系統人工標記的「有逾期，但不知道逾期
    # 幾個月（至少 1 個月）」。這跟欄位規格定義的數值代碼（-2~9）語意不同、
    # 無法轉成具體代碼，Client 也只能說「僅知有逾期未知月數」，所以在
    # missing_rate 的檢查欄位中，把 late 視為「有資料但資訊不足以使用」，
    # 標記為缺值（NULL），而不是自行猜一個代碼（例如猜成 1）。
    df["PAY_0_clean"] = df["PAY_0"].replace({"late": pd.NA})

    # 規則 5：BILL_AMT1 空白＝該期還沒出帳，n/a＝帳務同步失敗。兩者語意
    # 不同，但都不是「使用者可清洗出正確數字」的情況，保留原樣（不猜測
    # 金額），交由後續分析自行決定是否排除含空值的列。
    df["BILL_AMT1_clean"] = df["BILL_AMT1"].replace({"n/a": pd.NA})

    # 規則 6：signup_at 有三種合法格式（台北時間+08:00／ISO UTC／
    # MM/DD/YYYY）混用，加上 "not-a-date" 的壞值。换算後三種合法格式
    # 全部指向同一個時間點，正規化後這欄沒有資訊量，這裡只標準化壞值，
    # 不做時區換算（換算與否不影響 missing_rate，留給需要時區資訊的人
    # 自己決定怎麼處理）。
    df["signup_at_clean"] = df["signup_at"].replace({"not-a-date": pd.NA})

    # 規則 7：MARITAL_STATUS 的 ?? 或 NULL 是申請人拒答，且依法遵規定
    # 不得用於授信模型 —— 統一標準化成缺值記號，但「不花力氣」去填補，
    # 因為這欄本來就不該進模型。
    df["MARITAL_STATUS_clean"] = df["MARITAL_STATUS"].replace({"??": pd.NA})

    # ---- missing_rate 計算（依 QA 規則：ID、PAY_0、default 三欄
    #      任一缺值列數 / 總列數，須 < 0.20）----
    check_cols = ["ID", "PAY_0_clean", "default"]
    missing_mask = df[check_cols].isna().any(axis=1)
    missing_rows = int(missing_mask.sum())
    rows_final = len(df)
    missing_rate = missing_rows / rows_final if rows_final else 0.0

    # 輸出清洗後資料（維持欄位可讀性，保留 _clean 後綴供報告使用，
    # 同時也輸出一份覆蓋原欄名的版本給下游 W13/W14 使用）
    out = df.copy()
    out["AGE"] = out["AGE_clean"]
    out["PAY_0"] = out["PAY_0_clean"]
    out["BILL_AMT1"] = out["BILL_AMT1_clean"]
    out["signup_at"] = out["signup_at_clean"]
    out["MARITAL_STATUS"] = out["MARITAL_STATUS_clean"]
    out = out[["ID", "AGE", "MARITAL_STATUS", "PAY_0", "BILL_AMT1",
               "default", "signup_at", "LEAK_FUTURE_DEFAULT"]]
    out.to_csv(OUTPUT_PATH, index=False)

    # ---- 列印 transformation_report.md 所需的可重現性數字 ----
    print("=== reproducibility ===")
    print(f"rows_before: {rows_before}")
    print(f"rows_after: {rows_final}")
    for reason, cnt in excluded_log:
        print(f"excluded [{reason}]: {cnt}")
    print(f"missing_rate ({'+'.join(check_cols)}): {missing_rows}/{rows_final} = {missing_rate:.4f}")
    print(f"random_seed: {RANDOM_SEED}")

if __name__ == "__main__":
    main()
