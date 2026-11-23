from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="醫療儀表板｜基本資料", page_icon="🏥", layout="wide")
DATA_FILE = Path(__file__).resolve().parent / "data.csv"


@st.cache_data
def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["性別"] = df["Gender"].map({0: "男性", 1: "女性"}).fillna("未知")
    df["年齡區間"] = pd.cut(
        df["Age"], [0, 29, 44, 59, 74, 120],
        labels=["13-29歲", "30-44歲", "45-59歲", "60-74歲", "75-89歲"]
    ).astype(str)
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("找不到 `data.csv`，請確認檔案與 `app.py` 位於同一資料夾。")
    st.stop()

with st.sidebar:
    st.header("基本資料篩選")
    g = st.selectbox("性別", ["全部", "男性", "女性"], key="p1_g")
    adm = st.selectbox("入院方式", ["全部"] + sorted(df["Admission Type"].dropna().unique()), key="p1_adm")
    age_grp = st.selectbox("年齡區間", ["全部", "13-29歲", "30-44歲", "45-59歲", "60-74歲", "75-89歲"], key="p1_age")
    no_neg = st.checkbox("排除負帳務金額", key="p1_neg")
    if st.button("重設條件", use_container_width=True, key="p1_rst"):
        st.rerun()

f = df.copy()
if g != "全部":
    f = f[f["性別"] == g]
if adm != "全部":
    f = f[f["Admission Type"] == adm]
if age_grp != "全部":
    f = f[f["年齡區間"] == age_grp]
if no_neg:
    f = f[f["Billing Amount"] >= 0]

st.title("🏥 醫療紀錄可視化儀表板 — 第一頁：基本資料總覽")
st.caption(f"篩選：性別＝{g}｜入院方式＝{adm}｜年齡區間＝{age_grp}")

if f.empty:
    st.warning("無符合資料，請調整篩選條件。")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("篩選筆數", f"{len(f):,}", f"{len(f) / len(df) * 100:.1f}%")
k2.metric("平均年齡", f"{f['Age'].mean():.1f} 歲", f"中位數 {f['Age'].median():.0f} 歲")
k3.metric("平均帳務金額", f"{f['Billing Amount'].mean():,.2f}", f"中位數 {f['Billing Amount'].median():,.2f}")
k4.metric("負帳務筆數", f"{(f['Billing Amount'] < 0).sum():,}")

c1, c2 = st.columns(2)
with c1:
    g_df = f.groupby("性別", as_index=False).agg(筆數=("Name", "count"), 平均費用=("Billing Amount", "mean"))
    fig = px.bar(g_df, x="性別", y="筆數", color="性別", text="筆數", hover_data={"平均費用": ":.2f"}, title="性別分佈（0＝男性，1＝女性）")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig.update_layout(showlegend=False), use_container_width=True)

with c2:
    age_order = ["13-29歲", "30-44歲", "45-59歲", "60-74歲", "75-89歲"]
    a_df = f["年齡區間"].value_counts().reindex(age_order, fill_value=0).reset_index().rename(columns={"count": "筆數"})
    fig = px.bar(a_df, x="年齡區間", y="筆數", text="筆數", title="年齡區間分佈")
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
adm_df = f.groupby("Admission Type", as_index=False).agg(筆數=("Name", "count"), 平均費用=("Billing Amount", "mean"))
with c3:
    st.plotly_chart(px.pie(adm_df, names="Admission Type", values="筆數", hole=0.35, title="入院方式佔比"), use_container_width=True)
with c4:
    fig = px.bar(adm_df.sort_values("平均費用", ascending=False), x="Admission Type", y="平均費用", color="Admission Type", text="平均費用", hover_data={"筆數": ":,"}, title="各入院方式平均帳務金額")
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig.update_layout(showlegend=False), use_container_width=True)

st.subheader("基本資料明細（前 5 筆）")
st.dataframe(f[["Name", "Age", "性別", "年齡區間", "Admission Type", "Medical Condition", "Medication", "Billing Amount"]].head(5), use_container_width=True, hide_index=True)

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# 原本（往上一層找，會找不到）：
# DATA_FILE = Path(__file__).resolve().parent.parent / "data.csv"

# 改成（與第二頁檔案同資料夾）：
DATA_FILE = Path(__file__).resolve().parent / "data.csv"


