import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import fungsi dari config.py
from config import *

# Set konfigurasi halaman dashboard
st.set_page_config("Dashboard Polusi", page_icon="🌍", layout="wide")

# Judul Dashboard
st.title("Dashboard Polusi & Kualitas Hidup")
st.markdown("---")

# ========== AMBIL DATA ==========
# Data Negara
result_negara = view_all_negara()
df_negara = pd.DataFrame(result_negara, columns=["id_negara", "nama_negara", "benua", "populasi"])

# Data Kota
result_kota = view_all_kota()
df_kota = pd.DataFrame(result_kota, columns=["id_kota", "nama_kota", "populasi", "nama_negara", "benua"])

# Data Polusi
result_polusi = view_all_polusi()
df_polusi = pd.DataFrame(result_polusi, columns=[
    "id_polusi", "nama_negara", "nama_kota", "tahun", 
    "indeks_kualitas_udara", "indeks_karbon", "indeks_ozon", "indeks_nitrogen_dioksida"
])

# Data Kualitas Hidup
result_kualitas_hidup = view_all_kualitas_hidup()
df_kualitas_hidup = pd.DataFrame(result_kualitas_hidup, columns=[
    "id_kualitas_hidup", "nama_negara", "tahun", "indeks_kualitas_hidup", 
    "indeks_keamanan", "indeks_kesehatan", "indeks_pendidikan", "indeks_biaya_hidup"
])

# Pastikan tipe data yang sesuai
if not df_polusi.empty:
    df_polusi['tahun'] = pd.to_numeric(df_polusi['tahun'], errors='coerce').astype('Int64')
    df_polusi['indeks_kualitas_udara'] = pd.to_numeric(df_polusi['indeks_kualitas_udara'], errors='coerce')
    df_polusi['indeks_karbon'] = pd.to_numeric(df_polusi['indeks_karbon'], errors='coerce')
    df_polusi['indeks_ozon'] = pd.to_numeric(df_polusi['indeks_ozon'], errors='coerce')
    df_polusi['indeks_nitrogen_dioksida'] = pd.to_numeric(df_polusi['indeks_nitrogen_dioksida'], errors='coerce')

if not df_kualitas_hidup.empty:
    df_kualitas_hidup['tahun'] = pd.to_numeric(df_kualitas_hidup['tahun'], errors='coerce').astype('Int64')
    df_kualitas_hidup['indeks_kualitas_hidup'] = pd.to_numeric(df_kualitas_hidup['indeks_kualitas_hidup'], errors='coerce')
    df_kualitas_hidup['indeks_keamanan'] = pd.to_numeric(df_kualitas_hidup['indeks_keamanan'], errors='coerce')
    df_kualitas_hidup['indeks_kesehatan'] = pd.to_numeric(df_kualitas_hidup['indeks_kesehatan'], errors='coerce')
    df_kualitas_hidup['indeks_pendidikan'] = pd.to_numeric(df_kualitas_hidup['indeks_pendidikan'], errors='coerce')
    df_kualitas_hidup['indeks_biaya_hidup'] = pd.to_numeric(df_kualitas_hidup['indeks_biaya_hidup'], errors='coerce')


