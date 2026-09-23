# Personalized Medical Insurance Recommendation Demo

這個版本是給專題／推甄展示用的 Streamlit 網站。

## 網站做什麼

使用者輸入：

1. 年齡
2. 性別
3. 六種疾病是否患有

疾病依專題設定計分：

- High cholesterol 高膽固醇：1
- Hypertension 高血壓：1
- Asthma 氣喘：1
- Diabetes 糖尿病：2
- Cancer 癌症：3
- Coronary heart disease 冠心病：3

風險分類：

- 0 分 = Low
- 1–2 分 = Middle
- 3 分以上 = High

接著把使用者歸入：

Age group × Sex × Disease risk = 18 cohorts

網站直接查詢專題最後的 recommendation matrix，顯示：

- Cost-only
- Forced-insurance (Mean)
- Forced-insurance (P95 Tail Risk)

其中畫面上的 **Primary recommendation** 使用 Forced-insurance (Mean)，因為它回答的是：
「如果使用者確定要買保險，在 Bronze / Silver / Gold 中，哪一個平均總成本最低？」

## 重要：這版刻意不在網頁現場重跑 Monte Carlo

這是展示網站比較穩的做法。

教授按下選項後應該立即看到結果，不應等待 100 replications × 1,000 individuals。
而且網站顯示的是你們已經在專題中跑完的正式結果，不會因為每次 random seed 不同而跳動。

未來如果要擴充，可把完整 simulation 封裝成 Python function，再增加：
- "Run simulation" 按鈕
- mean total cost
- P95
- confidence interval
- 各方案成本圖

## Mac 本機執行

在 Terminal 進入這個資料夾：

```bash
cd insurance_demo_site
```

建立虛擬環境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安裝套件：

```bash
pip install -r requirements.txt
```

啟動網站：

```bash
streamlit run app.py
```

Terminal 會顯示 Local URL，通常瀏覽器會自動開啟。

## 部署

最簡單的方式是把以下四個檔案放到 GitHub repository：

- app.py
- recommendation_table.csv
- disease_weights.csv
- requirements.txt

再用支援 Streamlit 的雲端平台部署 `app.py`。

## 資料一致性提醒

目前簡報與另一份 policy parameter 文字資料中的 premium / deductible 數值並不完全一致。
因此這個 demo **只使用 PPT 最終 decision recommendation matrix 做推薦**，
暫時不在首頁顯示精確 premium / deductible 金額。

如果之後要把「預估平均成本是多少美元」一起放到網站，
請先確認哪一版 policy parameters 才是報告最終版本，再把同一套數字接進網站。