@st.cache_data
def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["性別"] = df["Gender"].map({0: "男性", 1: "女性"}).fillna("未知")
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error("找不到 `data.csv`，請確認資料檔位於專案資料夾內。")
    st.stop()

with st.sidebar:
    st.header("疾病・用藥・費用篩選")
    cond = st.selectbox("疾病", ["全部"] + sorted(df["Medical Condition"].dropna().unique()), key="p2_cond")
    med = st.selectbox("用藥", ["全部"] + sorted(df["Medication"].dropna().unique()), key="p2_med")
    g = st.selectbox("性別", ["全部", "男性", "女性"], key="p2_g")
    adm = st.selectbox("入院方式", ["全部"] + sorted(df["Admission Type"].dropna().unique()), key="p2_adm")
    no_neg = st.checkbox("排除負帳務金額", key="p2_neg")

f = df.copy()
if cond != "全部":
    f = f[f["Medical Condition"] == cond]
if med != "全部":
    f = f[f["Medication"] == med]
if g != "全部":
    f = f[f["性別"] == g]
if adm != "全部":
    f = f[f["Admission Type"] == adm]
if no_neg:
    f = f[f["Billing Amount"] >= 0]

st.title("💊 醫療紀錄可視化儀表板 — 第二頁：疾病、用藥、費用")
st.caption(f"篩選：疾病＝{cond}｜用藥＝{med}｜性別＝{g}｜入院方式＝{adm}")

if f.empty:
    st.warning("無符合資料，請調整篩選條件。")
    st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("符合筆數", f"{len(f):,}")
m2.metric("平均帳務金額", f"{f['Billing Amount'].mean():,.2f}")
m3.metric("中位數帳務金額", f"{f['Billing Amount'].median():,.2f}")
m4.metric("平均年齡", f"{f['Age'].mean():.1f} 歲")

c1, c2 = st.columns(2)
with c1:
    c_df = f.groupby("Medical Condition", as_index=False).agg(筆數=("Billing Amount", "count"), 平均費用=("Billing Amount", "mean"), 中位數費用=("Billing Amount", "median"), 平均年齡=("Age", "mean")).sort_values("平均費用", ascending=False)
    fig = px.bar(c_df, x="Medical Condition", y="平均費用", color="Medical Condition", text="平均費用", hover_data={"筆數": ":,", "中位數費用": ":,.2f", "平均年齡": ":.1f"}, title="各疾病平均帳務金額")
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig.update_layout(showlegend=False), use_container_width=True)

with c2:
    piv = f.pivot_table(index="Medical Condition", columns="Medication", values="Billing Amount", aggfunc="mean")
    st.plotly_chart(px.imshow(piv, text_auto=",.0f", aspect="auto", color_continuous_scale="YlGnBu", title="疾病 × 用藥 平均帳務金額熱圖"), use_container_width=True)

c3, c4 = st.columns(2)
combo_df = f.groupby(["Medical Condition", "Medication"], as_index=False).agg(筆數=("Name", "count"), 平均年齡=("Age", "mean"), 平均費用=("Billing Amount", "mean"), 中位數費用=("Billing Amount", "median")).sort_values("平均費用", ascending=False)

with c3:
    st.plotly_chart(px.bar(combo_df, x="Medical Condition", y="筆數", color="Medication", barmode="stack", hover_data={"平均費用": ":,.2f"}, title="各疾病用藥筆數分佈"), use_container_width=True)

with c4:
    tb = pd.concat([combo_df.head(5), combo_df.tail(5)], ignore_index=True)
    tb["組合"] = tb["Medical Condition"] + " + " + tb["Medication"]
    fig = px.bar(tb.sort_values("平均費用"), x="平均費用", y="組合", orientation="h", text="平均費用", hover_data={"筆數": ":,", "平均年齡": ":.1f", "中位數費用": ":,.2f"}, title="平均費用最高 5 組 vs. 最低 5 組")
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("疾病 × 用藥 交叉統計明細")
st.dataframe(
    combo_df.style.format({"筆數": "{:,}", "平均年齡": "{:.2f}", "平均費用": "{:,.2f}", "中位數費用": "{:,.2f}"}),
    use_container_width=True,
    hide_index=True,
)