# ========== FUNGSI UNTUK TABEL DATA POLUSI ==========
def tabel_polusi_dan_export():
    st.header("Data Polusi")
    
    if df_polusi.empty:
        st.warning("Tidak ada data polusi untuk ditampilkan.")
        return

    # Hitung statistik
    total_records = df_polusi.shape[0]
    avg_aqi = df_polusi['indeks_kualitas_udara'].mean()

    # Tampilkan metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Record", value=total_records)
    with col2:
        st.metric(label="Rata-rata Indeks Kualitas Udara", value=f"{avg_aqi:.1f}")
    with col3:
        unique_countries = df_polusi['nama_negara'].nunique()
        st.metric(label="Jumlah Negara", value=unique_countries)

    # Sidebar: Filter
    st.sidebar.header("Filter Data Polusi")

    # Filter Tahun
    min_year = int(df_polusi['tahun'].min()) if df_polusi['tahun'].notna().any() else 2018
    max_year = int(df_polusi['tahun'].max()) if df_polusi['tahun'].notna().any() else 2023
    
    if min_year >= max_year:
        yr = st.sidebar.number_input("Pilih Tahun", min_value=int(min_year), max_value=int(max_year), value=int(min_year), step=1)
        year_range = (int(yr), int(yr))
    else:
        year_range = st.sidebar.slider(
            "Pilih Rentang Tahun",
            min_value=int(min_year),
            max_value=int(max_year),
            value=(int(min_year), int(max_year))
        )

    # Filter Negara
    countries_list = sorted(df_polusi['nama_negara'].unique().tolist())
    selected_countries = st.sidebar.multiselect("Pilih Negara (kosong = semua)", options=countries_list)

    # Filter Indeks Kualitas Udara
    min_aqi = float(df_polusi['indeks_kualitas_udara'].min()) if df_polusi['indeks_kualitas_udara'].notna().any() else 0.0
    max_aqi = float(df_polusi['indeks_kualitas_udara'].max()) if df_polusi['indeks_kualitas_udara'].notna().any() else 100.0
    
    if min_aqi >= max_aqi:
        aqi = st.sidebar.number_input("Pilih Indeks Kualitas Udara", min_value=float(min_aqi), max_value=float(max_aqi), value=float(min_aqi), step=1.0)
        aqi_range = (float(aqi), float(aqi))
    else:
        aqi_range = st.sidebar.slider(
            "Pilih Rentang Indeks Kualitas Udara",
            min_value=float(min_aqi),
            max_value=float(max_aqi),
            value=(float(min_aqi), float(max_aqi))
        )

    # Terapkan filter
    filtered_df = df_polusi[
        df_polusi['tahun'].between(year_range[0], year_range[1]) &
        df_polusi['indeks_kualitas_udara'].between(aqi_range[0], aqi_range[1])
    ]

    if selected_countries:
        filtered_df = filtered_df[filtered_df['nama_negara'].isin(selected_countries)]

    # Tampilkan tabel
    st.markdown("### Tabel Data Polusi")
    showdata = st.multiselect(
        "Pilih Kolom yang Ditampilkan",
        options=filtered_df.columns.tolist(),
        default=["nama_negara", "nama_kota", "tahun", "indeks_kualitas_udara", "indeks_karbon", "indeks_ozon"]
    )

    st.dataframe(filtered_df[showdata], use_container_width=True)

    # Download CSV
    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df[showdata])
    st.download_button(
        label="Download Data Polusi sebagai CSV",
        data=csv,
        file_name='data_polusi.csv',
        mime='text/csv'
    )

    # Visualisasi
    st.markdown("### Visualisasi Data Polusi")
    
    # Chart 1: Top 10 Negara dengan Indeks Kualitas Udara Tertinggi
    avg_by_country = filtered_df.groupby('nama_negara')['indeks_kualitas_udara'].mean().sort_values(ascending=False).head(10)
    fig1 = px.bar(
        x=avg_by_country.values,
        y=avg_by_country.index,
        orientation='h',
        title='Negara dengan Rata-rata Indeks Kualitas Udara Tertinggi',
        labels={'x': 'Indeks Kualitas Udara', 'y': 'Negara'},
        color=avg_by_country.values,
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Tren Polusi per Tahun
    if not filtered_df.empty and len(filtered_df['tahun'].unique()) > 1:
        trend_df = filtered_df.groupby('tahun')[['indeks_kualitas_udara', 'indeks_karbon', 'indeks_ozon', 'indeks_nitrogen_dioksida']].mean().reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_df['tahun'], y=trend_df['indeks_kualitas_udara'], mode='lines+markers', name='Kualitas Udara'))
        fig2.add_trace(go.Scatter(x=trend_df['tahun'], y=trend_df['indeks_karbon'], mode='lines+markers', name='Karbon'))
        fig2.add_trace(go.Scatter(x=trend_df['tahun'], y=trend_df['indeks_ozon'], mode='lines+markers', name='Ozon'))
        fig2.add_trace(go.Scatter(x=trend_df['tahun'], y=trend_df['indeks_nitrogen_dioksida'], mode='lines+markers', name='Nitrogen Dioksida'))
        fig2.update_layout(title='Tren Indeks Polusi per Tahun', xaxis_title='Tahun', yaxis_title='Indeks')
        st.plotly_chart(fig2, use_container_width=True)


