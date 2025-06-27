import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Penjualan", layout="wide")
st.markdown(
    "<h1 style='text-align: left; color: white;'>📊 Dashboard Penjualan Toko Elektronik</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr style='border: 0.3px solid #ffffff;'>", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("toko.csv")
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["Harga"] = df["Harga"].str.replace(".", "").str.replace(",", "").astype(float)
    df["Total Income"] = df["Harga"] * df["Billing Item"]
    return df

df = load_data()

# Tentukan rentang tanggal dari data
min_date = df["Tanggal"].min().date()
max_date = df["Tanggal"].max().date()

# Default: 3 hari terakhir
default_start = (max_date - pd.Timedelta(days=2)) if (max_date - pd.Timedelta(days=2)) >= min_date else min_date
default_end = max_date

# Sidebar
st.sidebar.header("Filter")

# Ambil input tanggal
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal:",
    value=[default_start, default_end],
    min_value=min_date,
    max_value=max_date
)

# Validasi input
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    st.sidebar.error("❗Silakan pilih *rentang tanggal* (dua tanggal).")
    st.stop()


# Filter Jenis Kelamin
gender = st.sidebar.multiselect("Pilih Jenis Kelamin:", df["Jenis Kelamin"].unique())

# Filter Nama Toko
store = st.sidebar.multiselect("Pilih Nama Toko:", df["Nama Toko"].unique())

# Terapkan filter
filtered_df = df.copy()
filtered_df = filtered_df[(filtered_df["Tanggal"].dt.date >= start_date) & (filtered_df["Tanggal"].dt.date <= end_date)]

if gender:
    filtered_df = filtered_df[filtered_df["Jenis Kelamin"].isin(gender)]

if store:
    filtered_df = filtered_df[filtered_df["Nama Toko"].isin(store)]

# Cek jika data kosong
if filtered_df.empty:
    st.warning("⚠️ Tidak ada data yang tersedia untuk filter yang dipilih. Silakan ubah rentang tanggal atau pilihan lainnya.")
    st.stop()


# Metrik
total_penjualan = filtered_df["Billing Item"].sum()
total_income = filtered_df["Total Income"].sum()

# Hitung rata-rata rating dan konversi ke bintang
if filtered_df["Rating"].notna().any():
    rata_rata_rating = round(filtered_df["Rating"].mean(), 1)
    full_stars = int(round(rata_rata_rating))
    star_rating = "⭐" * full_stars
else:
    rata_rata_rating = 0
    star_rating = "⭐"

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <p>Total Penjualan Item</p>
            <h1>{int(total_penjualan)}</h1>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <p>Rata-rata Rating</p>
            <h1>{rata_rata_rating} {star_rating}</h1>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <p>Total Income</p>
            <h1>Rp {int(total_income):,}</h1>
        </div>
    """, unsafe_allow_html=True)
st.markdown("""---""")

# Visualisasi 1: Trend Harian
trend_chart = filtered_df.groupby("Tanggal")["Total Income"].sum().reset_index()
fig1 = px.line(trend_chart, x="Tanggal", y="Total Income",
               title="Trend Total Penjualan Harian",
               labels={"Total Income": "Total Penjualan (Rp)"})
fig1.update_layout(yaxis_tickformat=',')
st.plotly_chart(fig1, use_container_width=True)

# Visualisasi 2: Total penjualan 5 toko teratas
top_stores = filtered_df.groupby("Nama Toko")["Total Income"].sum().nlargest(5).reset_index()
fig2 = px.bar(top_stores, x="Nama Toko", y="Total Income",
              title="Total Penjualan di 5 Cabang Teratas",
              labels={"Total Income": "Total Penjualan (Rp)"},
              text_auto=True)
fig2.update_layout(yaxis_tickformat=',')

# Visualisasi 3: Brand Paling Diminati
fav_brands = filtered_df["Brand Name"].value_counts().nlargest(5).reset_index()
fav_brands.columns = ["Brand", "Jumlah"]
colors = ['#66B2FF', '#3399FF', '#0066CC', '#003399', '#001f4d']

fig3 = px.pie(
    fav_brands,
    names="Brand",
    values="Jumlah",
    title="Brand Paling Diminati (Top 5)",
    color_discrete_sequence=colors
)
fig3.update_traces(
    textposition='inside',
    textinfo='percent+label',
    pull=[0.02, 0.02, 0.03, 0.03, 0.04],
    marker=dict(line=dict(color='#000000', width=1))
)
fig3.update_layout(
    showlegend=True,
    height=500,
    width=600,
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend=dict(font=dict(size=20))
)

col_v2, col_v3 = st.columns(2)
with col_v2:
    st.plotly_chart(fig2, use_container_width=True)
with col_v3:
    st.plotly_chart(fig3, use_container_width=True)

# Visualisasi 4: Total Penjualan per Brand
brand_sales = filtered_df.groupby("Brand Name")["Total Income"].sum().sort_values(ascending=True).reset_index()
fig4 = px.bar(
    brand_sales,
    x="Total Income",
    y="Brand Name",
    orientation='h',
    title="Total Penjualan per Brand",
    labels={"Total Income": "Total Penjualan (Rp)", "Brand Name": "Brand"},
    text_auto=True
)
fig4.update_layout(
    xaxis_tickformat=',',
    height=500,
    width=800,
    font=dict(size=20),
    title_font_size=24,
    xaxis_title_font=dict(size=18),
    yaxis_title_font=dict(size=18),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14),
    margin=dict(l=120, r=20, t=60, b=40)
)
st.plotly_chart(fig4, use_container_width=True)

# Visualisasi 5: Total Penjualan Top 6 Group Name
group_sales = filtered_df.groupby("Group Name")["Total Income"].sum().sort_values(ascending=False).reset_index()
top_group_sales = group_sales.head(6).sort_values(ascending=True, by="Total Income")
fig5 = px.bar(
    top_group_sales,
    x="Total Income",
    y="Group Name",
    orientation='h',
    title="Total Penjualan Tertinggi Berdasarkan Group Name (Top 6)",
    labels={"Total Income": "Total Penjualan (Rp)", "Group Name": "Kategori Produk"},
    text_auto=True
)
fig5.update_layout(
    xaxis_tickformat=',',
    height=600,
    font=dict(size=14),
    title_font=dict(size=22),
    xaxis_title_font=dict(size=16),
    yaxis_title_font=dict(size=16),
    xaxis_tickfont=dict(size=14),
    yaxis_tickfont=dict(size=14),
    margin=dict(l=120, r=20, t=60, b=40)
)
fig5.update_traces(textfont_size=14)
st.plotly_chart(fig5, use_container_width=True)
