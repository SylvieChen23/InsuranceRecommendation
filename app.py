from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Personalized Insurance Recommendation",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>
    .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.6rem 1.8rem;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 20px;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin: 0 0 .35rem 0; font-size: 2.05rem;}
    .hero p {margin: 0; opacity: .78; font-size: 1rem;}
    .result-card {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        padding: 1.15rem 1.2rem;
        min-height: 150px;
    }
    .result-card.primary {
        border-width: 2px;
    }
    .kicker {
        font-size: .78rem;
        opacity: .65;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: .3rem;
    }
    .plan {
        font-size: 1.7rem;
        font-weight: 750;
        margin: .15rem 0 .5rem 0;
    }
    .small-note {
        font-size: .88rem;
        opacity: .72;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,.18);
        padding: .8rem 1rem;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    rec = pd.read_csv(BASE_DIR / "recommendation_table.csv")
    disease = pd.read_csv(BASE_DIR / "disease_weights.csv")
    return rec, disease

rec_df, disease_df = load_data()

def age_group(age: int) -> str:
    if age <= 15:
        return "0-15"
    elif age <= 64:
        return "16-64"
    return "65+"

def risk_group(score: int) -> str:
    if score == 0:
        return "Low"
    elif score <= 2:
        return "Middle"
    return "High"

def lookup(age_grp: str, sex: str, risk: str):
    row = rec_df[
        (rec_df["age_group"] == age_grp) &
        (rec_df["sex"] == sex) &
        (rec_df["risk"] == risk)
    ]
    if row.empty:
        return None
    return row.iloc[0]

def pretty_plan(plan: str) -> str:
    icons = {
        "Bronze": "🥉 Bronze",
        "Silver": "🥈 Silver",
        "Gold": "🥇 Gold",
        "No Insurance": "— No Insurance",
    }
    return icons.get(plan, plan)

st.markdown("""
<div class="hero">
    <h1>Personalized Medical Insurance Recommendation</h1>
    <p>
        Monte Carlo simulation–based decision support using age, sex, and six chronic-disease indicators.
        Select a profile to view the recommendation generated from the project's final 18-cohort decision matrix.
    </p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([0.92, 1.35], gap="large")

with left:
    st.subheader("1. Your profile")

    age = st.number_input(
        "Age 年齡",
        min_value=0,
        max_value=100,
        value=25,
        step=1,
    )

    sex_label = st.radio(
        "Sex 性別",
        ["Female 女性", "Male 男性"],
        horizontal=True,
    )
    sex = "Female" if sex_label.startswith("Female") else "Male"

    st.markdown("#### 2. Chronic conditions")
    st.caption("勾選目前患有的疾病；系統會依專題中設定的 actuarial weights 計算 disease-risk score。")

    selected = []
    score = 0

    for _, d in disease_df.iterrows():
        label = f'{d["disease_zh"]}  {d["disease_en"]}  ·  +{int(d["weight"])}'
        checked = st.checkbox(label, key=d["disease_en"])
        if checked:
            selected.append(d["disease_zh"])
            score += int(d["weight"])

    ag = age_group(int(age))
    risk = risk_group(score)
    result = lookup(ag, sex, risk)

    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("Disease-risk score", score)
    c2.metric("Risk group", risk)

    st.caption(f"Matched cohort: {ag} · {sex} · {risk}")
    if selected:
        st.caption("Selected: " + "、".join(selected))
    else:
        st.caption("Selected: 無")

with right:
    st.subheader("3. Simulation recommendation")

    if result is None:
        st.error("找不到對應的 cohort，請檢查推薦表。")
    else:
        primary = result["forced_mean"]

        st.markdown(
            f"""
            <div class="result-card primary">
                <div class="kicker">Primary recommendation · Forced insurance (Mean)</div>
                <div class="plan">{pretty_plan(primary)}</div>
                <div>
                    若使用者確定要投保，這是你們模擬中在 Bronze / Silver / Gold
                    之間，以<strong>平均年度總成本最低</strong>為準的推薦結果。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="kicker">Cost-only</div>
                    <div class="plan">{pretty_plan(result["cost_only"])}</div>
                    <div class="small-note">
                        允許 No Insurance；只比較平均總成本，不另外強制風險保障。
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="kicker">P95 tail-risk</div>
                    <div class="plan">{pretty_plan(result["p95"])}</div>
                    <div class="small-note">
                        只比較保險方案，重視第 95 百分位的極端醫療支出風險。
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.info(
            f"系統先將年齡 {int(age)} 歲歸入 {ag}、性別為 {sex}，"
            f"再由六種疾病加權得到 {score} 分，因此屬於 {risk} disease-risk group，"
            "最後查詢你們 Monte Carlo 模擬完成後的 cohort recommendation。"
        )

        with st.expander("How the model works / 模型怎麼產生這個答案"):
            st.markdown("""
**Step 1 — Risk stratification**  
Age (0–15 / 16–64 / 65+) × Sex (Female / Male) × Disease risk (Low / Middle / High) = **18 cohorts**.

**Step 2 — Disease-risk score**  
High cholesterol +1, Hypertension +1, Asthma +1, Diabetes +2, Cancer +3, Coronary heart disease +3.  
Score 0 = Low; 1–2 = Middle; ≥3 = High.

**Step 3 — Medical-cost simulation**  
Each cohort uses a two-part medical expenditure model to handle zero expenditures and the right-skewed positive-cost distribution.

**Step 4 — Policy comparison**  
The project compares Bronze, Silver, Gold, and a No-Insurance baseline using annual total cost:

`Total Cost = Premium + Patient Payment`

**Step 5 — Final decision**  
The website does **not** rerun the simulation. It maps the user's profile to one of the 18 cohorts and retrieves the already-computed final recommendation. This makes the demo immediate and reproducible.
""")

st.markdown("---")
st.caption(
    "Academic demonstration only. This tool reproduces the project's simulation-based decision matrix "
    "and is not medical, financial, or insurance advice."
)
