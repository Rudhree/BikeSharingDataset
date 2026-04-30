import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="🚴 Bike Sharing Dashboard",
    layout="wide"
)

sns.set_style("whitegrid")

# ======================
# LOAD DATA
# ======================
day_df = pd.read_csv("day.csv")
hour_df = pd.read_csv("hour.csv")

# ======================
# MAPPING
# ======================
weather_map = {
    1: "Cerah",
    2: "Berawan",
    3: "Hujan Ringan",
    4: "Hujan Lebat"
}

year_map = {
    0: "2011",
    1: "2012"
}

day_df["weathersit"] = day_df["weathersit"].map(weather_map)
hour_df["weathersit"] = hour_df["weathersit"].map(weather_map)

day_df["year"] = day_df["yr"].map(year_map)
hour_df["year"] = hour_df["yr"].map(year_map)

hour_df["day_type"] = hour_df["workingday"].map({
    1: "Working Day",
    0: "Weekend"
})

# ======================
# CLUSTERING (MANUAL)
# ======================
day_df["demand_level"] = pd.cut(
    day_df["cnt"],
    bins=[0, 2000, 4000, 6000, 9000],
    labels=["Low", "Medium", "High", "Very High"]
)

# ======================
# SIDEBAR
# ======================
st.sidebar.markdown("## 🎛️ Dashboard Control Panel")

# Filter Hari
day_filter = st.sidebar.selectbox(
    "📅 Jenis Hari",
    ["All", "Working Day", "Weekend"]
)

# Filter Cuaca
weather_filter = st.sidebar.multiselect(
    "🌦️ Kondisi Cuaca",
    options=day_df["weathersit"].unique(),
    default=day_df["weathersit"].unique()
)

# 🔥 Filter Tahun (BARU)
year_filter = st.sidebar.multiselect(
    "📆 Tahun",
    options=day_df["year"].unique(),
    default=day_df["year"].unique()
)

#st.sidebar.markdown("---")
#st.sidebar.info("""
#Dashboard ini menampilkan:
#- Pola penyewaan sepeda
#- Perbandingan waktu
#- Pengaruh cuaca
#- Clustering demand
#""")

# ======================
# FILTER DATA
# ======================
hour_filtered = hour_df.copy()
day_filtered = day_df.copy()

if day_filter != "All":
    hour_filtered = hour_filtered[hour_filtered["day_type"] == day_filter]

day_filtered = day_filtered[day_filtered["weathersit"].isin(weather_filter)]

# 🔥 FILTER TAHUN
hour_filtered = hour_filtered[hour_filtered["year"].isin(year_filter)]
day_filtered = day_filtered[day_filtered["year"].isin(year_filter)]

# INFO JUMLAH DATA
#st.sidebar.success(f"📊 Data terpilih: {len(day_filtered)} baris")

# ======================
# HEADER
# ======================
st.title("🚴 Bike Sharing Analysis Dashboard")
st.markdown("### 📊 Analisis Penyewaan Sepeda Berbasis Data")

# ======================
# KPI STYLE (CENTER) - FIXED
# ======================
st.markdown("""
<style>
.kpi-card {
    background: linear-gradient(135deg, #f8f9fa, #eef1f5);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    color: #212529; /* 🔥 semua teks jadi gelap */
}
.kpi-title {
    font-size: 14px;
    color: #6c757d; /* abu-abu biar soft */
}
.kpi-value {
    font-size: 30px;
    font-weight: bold;
    color: #212529; /* 🔥 ini fix utama */
}
</style>
""", unsafe_allow_html=True)

# KPI VALUES
total_data = len(day_filtered)
avg_demand = int(day_filtered["cnt"].mean())
max_demand = int(day_filtered["cnt"].max())
peak_hour = hour_filtered.groupby("hr")["cnt"].mean().idxmax()

# KPI LAYOUT
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📦 Total Data</div>
        <div class="kpi-value">{total_data:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📈 Avg Demand</div>
        <div class="kpi-value">{avg_demand:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🔥 Max Demand</div>
        <div class="kpi-value">{max_demand:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⏰ Peak Hour</div>
        <div class="kpi-value">{peak_hour}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ======================
# TABS
# ======================
tab1, tab2, tab3 = st.tabs([
    "⏰ Time Analysis",
    "🌦️ Weather Insight",
    "🧠 Demand Clustering"
])

# ======================
# TAB 1
# ======================
with tab1:

    st.subheader("📊 Pola Penyewaan per Jam")

    hour_avg = hour_filtered.groupby("hr")["cnt"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10,5))
    sns.lineplot(data=hour_avg, x="hr", y="cnt", marker="o", ax=ax)

    peak = hour_avg.loc[hour_avg["cnt"].idxmax()]
    ax.scatter(peak["hr"], peak["cnt"], color="red", s=120)

    ax.set_title("Peak Hour Detection 🚀")

    st.pyplot(fig)
    st.success(f"Peak terjadi pada jam {int(peak['hr'])}")

    st.subheader("📊 Working Day vs Weekend")

    compare = hour_filtered.groupby(["hr","day_type"])["cnt"].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(10,5))
    sns.lineplot(data=compare, x="hr", y="cnt", hue="day_type", marker="o", ax=ax2)

    st.pyplot(fig2)

# ======================
# TAB 2
# ======================
with tab2:

    st.subheader("🌦️ Pengaruh Cuaca")

    weather_avg = day_filtered.groupby("weathersit")["cnt"].mean().reset_index()

    fig3, ax3 = plt.subplots(figsize=(8,5))
    sns.barplot(data=weather_avg, x="weathersit", y="cnt", ax=ax3)

    st.pyplot(fig3)
    st.info("Cuaca cerah memiliki demand tertinggi")

    st.subheader("📉 Perubahan 2011 vs 2012")

    weather_year = day_filtered.groupby(["weathersit","yr"])["cnt"].mean().unstack()

    weather_year["Change (%)"] = (
        (weather_year[0] - weather_year[1]) / weather_year[0]
    ) * 100

    st.dataframe(weather_year)

# ======================
# TAB 3
# ======================
with tab3:

    st.subheader("🧠 Demand Segmentation")

    order = ["Low","Medium","High","Very High"]

    cluster = day_filtered.groupby("demand_level")["cnt"].agg(["count","mean","max"])
    cluster = cluster.reindex(order)

    st.dataframe(cluster)

    st.markdown("""
    ###  Insight:
    - Demand tertinggi berada pada kategori High & Very High
    - Low demand relatif sedikit
    - Cuaca dan waktu sangat mempengaruhi penyewaan
    """)

# ======================
# FOOTER
# ======================
st.markdown("---")
st.caption("Bike Sharing Dashboard | BFDA Project | Rudh Renata")