# ========== FUNGSI UNTUK TABEL KUALITAS HIDUP ==========
def tabel_kualitas_hidup_dan_export():
    st.header("Data Kualitas Hidup")
    
    if df_kualitas_hidup.empty:
        st.warning("Tidak ada data kualitas hidup untuk ditampilkan.")
        return

    # Hitung statistik
    total_records = df_kualitas_hidup.shape[0]
    avg_life_quality = df_kualitas_hidup['indeks_kualitas_hidup'].mean()

    # Tampilkan metrik
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Record", value=total_records)
    with col2:
        st.metric(label="Rata-rata Indeks Kualitas Hidup", value=f"{avg_life_quality:.1f}")
    with col3:
        unique_countries = df_kualitas_hidup['nama_negara'].nunique()
        st.metric(label="Jumlah Negara", value=unique_countries)

    # Sidebar: Filter
    st.sidebar.header("Filter Kualitas Hidup")

    # Filter Tahun
    min_year = int(df_kualitas_hidup['tahun'].min()) if df_kualitas_hidup['tahun'].notna().any() else 2018
    max_year = int(df_kualitas_hidup['tahun'].max()) if df_kualitas_hidup['tahun'].notna().any() else 2023
    
    if min_year >= max_year:
        yr = st.sidebar.number_input("Pilih Tahun Kualitas Hidup", min_value=int(min_year), max_value=int(max_year), value=int(min_year), step=1)
        year_range = (int(yr), int(yr))
    else:
        year_range = st.sidebar.slider(
            "Pilih Rentang Tahun Kualitas Hidup",
            min_value=int(min_year),
            max_value=int(max_year),
            value=(int(min_year), int(max_year))
        )

    # Filter Negara
    countries_list = sorted(df_kualitas_hidup['nama_negara'].unique().tolist())
    selected_countries = st.sidebar.multiselect("Pilih Negara Kualitas Hidup (kosong = semua)", options=countries_list)

    # Terapkan filter
    filtered_df = df_kualitas_hidup[
        df_kualitas_hidup['tahun'].between(year_range[0], year_range[1])
    ]

    if selected_countries:
        filtered_df = filtered_df[filtered_df['nama_negara'].isin(selected_countries)]

    # Tampilkan tabel
    st.markdown("### Tabel Data Kualitas Hidup")
    showdata = st.multiselect(
        "Pilih Kolom yang Ditampilkan",
        options=filtered_df.columns.tolist(),
        default=["nama_negara", "tahun", "indeks_kualitas_hidup", "indeks_keamanan", "indeks_kesehatan", "indeks_pendidikan"]
    )

    st.dataframe(filtered_df[showdata], use_container_width=True)

    # Download CSV
    @st.cache_data
    def convert_df_to_csv(_df):
        return _df.to_csv(index=False).encode('utf-8')

    csv = convert_df_to_csv(filtered_df[showdata])
    st.download_button(
        label="Download Data Kualitas Hidup sebagai CSV",
        data=csv,
        file_name='data_kualitas_hidup.csv',
        mime='text/csv'
    )

    # Visualisasi
    st.markdown("### Visualisasi Kualitas Hidup")
    
    # Chart 1: Top 10 Negara dengan Indeks Kualitas Hidup Tertinggi
    avg_by_country = filtered_df.groupby('nama_negara')['indeks_kualitas_hidup'].mean().sort_values(ascending=False).head(10)
    fig1 = px.bar(
        x=avg_by_country.values,
        y=avg_by_country.index,
        orientation='h',
        title='Negara dengan Rata-rata Indeks Kualitas Hidup Tertinggi',
        labels={'x': 'Indeks Kualitas Hidup', 'y': 'Negara'},
        color=avg_by_country.values,
        color_continuous_scale='Greens'
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Perbandingan Indeks
    if not filtered_df.empty:
        avg_indices = filtered_df[['indeks_kualitas_hidup', 'indeks_keamanan', 'indeks_kesehatan', 'indeks_pendidikan', 'indeks_biaya_hidup']].mean()
        fig2 = px.bar(
            x=avg_indices.index,
            y=avg_indices.values,
            title='Rata-rata Indeks Kualitas Hidup',
            labels={'x': 'Indeks', 'y': 'Nilai'},
            color=avg_indices.values,
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig2, use_container_width=True)


# ========== FUNGSI UNTUK ANALISIS KORELASI ==========
def analisis_korelasi():
    st.header("Analisis Korelasi Polusi vs Kualitas Hidup")
    
    if df_polusi.empty or df_kualitas_hidup.empty:
        st.warning("Data tidak lengkap untuk analisis korelasi.")
        return

    # Merge data polusi dan kualitas hidup berdasarkan negara dan tahun
    merged_df = pd.merge(
        df_polusi.groupby(['nama_negara', 'tahun']).agg({
            'indeks_kualitas_udara': 'mean',
            'indeks_karbon': 'mean',
            'indeks_ozon': 'mean',
            'indeks_nitrogen_dioksida': 'mean'
        }).reset_index(),
        df_kualitas_hidup.groupby(['nama_negara', 'tahun']).agg({
            'indeks_kualitas_hidup': 'mean',
            'indeks_keamanan': 'mean',
            'indeks_kesehatan': 'mean',
            'indeks_pendidikan': 'mean'
        }).reset_index(),
        on=['nama_negara', 'tahun'],
        how='inner'
    )

    if merged_df.empty:
        st.warning("Tidak ada data yang cocok untuk analisis korelasi.")
        return

    st.markdown("### Data Gabungan")
    st.dataframe(merged_df, use_container_width=True)

    # Scatter plot: Indeks Kualitas Udara vs Indeks Kualitas Hidup
    st.markdown("### Scatter Plot: Indeks Kualitas Udara vs Indeks Kualitas Hidup")
    fig = px.scatter(
        merged_df,
        x='indeks_kualitas_udara',
        y='indeks_kualitas_hidup',
        color='nama_negara',
        size='tahun',
        hover_data=['nama_negara', 'tahun'],
        title='Korelasi antara Indeks Kualitas Udara dan Indeks Kualitas Hidup',
        labels={'indeks_kualitas_udara': 'Indeks Kualitas Udara', 'indeks_kualitas_hidup': 'Indeks Kualitas Hidup'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap korelasi
    st.markdown("### Heatmap Korelasi")
    corr_df = merged_df[['indeks_kualitas_udara', 'indeks_karbon', 'indeks_ozon', 'indeks_nitrogen_dioksida', 
                          'indeks_kualitas_hidup', 'indeks_keamanan', 'indeks_kesehatan', 'indeks_pendidikan']].corr()
    
    fig_heatmap = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        title='Heatmap Korelasi Indeks Polusi dan Kualitas Hidup',
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)


# ========== SIDEBAR MENU ==========
st.sidebar.title("Menu Dashboard")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Pilih Halaman:",
    ["Data Polusi", "Kualitas Hidup", "Analisis Korelasi"]
)

st.sidebar.markdown("---")
st.sidebar.info("Dashboard Visualisasi Data Polusi & Kualitas Hidup")

# ========== MAIN CONTENT ==========
if menu == "Data Polusi":
    tabel_polusi_dan_export()

elif menu == "Kualitas Hidup":
    tabel_kualitas_hidup_dan_export()

elif menu == "Analisis Korelasi":
    analisis_korelasi()