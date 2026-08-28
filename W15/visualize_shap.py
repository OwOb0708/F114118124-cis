"""W15 XAI：產生申請案 APP-20260312-0417 的 SHAP 貢獻度瀑布圖（Waterfall Plot）。

APP-20260312-0417 是劇本虛構的案號，整個平台從未訓練過真正的模型、也沒有這筆申請人的
真實資料（CIS_ENABLE_SANDBOX 預設關閉，見 backend/cis/sandbox.py，系統從不執行程式碼；
domains/ 目錄裡也搜不到這個案號對應的任何一筆真實資料列）。所以下面這組貢獻度數字不是
算出來的，是根據 W12 EDA 的真實統計模式（PAY_0 與違約率的已知關係、signup_at 帳齡效應）
編寫的示範用途數字，用來說明「如果要解釋，該用什麼方法、長什麼樣子」，不是這個模型真正
算出來的 SHAP 輸出——這點在 xai_report.md 也有註明。

原本第一版用簡單長條圖，只畫出兩個特徵各自的貢獻度數字，看不出「為什麼會被拒絕」——沒
有基準線、沒有終點，客戶看了還是要自己拼湊。瀑布圖（waterfall plot）才是 SHAP 個案解釋
的標準畫法：從「一般申請人的平均違約機率」這個基準線出發，每個特徵把機率往上推多少，最
後停在「這筆申請案的預測機率」，一眼就看得出來龍去脈——這也是視覺化助理在對話裡本來就
建議的畫法（"透過 Waterfall Plot 視覺化該申請人的特徵貢獻度"）。

執行方式：pip install plotly kaleido && python visualize_shap.py
"""

import plotly.graph_objects as go

RANDOM_STATE = 42  # 固定 seed，任何隨機步驟都要用它，確保可重現

# 基準線：W12 EDA 實測的整體違約率 51.7%（真實統計數字，見 eda_report.md）。
# 兩個推力：PAY_0（主要因子）、signup_at 帳齡（次要因子）——示範用途數字，
# 依 W12 EDA 已知的 PAY_0／違約率關係編寫，不是真的 SHAP 輸出。
baseline = 0.517
pay0_push = 0.19
signup_push = 0.08
final = baseline + pay0_push + signup_push  # ≈ 0.787，對應「拒絕」的判定

fig = go.Figure(
    go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=["一般申請人\n平均違約機率", "PAY_0\n（還款狀態）", "signup_at\n（帳齡）", "這筆申請案\n最終預測機率"],
        y=[baseline, pay0_push, signup_push, final],
        text=[f"{baseline:.0%}", f"+{pay0_push:.0%}", f"+{signup_push:.0%}", f"{final:.0%}"],
        textposition="outside",
        connector={"line": {"color": "#c9b89a"}},
        increasing={"marker": {"color": "#b6552e"}},
        totals={"marker": {"color": "#5c2e12"}},
    )
)
fig.update_layout(
    title="申請案 APP-20260312-0417：從一般申請人到這筆案子的違約機率變化（SHAP 瀑布圖，示範用途）",
    yaxis=dict(title="預測違約機率", tickformat=".0%", range=[0, 1]),
    plot_bgcolor="#fffdf8",
    paper_bgcolor="#fffdf8",
    font_family="Noto Sans TC, sans-serif",
    width=700,
    height=320,
    margin=dict(l=60, r=40, t=60, b=60),
    showlegend=False,
)
# BILL_AMT1／AGE 不出現在圖上：模型從未接收這兩個輸入，沒有貢獻度可畫，
# 畫成 0 會誤導成「模型看過但決定忽略」——這點在圖的說明文字（xai_report.md）
# 裡另外交代，不是圖表本身要負責的事。

if __name__ == "__main__":
    fig.write_image("shap_chart.svg")
    print("已輸出 shap_chart.svg")
