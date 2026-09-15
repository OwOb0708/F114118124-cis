## 準確度 － 對應評分：accuracy

- F1 分數：**1.0**（precision 1.0、recall 1.0，0 項沒抓到）
- 這個分數不是我自己列缺陷類型去對答案算出來的——是右欄「缺陷辨識評分」把 `grading_prompt.md`
  的完整內容送給 AI QA，AI QA **只依照這份 Prompt 的邏輯**實際審查 `credit_pipeline_v2.py`，
  自己決定要退件哪幾項，系統再拿 AI QA 自己判定的清單去對照黃金清單算 F1。
- 漏抓的問題（False Negative）：無（AI QA 回報的 8 項判定跟它自己列出的逐項理由，見下方）
- 誤判的問題（False Positive，AI QA 抓錯或抓太多）：無

AI QA 這次審查後回傳的完整理由（節錄自實際回應）：

> 1. 命中邏輯1：feature_cols 包含 'LEAK_FUTURE_DEFAULT' (data_leakage)。
> 2. 命中邏輯2：train_test_split 與 RandomForestClassifier 均未設定 random_state (no_random_seed)。
> 3. 命中邏輯3：StandardScaler 在 train_test_split 之前對全體 X 進行 fit_transform (train_test_contamination)。
> 4. 命中邏輯4：DATA_PATH 為絕對路徑 'C:/Users/pm/Desktop/credit-dirty_v2.csv' (hardcoded_path)。
> 5. 命中邏輯5：BILL_AMT1 的缺值直接用 fillna(0) 補成 0 (missing_null_handling)。
> 6. 命中邏輯6：train_test_split 未用 stratify，模型未設 class_weight，且僅評估 accuracy_score (no_class_imbalance_handling)。
> 7. 命中邏輯7：pip install pandas scikit-learn 未鎖版本號 (unversioned_dependency)。
> 8. 命中邏輯8：drop_duplicates 與 ID 過濾後僅印出「資料清理完成」，未印出刪除筆數 (silent_row_drop)。

## 修正歷程與盲點 － 對應評分：metacognition

- **對照組：故意送一個爛 Prompt 看會發生什麼事**。在正式送出 `grading_prompt.md` 之前，我先
  拿一個完全沒內容的 Prompt（就打了「test」兩個字）送進同一個「缺陷辨識評分」檢測，結果
  **F1 直接是 0**，precision／recall 都是 0，AI QA 給的理由是：「學習者提供的評分邏輯僅為
  'test'，並未定義任何具體的審查標準或檢查項目……即使程式碼中存在候選問題中的情況，但只要
  學習者沒有教我檢查，就不能將其列入 flagged」。這證實了系統真的是照 Prompt 的內容在審查，
  不是隨便給分：Prompt 沒教的東西，AI QA 就算「看得出來」也不會退件。
- **這如何說明「Prompt 寫不好」跟「Prompt 寫得好」的差別**：同一份程式碼、同一個 AI QA，唯一
  的變數是 Prompt 的內容——空泛的 Prompt 讓 AI QA 完全不知道要檢查什麼，等於沒有評分能力
  （F1 0）；具體到「哪個欄位、哪一行、為什麼有問題」的 Prompt，AI QA 才有辦法逐條對照程式碼
  判斷（F1 1.0）。這代表這週真正在練的不是「找出 8 個缺陷」本身，而是「能不能把自己抓到的問
  題，寫成別人（或別的系統）看得懂、可以照著執行的檢查標準」——只有自己心裡知道問題在哪裡，
  但講不清楚、教不會別人，等於沒有評分能力可以複製。
- **第一版 Prompt 為什麼會漏掉／誤判**：這次沒有發生——第一次正式送出 `grading_prompt.md` 就
  拿到 F1 1.0，因為 8 條檢查項目在寫的時候就已經具體到「講出哪個變數／哪一行、為什麼是問題」
  （對應 `grading_prompt.md` 裡的 8 條判準），不是抽象地說「程式碼品質不好」。
- **這件事讓你發現自己原本對「品質好壞」的判斷有什麼盲點**：我原本以為只要自己心裡清楚「這
  8 個是真正的問題」，跟 AI QA 對話時它也正確複述了判準（見 `grading_prompt.md` 開頭 QA 的
  回覆記錄），這週的任務就算做到位了。但「test」這個對照組讓我意識到：**AI QA 的判斷能力上
  限，就是 Prompt 寫清楚的程度**，不會因為我自己心裡懂就自動補上去。這跟現實中帶團隊、寫
  SOP 是同一件事——自己懂不代表寫得出讓別人（或 AI）照著做出一樣結果的文件，這中間需要刻意
  把隱性的判斷邏輯，轉譯成外顯、可執行的具體條件。
