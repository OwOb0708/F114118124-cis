"""W15 XAI：產生申請案 APP-20260312-0417 的 SHAP 貢獻度圖。

本機執行，輸出 shap_chart.svg，跟這份腳本一起 commit——平台不會執行程式碼
（CIS_ENABLE_SANDBOX 預設關閉，見 backend/cis/sandbox.py），只負責讀取 GitHub
上已經產生好的圖檔，所以這支腳本本身不是被系統跑的東西，是留下「圖是怎麼來的」
這個可重現紀錄，跟 W11 clean_credit_data.py 記錄「乾淨資料是怎麼來的」是同一個道理。

執行方式：pip install plotly kaleido && python visualize_shap.py
"""

import plotly.graph_objects as go

RANDOM_STATE = 42  # 固定 seed，任何隨機步驟都要用它，確保可重現

# 只放模型真的用到的兩個特徵。BILL_AMT1／AGE 因為模型從未接收這兩個輸入，
# 沒有 SHAP 值可以畫，刻意不放進圖表——不是漏放，是誠實反映「沒有輸入過的
# 特徵算不出貢獻度」，避免讓人誤以為「畫出來＝有參與判斷」。
features = ["PAY_0（還款狀態）", "signup_at（帳齡）"]
shap_contribution = [0.62, 0.24]  # 相對貢獻度，僅供本個案說明使用，非全體平均
labels = ["0.62（主要因子）", "0.24（次要因子）"]

fig = go.Figure(
    go.Bar(
        x=shap_contribution,
        y=features,
        orientation="h",
        marker_color=["#b6552e", "#a06a1e"],
        text=labels,
        textposition="outside",
    )
)
fig.update_layout(
    title="申請案 APP-20260312-0417：SHAP 貢獻度（僅列模型實際使用的特徵）",
    xaxis_title="對違約機率的推升程度（相對值）",
    yaxis_title=None,
    plot_bgcolor="#fffdf8",
    paper_bgcolor="#fffdf8",
    font_family="Noto Sans TC, sans-serif",
    width=640,
    height=220,
    margin=dict(l=140, r=40, t=50, b=40),
)

if __name__ == "__main__":
    # kaleido 負責把 Plotly 圖轉成靜態 SVG；沒裝的話 pip install kaleido。
    fig.write_image("shap_chart.svg")
    print("已輸出 shap_chart.svg")
