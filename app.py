from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="Personalized Insurance Recommendation",
    page_icon="🛡️",
    layout="wide",
)

# -------- Light, clean visual style --------
st.markdown("""
<style>
    :root {
        --bg: #F5F7FB;
        --panel: #FFFFFF;
        --panel-soft: #F8FAFD;
        --text: #1F2937;
        --muted: #667085;
        --line: #E5EAF1;
        --accent: #3B6EA8;
        --accent-soft: #EAF2FB;
        --shadow: 0 8px 24px rgba(31, 41, 55, 0.06);
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: var(--bg) !important;
        color: var(--text) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(245, 247, 251, 0.92) !important;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4, p, label, div {
        color: var(--text);
    }

    .hero {
        background: linear-gradient(135deg, #FFFFFF 0%, #F2F6FC 100%);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.35rem;
        box-shadow: var(--shadow);
    }

    .hero h1 {
        margin: 0 0 0.45rem 0;
        font-size: 2.05rem;
        line-height: 1.25;
        color: #17324F !important;
    }

    .hero p {
        margin: 0;
        color: var(--muted) !important;
        font-size: 1rem;
        line-height: 1.7;
    }

    .section-title {
        font-size: 1.22rem;
        font-weight: 760;
        color: #17324F;
        margin: 0.25rem 0 0.7rem 0;
    }

    .result-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.2rem 1.25rem;
        min-height: 158px;
        box-shadow: var(--shadow);
    }

    .result-card.primary {
        border: 1.5px solid #BFD3E8;
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
    }

    .kicker {
        font-size: .76rem;
        color: var(--muted) !important;
        text-transform: uppercase;
        letter-spacing: .075em;
        font-weight: 700;
        margin-bottom: .35rem;
    }

    .plan {
        font-size: 1.72rem;
        color: #17324F !important;
        font-weight: 800;
        margin: .1rem 0 .55rem 0;
    }

    .card-text {
        color: #475467 !important;
        line-height: 1.65;
        font-size: .96rem;
    }

    .small-note {
        font-size: .9rem;
        color: var(--muted) !important;
        line-height: 1.6;
    }

    .guide-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1rem 1.05rem;
        height: 100%;
    }

    .guide-title {
        font-weight: 750;
        color: #17324F !important;
        margin-bottom: .35rem;
    }

    .guide-card p {
        color: #5B6575 !important;
        font-size: .92rem;
        line-height: 1.62;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        padding: .8rem 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 14px rgba(31, 41, 55, 0.04);
    }

    div[data-testid="stMetricLabel"] p {
        color: var(--muted) !important;
    }

    div[data-testid="stMetricValue"] {
        color: #17324F !important;
    }

    div[data-testid="stNumberInput"],
    div[data-testid="stRadio"],
    div[data-testid="stCheckbox"] {
        color: var(--text) !important;
    }

    div[data-baseweb="input"] > div {
        background-color: #FFFFFF !important;
        border-color: #D9E1EA !important;
    }

    div[data-baseweb="radio"] label,
    div[data-testid="stCheckbox"] label {
        color: var(--text) !important;
    }

    details {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
    }

    hr {
        border-color: var(--line) !important;
    }

    .footer-note {
        color: #7A8493 !important;
        font-size: .82rem;
        margin-top: 1rem;
    }

    @media (max-width: 800px) {
        .hero {
            padding: 1.35rem 1.25rem;
        }
        .hero h1 {
            font-size: 1.65rem;
        }
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
        (rec_df["age_group"] == age_grp)
        & (rec_df["sex"] == sex)
        & (rec_df["risk"] == risk)
    ]
    if row.empty:
        return None
    return row.iloc[0]


def pretty_plan(plan: str) -> str:
    labels = {
        "Bronze": "🥉 Bronze",
        "Silver": "🥈 Silver",
        "Gold": "🥇 Gold",
        "No Insurance": "— No Insurance",
    }
    return labels.get(plan, plan)


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
    st.markdown('<div class="section-title">1. Your profile</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="section-title">2. Chronic conditions</div>', unsafe_allow_html=True)
    st.caption("勾選目前患有的疾病；系統會依專題中設定的權重計算 disease-risk score。")

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
    st.caption("Selected: " + ("、".join(selected) if selected else "無"))


with right:
    st.markdown('<div class="section-title">3. Simulation recommendation</div>', unsafe_allow_html=True)

    if result is None:
        st.error("找不到對應的 cohort，請檢查推薦表。")
    else:
        primary = result["forced_mean"]

        st.markdown(
            f"""
            <div class="result-card primary">
                <div class="kicker">Primary recommendation · Forced insurance (Mean)</div>
                <div class="plan">{pretty_plan(primary)}</div>
                <div class="card-text">
                    若使用者確定要投保，這是模擬在 Bronze / Silver / Gold
                    之間，以<strong>平均年度總成本</strong>為準的推薦結果。
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
                        允許 No Insurance，只比較平均總成本，不另外加入極端風險考量。
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
                        聚焦醫療支出分布較高尾端的情況，用來觀察高額醫療支出情境下的方案差異。
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        st.markdown('<div class="section-title">How should I read these three results?</div>', unsafe_allow_html=True)

        g1, g2, g3 = st.columns(3, gap="medium")

        with g1:
            st.markdown("""
            <div class="guide-card">
                <div class="guide-title">Primary recommendation</div>
                <p>
                    如果你已經確定會投保，而且主要想比較 Bronze、Silver、Gold
                    三種方案的<strong>平均年度總成本</strong>，可以優先看這個結果。
                </p>
            </div>
            """, unsafe_allow_html=True)

        with g2:
            st.markdown("""
            <div class="guide-card">
                <div class="guide-title">Cost-only</div>
                <p>
                    如果你願意把<strong>不投保</strong>也納入選項，而且目前只想從
                    平均總成本角度比較，可以參考 Cost-only 的結果。
                </p>
            </div>
            """, unsafe_allow_html=True)

        with g3:
            st.markdown("""
            <div class="guide-card">
                <div class="guide-title">P95 tail-risk</div>
                <p>
                    如果你比起平均成本，更在意少數但非常高額的醫療支出情況，
                    可以參考 P95 tail-risk 的推薦結果。
                </p>
            </div>
            """, unsafe_allow_html=True)

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
The website maps the user's profile to one of the 18 cohorts and retrieves the already-computed final recommendation.
""")

st.markdown("---")
st.markdown(
    '<div class="footer-note">Academic demonstration only. This tool reproduces the project’s simulation-based decision matrix and is not medical, financial, or insurance advice.</div>',
    unsafe_allow_html=True,
)
