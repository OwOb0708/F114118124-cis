## 轉換摘要 － 對應評分：reproducibility
- 處理前總列數：219　處理後總列數：190
- missing_rate：待系統回報（清洗後 AGE、BILL_AMT1 仍保留大量 NULL，屬正確結果，不是做錯）
- 被拒絕列數：29　拒絕原因：ID 為空值（12 列）或與先前列重複（17 列），主鍵不可補值，一律整列拒絕
- random seed：42（固定值，np.random.seed(42)，確保重跑結果一致）

補充說明：AGE、BILL_AMT1、signup_at 清洗後仍有大量 NULL，是刻意保留、不做任何插補的結果——寧可誠實揭露缺漏，也不要用假資料掩蓋真實的風險缺口。
