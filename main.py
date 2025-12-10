import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DatabaseConfig

# Konfigurasi halaman
st.set_page_config(
    page_title="Visualisasi Data Polusi & Kualitas Hidup",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi helper
def format_number(num):
    """Format angka dengan pemisah ribuan"""
    if pd.isna(num):
        return "N/A"
    return f"{num:,.0f}".replace(",", ".")

def create_metric_card(title, value, delta=None):
    """Membuat metric card"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label=title, value=value, delta=delta)

# Sidebar Navigation
with st.sidebar:
    st.title("Dashboard Polusi")
    st.markdown("---")
    
    menu = st.radio(
        "Menu Navigasi",
        ["Home", "Polusi Udara", "Kualitas Hidup", "Perbandingan Data"],
        label_visibility="collapsed"
    )
    

# ============================================
# HALAMAN HOME
# ============================================
if menu == "Home":
    st.title("Dashboard Polusi dan Kualitas Hidup Global")
    st.markdown("Selamat datang di dashboard visualisasi data polusi dan kualitas hidup kota-kota di dunia")
    
    # Statistik Ringkasan
    stats = DatabaseConfig.get_summary_stats()
    
    if not stats.empty:
        st.markdown("### Ringkasan Data")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Negara", int(stats['total_negara'].values[0]))
        with col2:
            st.metric("Total Kota", int(stats['total_kota'].values[0]))
        with col3:
            st.metric("Rata-rata Polusi", f"{stats['avg_polusi'].values[0]:.1f}")
        with col4:
            st.metric("Rata-rata Kualitas Hidup", f"{stats['avg_kualitas_hidup'].values[0]:.1f}")
    
    st.markdown("---")
    
    # Data Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Data Polusi Terkini")
        polusi_df = DatabaseConfig.get_polusi_data()
        if not polusi_df.empty:
            # Ambil data tahun terbaru
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].nlargest(5, 'index_kualitas_udara')
            
            # Bar chart polusi tertinggi
            fig = px.bar(
                latest_polusi,
                x='nama_kota',
                y='index_kualitas_udara',
                title=f'5 Kota dengan Polusi Tertinggi ({latest_year})',
                labels={'nama_kota': 'Kota', 'index_kualitas_udara': 'Index Polusi'},
                color='index_kualitas_udara',
                color_continuous_scale='Reds'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Data polusi tidak tersedia")
    
    with col2:
        st.markdown("### Data Kualitas Hidup Terkini")
        kualitas_df = DatabaseConfig.get_kualitas_hidup_data()
        if not kualitas_df.empty:
            # Ambil data tahun terbaru
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].nlargest(5, 'index_kualitas_hidup')
            
            # Bar chart kualitas hidup tertinggi
            fig = px.bar(
                latest_kualitas,
                x='nama_kota',
                y='index_kualitas_hidup',
                title=f'5 Kota dengan Kualitas Hidup Terbaik ({latest_year})',
                labels={'nama_kota': 'Kota', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                color='index_kualitas_hidup',
                color_continuous_scale='Greens'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Data kualitas hidup tidak tersedia")
    
    # Distribusi per Benua
    st.markdown("---")
    st.markdown("### Distribusi Kota per Benua")
    
    negara_df = DatabaseConfig.get_negara_list()
    kota_df = DatabaseConfig.get_all_kota()
    
    if not negara_df.empty and not kota_df.empty:
        # Merge untuk mendapatkan benua
        kota_benua = kota_df.merge(negara_df[['kode_negara', 'benua']], on='kode_negara')
        benua_count = kota_benua['benua'].value_counts().reset_index()
        benua_count.columns = ['benua', 'jumlah_kota']
        
        fig = px.pie(
            benua_count,
            values='jumlah_kota',
            names='benua',
            title='Distribusi Kota Berdasarkan Benua',
            color_discrete_sequence=DatabaseConfig.COLOR_PALETTE
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# HALAMAN POLUSI
# ============================================
elif menu == "Polusi Udara":
    st.title("Analisis Data Polusi Udara")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        negara_list = DatabaseConfig.get_negara_list()
        negara_options = ['Semua Negara'] + negara_list['nama'].tolist()
        selected_negara = st.selectbox("Pilih Negara", negara_options)
    
    with col2:
        if selected_negara != 'Semua Negara':
            kode_negara = negara_list[negara_list['nama'] == selected_negara]['kode_negara'].values[0]
            kota_list = DatabaseConfig.get_kota_by_negara(kode_negara)
            kota_options = ['Semua Kota'] + kota_list['nama_kota'].tolist()
            selected_kota = st.selectbox("Pilih Kota", kota_options)
        else:
            selected_kota = 'Semua Kota'
            st.selectbox("Pilih Kota", ['Semua Kota'], disabled=True)
    
    # Ambil data
    if selected_negara != 'Semua Negara' and selected_kota != 'Semua Kota':
        id_kota = kota_list[kota_list['nama_kota'] == selected_kota]['id_kota'].values[0]
        polusi_df = DatabaseConfig.get_polusi_data(id_kota=id_kota)
    elif selected_negara != 'Semua Negara':
        # Filter berdasarkan negara
        all_kota = DatabaseConfig.get_kota_by_negara(kode_negara)
        kota_ids = all_kota['id_kota'].tolist()
        polusi_df = DatabaseConfig.get_polusi_data()
        polusi_df = polusi_df[polusi_df['id_kota'].isin(kota_ids)]
    else:
        polusi_df = DatabaseConfig.get_polusi_data()
    
    if not polusi_df.empty:
        st.markdown("---")
        
        # Metrics
        latest_data = polusi_df[polusi_df['tahun'] == polusi_df['tahun'].max()]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_aqi = latest_data['index_kualitas_udara'].mean()
            st.metric("Rata-rata Index Polusi", f"{avg_aqi:.1f}")
        with col2:
            avg_pm25 = latest_data['pm25'].mean()
            st.metric("Rata-rata PM2.5", f"{avg_pm25:.1f}")
        with col3:
            avg_co2 = latest_data['index_co2'].mean()
            st.metric("Rata-rata CO2", f"{avg_co2:.1f}")
        with col4:
            avg_no2 = latest_data['index_no2'].mean()
            st.metric("Rata-rata NO2", f"{avg_no2:.1f}")
        
        st.markdown("---")
        
        # Visualisasi
        tab1, tab2, tab3 = st.tabs(["Trend Polusi", "Perbandingan Indikator", "Perbandingan Kota"])
        
        with tab1:
            st.subheader("Trend Index Kualitas Udara")
            
            if selected_kota != 'Semua Kota':
                # Trend untuk satu kota
                fig = px.line(
                    polusi_df,
                    x='tahun',
                    y='index_kualitas_udara',
                    title=f'Trend Polusi - {selected_kota}',
                    labels={'tahun': 'Tahun', 'index_kualitas_udara': 'Index Kualitas Udara'},
                    markers=True
                )
                fig.update_traces(line_color=DatabaseConfig.COLORS['danger'])
            else:
                # Trend untuk multiple kota
                fig = px.line(
                    polusi_df,
                    x='tahun',
                    y='index_kualitas_udara',
                    color='nama_kota',
                    title='Trend Polusi per Kota',
                    labels={'tahun': 'Tahun', 'index_kualitas_udara': 'Index Kualitas Udara'},
                    markers=True,
                    color_discrete_sequence=DatabaseConfig.COLOR_PALETTE
                )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Perbandingan Indikator Polusi")
            
            # Ambil data tahun terbaru
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].copy()
            
            if not latest_polusi.empty:
                # Pilih kota untuk ditampilkan (max 10)
                if len(latest_polusi) > 10:
                    latest_polusi = latest_polusi.nlargest(10, 'index_kualitas_udara')
                
                # Reshape data untuk grouped bar chart
                indicators = ['index_co2', 'index_ozone', 'index_no2', 'pm25']
                
                fig = go.Figure()
                
                for indicator in indicators:
                    fig.add_trace(go.Bar(
                        name=indicator.replace('index_', '').replace('_', ' ').upper(),
                        x=latest_polusi['nama_kota'],
                        y=latest_polusi[indicator]
                    ))
                
                fig.update_layout(
                    title=f'Perbandingan Indikator Polusi ({latest_year})',
                    xaxis_title='Kota',
                    yaxis_title='Nilai Index',
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Perbandingan Polusi Antar Kota")
            
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].copy()
            
            if not latest_polusi.empty:
                # Horizontal bar chart
                latest_polusi_sorted = latest_polusi.sort_values('index_kualitas_udara', ascending=True)
                
                fig = px.bar(
                    latest_polusi_sorted,
                    y='nama_kota',
                    x='index_kualitas_udara',
                    orientation='h',
                    title=f'Index Kualitas Udara per Kota ({latest_year})',
                    labels={'nama_kota': 'Kota', 'index_kualitas_udara': 'Index Kualitas Udara'},
                    color='index_kualitas_udara',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=max(400, len(latest_polusi_sorted) * 30))
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Data
        st.markdown("---")
        st.subheader("Data Detail")
        
        # Pilihan kolom yang dapat ditampilkan
        available_columns = {
            'nama_kota': 'Nama Kota',
            'nama_negara': 'Nama Negara',
            'tahun': 'Tahun',
            'index_kualitas_udara': 'Index Kualitas Udara',
            'index_co2': 'Index CO2',
            'index_ozone': 'Index Ozone',
            'index_no2': 'Index NO2',
            'pm25': 'PM2.5'
        }
        
        # Multiselect untuk memilih kolom
        selected_columns = st.multiselect(
            "Pilih kolom yang ingin ditampilkan:",
            options=list(available_columns.keys()),
            default=list(available_columns.keys()),
            format_func=lambda x: available_columns[x]
        )
        
        if selected_columns:
            # Filter dataframe berdasarkan kolom yang dipilih
            display_df = polusi_df[selected_columns].sort_values('tahun', ascending=False) if 'tahun' in selected_columns else polusi_df[selected_columns]
            
            # Tampilkan dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Menampilkan {len(display_df)} baris data")
        else:
            st.warning("Pilih minimal satu kolom untuk ditampilkan")

# ============================================
# HALAMAN KUALITAS HIDUP
# ============================================
elif menu == "Kualitas Hidup":
    st.title("Analisis Kualitas Hidup")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        negara_list = DatabaseConfig.get_negara_list()
        negara_options = ['Semua Negara'] + negara_list['nama'].tolist()
        selected_negara = st.selectbox("Pilih Negara", negara_options)
    
    with col2:
        if selected_negara != 'Semua Negara':
            kode_negara = negara_list[negara_list['nama'] == selected_negara]['kode_negara'].values[0]
            kota_list = DatabaseConfig.get_kota_by_negara(kode_negara)
            kota_options = ['Semua Kota'] + kota_list['nama_kota'].tolist()
            selected_kota = st.selectbox("Pilih Kota", kota_options)
        else:
            selected_kota = 'Semua Kota'
            st.selectbox("Pilih Kota", ['Semua Kota'], disabled=True)
    
    # Ambil data
    if selected_negara != 'Semua Negara' and selected_kota != 'Semua Kota':
        id_kota = kota_list[kota_list['nama_kota'] == selected_kota]['id_kota'].values[0]
        kualitas_df = DatabaseConfig.get_kualitas_hidup_data(id_kota=id_kota)
    elif selected_negara != 'Semua Negara':
        all_kota = DatabaseConfig.get_kota_by_negara(kode_negara)
        kota_ids = all_kota['id_kota'].tolist()
        kualitas_df = DatabaseConfig.get_kualitas_hidup_data()
        kualitas_df = kualitas_df[kualitas_df['id_kota'].isin(kota_ids)]
    else:
        kualitas_df = DatabaseConfig.get_kualitas_hidup_data()
    
    if not kualitas_df.empty:
        st.markdown("---")
        
        # Metrics
        latest_data = kualitas_df[kualitas_df['tahun'] == kualitas_df['tahun'].max()]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            avg_kualitas = latest_data['index_kualitas_hidup'].mean()
            st.metric("Index Kualitas", f"{avg_kualitas:.1f}")
        with col2:
            avg_keamanan = latest_data['index_keamanan'].mean()
            st.metric("Keamanan", f"{avg_keamanan:.1f}")
        with col3:
            avg_kesehatan = latest_data['index_kesehatan'].mean()
            st.metric("Kesehatan", f"{avg_kesehatan:.1f}")
        with col4:
            avg_pendidikan = latest_data['index_pendidikan'].mean()
            st.metric("Pendidikan", f"{avg_pendidikan:.1f}")
        with col5:
            avg_biaya = latest_data['index_biaya_hidup'].mean()
            st.metric("Biaya Hidup", f"{avg_biaya:.1f}")
        
        st.markdown("---")
        
        # Visualisasi
        tab1, tab2, tab3 = st.tabs(["Trend Kualitas Hidup", "Breakdown Indikator", "Ranking Kota"])
        
        with tab1:
            st.subheader("Trend Index Kualitas Hidup")
            
            if selected_kota != 'Semua Kota':
                fig = px.line(
                    kualitas_df,
                    x='tahun',
                    y='index_kualitas_hidup',
                    title=f'Trend Kualitas Hidup - {selected_kota}',
                    labels={'tahun': 'Tahun', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                    markers=True
                )
                fig.update_traces(line_color=DatabaseConfig.COLORS['success'])
            else:
                fig = px.line(
                    kualitas_df,
                    x='tahun',
                    y='index_kualitas_hidup',
                    color='nama_kota',
                    title='Trend Kualitas Hidup per Kota',
                    labels={'tahun': 'Tahun', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                    markers=True,
                    color_discrete_sequence=DatabaseConfig.COLOR_PALETTE
                )
            
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Breakdown Indikator Kualitas Hidup")
            
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].copy()
            
            if not latest_kualitas.empty:
                if len(latest_kualitas) > 10:
                    latest_kualitas = latest_kualitas.nlargest(10, 'index_kualitas_hidup')
                
                indicators = ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']
                
                fig = go.Figure()
                
                for indicator in indicators:
                    fig.add_trace(go.Bar(
                        name=indicator.replace('index_', '').replace('_', ' ').title(),
                        x=latest_kualitas['nama_kota'],
                        y=latest_kualitas[indicator]
                    ))
                
                fig.update_layout(
                    title=f'Breakdown Indikator Kualitas Hidup ({latest_year})',
                    xaxis_title='Kota',
                    yaxis_title='Nilai Index',
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Ranking Kota Berdasarkan Kualitas Hidup")
            
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].copy()
            
            if not latest_kualitas.empty:
                latest_kualitas_sorted = latest_kualitas.sort_values('index_kualitas_hidup', ascending=True)
                
                fig = px.bar(
                    latest_kualitas_sorted,
                    y='nama_kota',
                    x='index_kualitas_hidup',
                    orientation='h',
                    title=f'Ranking Kualitas Hidup per Kota ({latest_year})',
                    labels={'nama_kota': 'Kota', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                    color='index_kualitas_hidup',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=max(400, len(latest_kualitas_sorted) * 30))
                st.plotly_chart(fig, use_container_width=True)
        
       # Tabel Data
        st.markdown("---")
        st.subheader("Data Detail")
        
        # Pilihan kolom yang dapat ditampilkan
        available_columns = {
            'nama_kota': 'Nama Kota',
            'nama_negara': 'Nama Negara',
            'tahun': 'Tahun',
            'index_kualitas_hidup': 'Index Kualitas Hidup',
            'index_keamanan': 'Index Keamanan',
            'index_kesehatan': 'Index Kesehatan',
            'index_pendidikan': 'Index Pendidikan',
            'index_biaya_hidup': 'Index Biaya Hidup'
        }
        
        # Multiselect untuk memilih kolom
        selected_columns = st.multiselect(
            "Pilih kolom yang ingin ditampilkan:",
            options=list(available_columns.keys()),
            default=['nama_kota', 'nama_negara', 'tahun', 'index_kualitas_hidup', 'index_keamanan'],
            format_func=lambda x: available_columns[x],
            key="kualitas_columns"
        )
        
        if selected_columns:
            # Filter dataframe berdasarkan kolom yang dipilih
            display_df = kualitas_df[selected_columns].sort_values('tahun', ascending=False) if 'tahun' in selected_columns else kualitas_df[selected_columns]
            
            # Tampilkan dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Menampilkan {len(display_df)} baris data")
        else:
            st.warning("Pilih minimal satu kolom untuk ditampilkan")
    else:
        st.warning("Data kualitas hidup tidak tersedia untuk filter yang dipilih")
# ============================================
# HALAMAN PERBANDINGAN DATA
# ============================================
elif menu == "Perbandingan Data":
    st.title("Perbandingan Data Antar Kota")
    
    st.markdown("### Pilih Kota untuk Dibandingkan")
    
    # Filter untuk memilih kota
    kota_all = DatabaseConfig.get_all_kota()
    
    if not kota_all.empty:
        kota_all['display_name'] = kota_all['nama_kota'] + ' (' + kota_all['nama_negara'] + ')'
        
        col1, col2 = st.columns(2)
        
        with col1:
            kota1 = st.selectbox(
                "Kota Pertama",
                options=kota_all['display_name'].tolist(),
                key='kota1'
            )
            id_kota1 = kota_all[kota_all['display_name'] == kota1]['id_kota'].values[0]
        
        with col2:
            kota2 = st.selectbox(
                "Kota Kedua",
                options=kota_all['display_name'].tolist(),
                index=1 if len(kota_all) > 1 else 0,
                key='kota2'
            )
            id_kota2 = kota_all[kota_all['display_name'] == kota2]['id_kota'].values[0]
        
        if id_kota1 == id_kota2:
            st.warning("Pilih dua kota yang berbeda untuk perbandingan")
        else:
            st.markdown("---")
            
            # Ambil data kedua kota
            polusi1 = DatabaseConfig.get_polusi_data(id_kota=id_kota1)
            polusi2 = DatabaseConfig.get_polusi_data(id_kota=id_kota2)
            kualitas1 = DatabaseConfig.get_kualitas_hidup_data(id_kota=id_kota1)
            kualitas2 = DatabaseConfig.get_kualitas_hidup_data(id_kota=id_kota2)
            
            # Tab untuk berbagai perbandingan
            tab1, tab2, tab3 = st.tabs(["Perbandingan Polusi", "Perbandingan Kualitas Hidup", "Overview"])
            
            with tab1:
                st.subheader("Perbandingan Data Polusi")
                
                if not polusi1.empty and not polusi2.empty:
                    # Ambil tahun terbaru yang ada di kedua kota
                    common_years = set(polusi1['tahun'].tolist()) & set(polusi2['tahun'].tolist())
                    
                    if common_years:
                        latest_year = max(common_years)
                        p1 = polusi1[polusi1['tahun'] == latest_year].iloc[0]
                        p2 = polusi2[polusi2['tahun'] == latest_year].iloc[0]
                        
                        # Metrics comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {p1['nama_kota']}")
                            st.metric("Index Kualitas Udara", f"{p1['index_kualitas_udara']:.1f}")
                            st.metric("PM2.5", f"{p1['pm25']:.1f}")
                            st.metric("CO2", f"{p1['index_co2']:.1f}")
                            st.metric("NO2", f"{p1['index_no2']:.1f}")
                        
                        with col2:
                            st.markdown(f"#### {p2['nama_kota']}")
                            delta_aqi = p2['index_kualitas_udara'] - p1['index_kualitas_udara']
                            st.metric("Index Kualitas Udara", f"{p2['index_kualitas_udara']:.1f}", 
                                     delta=f"{delta_aqi:+.1f}", delta_color="inverse")
                            
                            delta_pm25 = p2['pm25'] - p1['pm25']
                            st.metric("PM2.5", f"{p2['pm25']:.1f}", 
                                     delta=f"{delta_pm25:+.1f}", delta_color="inverse")
                            
                            delta_co2 = p2['index_co2'] - p1['index_co2']
                            st.metric("CO2", f"{p2['index_co2']:.1f}", 
                                     delta=f"{delta_co2:+.1f}", delta_color="inverse")
                            
                            delta_no2 = p2['index_no2'] - p1['index_no2']
                            st.metric("NO2", f"{p2['index_no2']:.1f}", 
                                     delta=f"{delta_no2:+.1f}", delta_color="inverse")
                        
                        st.markdown("---")
                        
                        # Comparison chart
                        indicators = ['index_kualitas_udara', 'pm25', 'index_co2', 'index_no2']
                        values1 = [p1[ind] for ind in indicators]
                        values2 = [p2[ind] for ind in indicators]
                        labels = ['Index Polusi', 'PM2.5', 'CO2', 'NO2']
                        
                        fig = go.Figure(data=[
                            go.Bar(name=p1['nama_kota'], x=labels, y=values1),
                            go.Bar(name=p2['nama_kota'], x=labels, y=values2)
                        ])
                        
                        fig.update_layout(
                            title=f'Perbandingan Indikator Polusi ({latest_year})',
                            barmode='group',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Trend comparison
                        st.markdown("#### Trend Polusi dari Waktu ke Waktu")
                        
                        combined_polusi = pd.concat([
                            polusi1.assign(kota=p1['nama_kota']),
                            polusi2.assign(kota=p2['nama_kota'])
                        ])
                        
                        fig = px.line(
                            combined_polusi,
                            x='tahun',
                            y='index_kualitas_udara',
                            color='kota',
                            markers=True,
                            labels={'tahun': 'Tahun', 'index_kualitas_udara': 'Index Kualitas Udara'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Tidak ada data tahun yang sama untuk kedua kota")
                else:
                    st.warning("Data polusi tidak lengkap untuk perbandingan")
            
            with tab2:
                st.subheader("Perbandingan Kualitas Hidup")
                
                if not kualitas1.empty and not kualitas2.empty:
                    common_years = set(kualitas1['tahun'].tolist()) & set(kualitas2['tahun'].tolist())
                    
                    if common_years:
                        latest_year = max(common_years)
                        k1 = kualitas1[kualitas1['tahun'] == latest_year].iloc[0]
                        k2 = kualitas2[kualitas2['tahun'] == latest_year].iloc[0]
                        
                        # Metrics comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {k1['nama_kota']}")
                            st.metric("Index Kualitas Hidup", f"{k1['index_kualitas_hidup']:.1f}")
                            st.metric("Keamanan", f"{k1['index_keamanan']:.1f}")
                            st.metric("Kesehatan", f"{k1['index_kesehatan']:.1f}")
                            st.metric("Pendidikan", f"{k1['index_pendidikan']:.1f}")
                            st.metric("Biaya Hidup", f"{k1['index_biaya_hidup']:.1f}")
                        
                        with col2:
                            st.markdown(f"#### {k2['nama_kota']}")
                            
                            delta_kualitas = k2['index_kualitas_hidup'] - k1['index_kualitas_hidup']
                            st.metric("Index Kualitas Hidup", f"{k2['index_kualitas_hidup']:.1f}", 
                                     delta=f"{delta_kualitas:+.1f}")
                            
                            delta_keamanan = k2['index_keamanan'] - k1['index_keamanan']
                            st.metric("Keamanan", f"{k2['index_keamanan']:.1f}", 
                                     delta=f"{delta_keamanan:+.1f}")
                            
                            delta_kesehatan = k2['index_kesehatan'] - k1['index_kesehatan']
                            st.metric("Kesehatan", f"{k2['index_kesehatan']:.1f}", 
                                     delta=f"{delta_kesehatan:+.1f}")
                            
                            delta_pendidikan = k2['index_pendidikan'] - k1['index_pendidikan']
                            st.metric("Pendidikan", f"{k2['index_pendidikan']:.1f}", 
                                     delta=f"{delta_pendidikan:+.1f}")
                            
                            delta_biaya = k2['index_biaya_hidup'] - k1['index_biaya_hidup']
                            st.metric("Biaya Hidup", f"{k2['index_biaya_hidup']:.1f}", 
                                     delta=f"{delta_biaya:+.1f}")
                        
                        st.markdown("---")
                        
                        # Radar chart comparison
                        indicators = ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']
                        labels = ['Keamanan', 'Kesehatan', 'Pendidikan', 'Biaya Hidup']
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatterpolar(
                            r=[k1[ind] for ind in indicators],
                            theta=labels,
                            fill='toself',
                            name=k1['nama_kota']
                        ))
                        
                        fig.add_trace(go.Scatterpolar(
                            r=[k2[ind] for ind in indicators],
                            theta=labels,
                            fill='toself',
                            name=k2['nama_kota']
                        ))
                        
                        fig.update_layout(
                            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                            title=f'Perbandingan Indikator Kualitas Hidup ({latest_year})',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Trend comparison
                        st.markdown("#### Trend Kualitas Hidup dari Waktu ke Waktu")
                        
                        combined_kualitas = pd.concat([
                            kualitas1.assign(kota=k1['nama_kota']),
                            kualitas2.assign(kota=k2['nama_kota'])
                        ])
                        
                        fig = px.line(
                            combined_kualitas,
                            x='tahun',
                            y='index_kualitas_hidup',
                            color='kota',
                            markers=True,
                            labels={'tahun': 'Tahun', 'index_kualitas_hidup': 'Index Kualitas Hidup'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Tidak ada data tahun yang sama untuk kedua kota")
                else:
                    st.warning("Data kualitas hidup tidak lengkap untuk perbandingan")
            
            with tab3:
                st.subheader("Overview Perbandingan")
                
                if not polusi1.empty and not polusi2.empty and not kualitas1.empty and not kualitas2.empty:
                    # Cari tahun terbaru yang ada di semua data
                    all_years = (set(polusi1['tahun'].tolist()) & set(polusi2['tahun'].tolist()) &
                                set(kualitas1['tahun'].tolist()) & set(kualitas2['tahun'].tolist()))
                    
                    if all_years:
                        latest_year = max(all_years)
                        
                        p1 = polusi1[polusi1['tahun'] == latest_year].iloc[0]
                        p2 = polusi2[polusi2['tahun'] == latest_year].iloc[0]
                        k1 = kualitas1[kualitas1['tahun'] == latest_year].iloc[0]
                        k2 = kualitas2[kualitas2['tahun'] == latest_year].iloc[0]
                        
                        # Comparison table
                        comparison_data = {
                            'Indikator': [
                                'Index Polusi',
                                'PM2.5',
                                'CO2',
                                'Index Kualitas Hidup',
                                'Keamanan',
                                'Kesehatan',
                                'Pendidikan'
                            ],
                            k1['nama_kota']: [
                                f"{p1['index_kualitas_udara']:.1f}",
                                f"{p1['pm25']:.1f}",
                                f"{p1['index_co2']:.1f}",
                                f"{k1['index_kualitas_hidup']:.1f}",
                                f"{k1['index_keamanan']:.1f}",
                                f"{k1['index_kesehatan']:.1f}",
                                f"{k1['index_pendidikan']:.1f}"
                            ],
                            k2['nama_kota']: [
                                f"{p2['index_kualitas_udara']:.1f}",
                                f"{p2['pm25']:.1f}",
                                f"{p2['index_co2']:.1f}",
                                f"{k2['index_kualitas_hidup']:.1f}",
                                f"{k2['index_keamanan']:.1f}",
                                f"{k2['index_kesehatan']:.1f}",
                                f"{k2['index_pendidikan']:.1f}"
                            ],
                            'Selisih': [
                                f"{(p2['index_kualitas_udara'] - p1['index_kualitas_udara']):.1f}",
                                f"{(p2['pm25'] - p1['pm25']):.1f}",
                                f"{(p2['index_co2'] - p1['index_co2']):.1f}",
                                f"{(k2['index_kualitas_hidup'] - k1['index_kualitas_hidup']):.1f}",
                                f"{(k2['index_keamanan'] - k1['index_keamanan']):.1f}",
                                f"{(k2['index_kesehatan'] - k1['index_kesehatan']):.1f}",
                                f"{(k2['index_pendidikan'] - k1['index_pendidikan']):.1f}"
                            ]
                        }
                        
                        df_comparison = pd.DataFrame(comparison_data)
                        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        
                        # Summary insights
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Ringkasan Polusi")
                            if p1['index_kualitas_udara'] < p2['index_kualitas_udara']:
                                st.success(f"{p1['nama_kota']} memiliki kualitas udara lebih baik")
                            else:
                                st.success(f"{p2['nama_kota']} memiliki kualitas udara lebih baik")
                        
                        with col2:
                            st.markdown("#### Ringkasan Kualitas Hidup")
                            if k1['index_kualitas_hidup'] > k2['index_kualitas_hidup']:
                                st.success(f"{k1['nama_kota']} memiliki kualitas hidup lebih baik")
                            else:
                                st.success(f"{k2['nama_kota']} memiliki kualitas hidup lebih baik")
                    else:
                        st.warning("Tidak ada data lengkap untuk tahun yang sama")
                else:
                    st.warning("Data tidak lengkap untuk overview perbandingan")
    else:
        st.error("Data kota tidak tersedia")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Dashboard Polusi dan Kualitas Hidup | Kelompok 9</p>
</div>
""", unsafe_allow_html=True)