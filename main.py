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

# Fungsi helper untuk filter negara dan kota
def render_filter(key_prefix):
    """Render filter negara dan kota"""
    col1, col2 = st.columns(2)
    
    with col1:
        negara_list = DatabaseConfig.get_negara_list()
        negara_options = ['Semua Negara'] + negara_list['nama'].tolist()
        selected_negara = st.selectbox("Pilih Negara", negara_options, key=f"{key_prefix}_negara")
    
    with col2:
        if selected_negara != 'Semua Negara':
            kode_negara = negara_list[negara_list['nama'] == selected_negara]['kode_negara'].values[0]
            kota_list = DatabaseConfig.get_kota_by_negara(kode_negara)
            kota_options = ['Semua Kota'] + kota_list['nama_kota'].tolist()
            selected_kota = st.selectbox("Pilih Kota", kota_options, key=f"{key_prefix}_kota")
        else:
            selected_kota = 'Semua Kota'
            kota_list = None
            st.selectbox("Pilih Kota", ['Semua Kota'], disabled=True, key=f"{key_prefix}_kota_disabled")
    
    return selected_negara, selected_kota, negara_list, kota_list

def get_filtered_data(selected_negara, selected_kota, negara_list, kota_list, data_type='polusi'):
    """Ambil data berdasarkan filter"""
    get_data_func = DatabaseConfig.get_polusi_data if data_type == 'polusi' else DatabaseConfig.get_kualitas_hidup_data
    
    if selected_negara != 'Semua Negara' and selected_kota != 'Semua Kota':
        id_kota = kota_list[kota_list['nama_kota'] == selected_kota]['id_kota'].values[0]
        return get_data_func(id_kota=id_kota)
    elif selected_negara != 'Semua Negara':
        kode_negara = negara_list[negara_list['nama'] == selected_negara]['kode_negara'].values[0]
        all_kota = DatabaseConfig.get_kota_by_negara(kode_negara)
        kota_ids = all_kota['id_kota'].tolist()
        df = get_data_func()
        return df[df['id_kota'].isin(kota_ids)]
    else:
        return get_data_func()

def render_metrics(df, metrics_config):
    """Render metrics secara dinamis"""
    latest_data = df[df['tahun'] == df['tahun'].max()]
    cols = st.columns(len(metrics_config))
    
    for i, (col_name, label) in enumerate(metrics_config.items()):
        with cols[i]:
            avg_val = latest_data[col_name].mean()
            st.metric(label, f"{avg_val:.1f}")

def render_trend_chart(df, y_col, title, selected_kota, color):
    """Render chart trend"""
    if selected_kota != 'Semua Kota':
        fig = px.line(df, x='tahun', y=y_col, title=f'{title} - {selected_kota}', 
                     labels={'tahun': 'Tahun', y_col: title}, markers=True)
        fig.update_traces(line_color=color)
    else:
        fig = px.line(df, x='tahun', y=y_col, color='nama_kota', 
                     title=f'{title} per Kota', labels={'tahun': 'Tahun', y_col: title}, 
                     markers=True, color_discrete_sequence=DatabaseConfig.COLOR_PALETTE)
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_data_table(df, available_columns, default_cols, key):
    """Render tabel data dengan pemilihan kolom"""
    st.markdown("---")
    st.subheader("Data Detail")
    
    selected_columns = st.multiselect(
        "Pilih kolom yang ingin ditampilkan:",
        options=list(available_columns.keys()),
        default=default_cols,
        format_func=lambda x: available_columns[x],
        key=key
    )
    
    if selected_columns:
        display_df = df[selected_columns].sort_values('tahun', ascending=False) if 'tahun' in selected_columns else df[selected_columns]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(f"Menampilkan {len(display_df)} baris data")
    else:
        st.warning("Pilih minimal satu kolom untuk ditampilkan")

# Sidebar Navigation
with st.sidebar:
    st.title("Dashboard Menu")
    st.markdown("---")
    menu = st.radio("Menu Navigasi", ["Home", "Polusi Udara", "Kualitas Hidup", "Perbandingan Data"], 
                   label_visibility="collapsed")

# ============================================
# HALAMAN HOME
# ============================================
if menu == "Home":
    st.title("Dashboard Polusi dan Kualitas Hidup Global")
    st.markdown("dashboard visualisasi data polusi dan kualitas hidup kota-kota di dunia")
    
    # Statistik Ringkasan
    stats = DatabaseConfig.get_summary_stats()
    
    if not stats.empty:
        st.markdown("### Ringkasan Data")
        col1, col2, col3, col4 = st.columns(4)
        metrics_data = [
            ("Total Negara", int(stats['total_negara'].values[0])),
            ("Total Kota", int(stats['total_kota'].values[0])),
            ("Rata-rata Polusi", f"{stats['avg_polusi'].values[0]:.1f}"),
            ("Rata-rata Kualitas Hidup", f"{stats['avg_kualitas_hidup'].values[0]:.1f}")
        ]
        for col, (label, value) in zip([col1, col2, col3, col4], metrics_data):
            with col:
                st.metric(label, value)
    
    st.markdown("---")
    
    # Data Overview
    col1, col2 = st.columns(2)
    
    # Chart Polusi
    with col1:
        st.markdown("### Data Polusi Terkini")
        polusi_df = DatabaseConfig.get_polusi_data()
        if not polusi_df.empty:
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].nlargest(5, 'index_kualitas_udara')
            
            fig = px.bar(latest_polusi, x='nama_kota', y='index_kualitas_udara',
                        title=f'5 Kota dengan Polusi Tertinggi ({latest_year})',
                        labels={'nama_kota': 'Kota', 'index_kualitas_udara': 'Index Polusi'},
                        color='index_kualitas_udara', color_continuous_scale='Reds')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Data polusi tidak tersedia")
    
    # Chart Kualitas Hidup
    with col2:
        st.markdown("### Data Kualitas Hidup Terkini")
        kualitas_df = DatabaseConfig.get_kualitas_hidup_data()
        if not kualitas_df.empty:
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].nlargest(5, 'index_kualitas_hidup')
            
            fig = px.bar(latest_kualitas, x='nama_kota', y='index_kualitas_hidup',
                        title=f'5 Kota dengan Kualitas Hidup Terbaik ({latest_year})',
                        labels={'nama_kota': 'Kota', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                        color='index_kualitas_hidup', color_continuous_scale='Greens')
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
        kota_benua = kota_df.merge(negara_df[['kode_negara', 'benua']], on='kode_negara')
        benua_count = kota_benua['benua'].value_counts().reset_index()
        benua_count.columns = ['benua', 'jumlah_kota']
        
        fig = px.pie(benua_count, values='jumlah_kota', names='benua',
                    title='Distribusi Kota Berdasarkan Benua',
                    color_discrete_sequence=DatabaseConfig.COLOR_PALETTE)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

# ============================================
# HALAMAN POLUSI
# ============================================
elif menu == "Polusi Udara":
    st.title("Analisis Data Polusi Udara")
    
    # Filter
    selected_negara, selected_kota, negara_list, kota_list = render_filter("polusi")
    
    # Ambil data
    polusi_df = get_filtered_data(selected_negara, selected_kota, negara_list, kota_list, 'polusi')
    
    if not polusi_df.empty:
        st.markdown("---")
        
        # Metrics
        metrics_config = {
            'index_kualitas_udara': 'Rata-rata Index Polusi',
            'pm25': 'Rata-rata PM2.5',
            'index_co2': 'Rata-rata CO2',
            'index_no2': 'Rata-rata NO2'
        }
        render_metrics(polusi_df, metrics_config)
        
        st.markdown("---")
        
        # Visualisasi
        tab1, tab2, tab3 = st.tabs(["Trend Polusi", "Perbandingan Indikator", "Perbandingan Kota"])
        
        with tab1:
            st.subheader("Trend Index Kualitas Udara")
            render_trend_chart(polusi_df, 'index_kualitas_udara', 'Trend Polusi', 
                             selected_kota, DatabaseConfig.COLORS['danger'])
        
        with tab2:
            st.subheader("Perbandingan Indikator Polusi")
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].copy()
            
            if not latest_polusi.empty:
                if len(latest_polusi) > 10:
                    latest_polusi = latest_polusi.nlargest(10, 'index_kualitas_udara')
                
                fig = go.Figure()
                for indicator in ['index_co2', 'index_ozone', 'index_no2', 'pm25']:
                    fig.add_trace(go.Bar(
                        name=indicator.replace('index_', '').replace('_', ' ').upper(),
                        x=latest_polusi['nama_kota'],
                        y=latest_polusi[indicator]
                    ))
                
                fig.update_layout(
                    title=f'Perbandingan Indikator Polusi ({latest_year})',
                    xaxis_title='Kota', yaxis_title='Nilai Index',
                    barmode='group', height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Perbandingan Polusi Antar Kota")
            latest_year = polusi_df['tahun'].max()
            latest_polusi = polusi_df[polusi_df['tahun'] == latest_year].copy()
            
            if not latest_polusi.empty:
                latest_polusi_sorted = latest_polusi.sort_values('index_kualitas_udara', ascending=True)
                
                fig = px.bar(latest_polusi_sorted, y='nama_kota', x='index_kualitas_udara', orientation='h',
                           title=f'Index Kualitas Udara per Kota ({latest_year})',
                           labels={'nama_kota': 'Kota', 'index_kualitas_udara': 'Index Kualitas Udara'},
                           color='index_kualitas_udara', color_continuous_scale='Reds')
                fig.update_layout(height=max(400, len(latest_polusi_sorted) * 30))
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Data
        available_columns = {
            'nama_kota': 'Nama Kota', 'nama_negara': 'Nama Negara', 'tahun': 'Tahun',
            'index_kualitas_udara': 'Index Kualitas Udara', 'index_co2': 'Index CO2',
            'index_ozone': 'Index Ozone', 'index_no2': 'Index NO2', 'pm25': 'PM2.5'
        }
        default_cols = ['nama_kota', 'nama_negara', 'tahun', 'index_kualitas_udara', 'pm25']
        render_data_table(polusi_df, available_columns, default_cols, "polusi_columns")
    else:
        st.warning("Data polusi tidak tersedia untuk filter yang dipilih")

# ============================================
# HALAMAN KUALITAS HIDUP
# ============================================
elif menu == "Kualitas Hidup":
    st.title("Analisis Kualitas Hidup")
    
    # Filter
    selected_negara, selected_kota, negara_list, kota_list = render_filter("kualitas")
    
    # Ambil data
    kualitas_df = get_filtered_data(selected_negara, selected_kota, negara_list, kota_list, 'kualitas')
    
    if not kualitas_df.empty:
        st.markdown("---")
        
        # Metrics
        metrics_config = {
            'index_kualitas_hidup': 'Index Kualitas',
            'index_keamanan': 'Keamanan',
            'index_kesehatan': 'Kesehatan',
            'index_pendidikan': 'Pendidikan',
            'index_biaya_hidup': 'Biaya Hidup'
        }
        render_metrics(kualitas_df, metrics_config)
        
        st.markdown("---")
        
        # Visualisasi
        tab1, tab2, tab3 = st.tabs(["Trend Kualitas Hidup", "Breakdown Indikator", "Ranking Kota"])
        
        with tab1:
            st.subheader("Trend Index Kualitas Hidup")
            render_trend_chart(kualitas_df, 'index_kualitas_hidup', 'Trend Kualitas Hidup',
                             selected_kota, DatabaseConfig.COLORS['success'])
        
        with tab2:
            st.subheader("Breakdown Indikator Kualitas Hidup")
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].copy()
            
            if not latest_kualitas.empty:
                if len(latest_kualitas) > 10:
                    latest_kualitas = latest_kualitas.nlargest(10, 'index_kualitas_hidup')
                
                fig = go.Figure()
                for indicator in ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']:
                    fig.add_trace(go.Bar(
                        name=indicator.replace('index_', '').replace('_', ' ').title(),
                        x=latest_kualitas['nama_kota'],
                        y=latest_kualitas[indicator]
                    ))
                
                fig.update_layout(
                    title=f'Breakdown Indikator Kualitas Hidup ({latest_year})',
                    xaxis_title='Kota', yaxis_title='Nilai Index',
                    barmode='group', height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Ranking Kota Berdasarkan Kualitas Hidup")
            latest_year = kualitas_df['tahun'].max()
            latest_kualitas = kualitas_df[kualitas_df['tahun'] == latest_year].copy()
            
            if not latest_kualitas.empty:
                latest_kualitas_sorted = latest_kualitas.sort_values('index_kualitas_hidup', ascending=True)
                
                fig = px.bar(latest_kualitas_sorted, y='nama_kota', x='index_kualitas_hidup', orientation='h',
                           title=f'Ranking Kualitas Hidup per Kota ({latest_year})',
                           labels={'nama_kota': 'Kota', 'index_kualitas_hidup': 'Index Kualitas Hidup'},
                           color='index_kualitas_hidup', color_continuous_scale='Greens')
                fig.update_layout(height=max(400, len(latest_kualitas_sorted) * 30))
                st.plotly_chart(fig, use_container_width=True)
        
        # Tabel Data
        available_columns = {
            'nama_kota': 'Nama Kota', 'nama_negara': 'Nama Negara', 'tahun': 'Tahun',
            'index_kualitas_hidup': 'Index Kualitas Hidup', 'index_keamanan': 'Index Keamanan',
            'index_kesehatan': 'Index Kesehatan', 'index_pendidikan': 'Index Pendidikan',
            'index_biaya_hidup': 'Index Biaya Hidup'
        }
        default_cols = ['nama_kota', 'nama_negara', 'tahun', 'index_kualitas_hidup', 'index_keamanan']
        render_data_table(kualitas_df, available_columns, default_cols, "kualitas_columns")
    else:
        st.warning("Data kualitas hidup tidak tersedia untuk filter yang dipilih")

# ============================================
# HALAMAN PERBANDINGAN DATA
# ============================================
elif menu == "Perbandingan Data":
    st.title("Perbandingan Data Antar Kota")
    st.markdown("### Pilih Kota untuk Dibandingkan")
    
    kota_all = DatabaseConfig.get_all_kota()
    
    if not kota_all.empty:
        kota_all['display_name'] = kota_all['nama_kota'] + ' (' + kota_all['nama_negara'] + ')'
        
        col1, col2 = st.columns(2)
        with col1:
            kota1 = st.selectbox("Kota Pertama", options=kota_all['display_name'].tolist(), key='kota1')
            id_kota1 = kota_all[kota_all['display_name'] == kota1]['id_kota'].values[0]
        
        with col2:
            kota2 = st.selectbox("Kota Kedua", options=kota_all['display_name'].tolist(),
                               index=1 if len(kota_all) > 1 else 0, key='kota2')
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
            
            tab1, tab2, tab3 = st.tabs(["Perbandingan Polusi", "Perbandingan Kualitas Hidup", "Overview"])
            
            with tab1:
                st.subheader("Perbandingan Data Polusi")
                
                if not polusi1.empty and not polusi2.empty:
                    common_years = set(polusi1['tahun'].tolist()) & set(polusi2['tahun'].tolist())
                    
                    if common_years:
                        latest_year = max(common_years)
                        p1 = polusi1[polusi1['tahun'] == latest_year].iloc[0]
                        p2 = polusi2[polusi2['tahun'] == latest_year].iloc[0]
                        
                        # Metrics comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"#### {p1['nama_kota']}")
                            for metric, label in [('index_kualitas_udara', 'Index Kualitas Udara'), 
                                                 ('pm25', 'PM2.5'), ('index_co2', 'CO2'), ('index_no2', 'NO2')]:
                                st.metric(label, f"{p1[metric]:.1f}")
                        
                        with col2:
                            st.markdown(f"#### {p2['nama_kota']}")
                            for metric, label in [('index_kualitas_udara', 'Index Kualitas Udara'), 
                                                 ('pm25', 'PM2.5'), ('index_co2', 'CO2'), ('index_no2', 'NO2')]:
                                delta = p2[metric] - p1[metric]
                                st.metric(label, f"{p2[metric]:.1f}", delta=f"{delta:+.1f}", delta_color="inverse")
                        
                        st.markdown("---")
                        
                        # Comparison chart
                        fig = go.Figure(data=[
                            go.Bar(name=p1['nama_kota'], x=['Index Polusi', 'PM2.5', 'CO2', 'NO2'],
                                  y=[p1['index_kualitas_udara'], p1['pm25'], p1['index_co2'], p1['index_no2']]),
                            go.Bar(name=p2['nama_kota'], x=['Index Polusi', 'PM2.5', 'CO2', 'NO2'],
                                  y=[p2['index_kualitas_udara'], p2['pm25'], p2['index_co2'], p2['index_no2']])
                        ])
                        fig.update_layout(title=f'Perbandingan Indikator Polusi ({latest_year})',
                                        barmode='group', height=400)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Trend comparison
                        st.markdown("#### Trend Polusi dari Waktu ke Waktu")
                        combined_polusi = pd.concat([
                            polusi1.assign(kota=p1['nama_kota']),
                            polusi2.assign(kota=p2['nama_kota'])
                        ])
                        
                        fig = px.line(combined_polusi, x='tahun', y='index_kualitas_udara', color='kota', markers=True,
                                    labels={'tahun': 'Tahun', 'index_kualitas_udara': 'Index Kualitas Udara'})
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
                            for metric, label in [('index_kualitas_hidup', 'Index Kualitas Hidup'),
                                                 ('index_keamanan', 'Keamanan'), ('index_kesehatan', 'Kesehatan'),
                                                 ('index_pendidikan', 'Pendidikan'), ('index_biaya_hidup', 'Biaya Hidup')]:
                                st.metric(label, f"{k1[metric]:.1f}")
                        
                        with col2:
                            st.markdown(f"#### {k2['nama_kota']}")
                            for metric, label in [('index_kualitas_hidup', 'Index Kualitas Hidup'),
                                                 ('index_keamanan', 'Keamanan'), ('index_kesehatan', 'Kesehatan'),
                                                 ('index_pendidikan', 'Pendidikan'), ('index_biaya_hidup', 'Biaya Hidup')]:
                                delta = k2[metric] - k1[metric]
                                st.metric(label, f"{k2[metric]:.1f}", delta=f"{delta:+.1f}")
                        
                        st.markdown("---")
                        
                        # Radar chart comparison
                        fig = go.Figure()
                        indicators = ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']
                        labels = ['Keamanan', 'Kesehatan', 'Pendidikan', 'Biaya Hidup']
                        
                        fig.add_trace(go.Scatterpolar(r=[k1[ind] for ind in indicators], theta=labels,
                                                     fill='toself', name=k1['nama_kota']))
                        fig.add_trace(go.Scatterpolar(r=[k2[ind] for ind in indicators], theta=labels,
                                                     fill='toself', name=k2['nama_kota']))
                        
                        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                        title=f'Perbandingan Indikator Kualitas Hidup ({latest_year})', height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Trend comparison
                        st.markdown("#### Trend Kualitas Hidup dari Waktu ke Waktu")
                        combined_kualitas = pd.concat([
                            kualitas1.assign(kota=k1['nama_kota']),
                            kualitas2.assign(kota=k2['nama_kota'])
                        ])
                        
                        fig = px.line(combined_kualitas, x='tahun', y='index_kualitas_hidup', color='kota', markers=True,
                                    labels={'tahun': 'Tahun', 'index_kualitas_hidup': 'Index Kualitas Hidup'})
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Tidak ada data tahun yang sama untuk kedua kota")
                else:
                    st.warning("Data kualitas hidup tidak lengkap untuk perbandingan")
            
            with tab3:
                st.subheader("Overview Perbandingan")
                
                if not polusi1.empty and not polusi2.empty and not kualitas1.empty and not kualitas2.empty:
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
                            'Indikator': ['Index Polusi', 'PM2.5', 'CO2', 'Index Kualitas Hidup', 
                                        'Keamanan', 'Kesehatan', 'Pendidikan'],
                            k1['nama_kota']: [f"{p1['index_kualitas_udara']:.1f}", f"{p1['pm25']:.1f}", f"{p1['index_co2']:.1f}",
                                            f"{k1['index_kualitas_hidup']:.1f}", f"{k1['index_keamanan']:.1f}",
                                            f"{k1['index_kesehatan']:.1f}", f"{k1['index_pendidikan']:.1f}"],
                            k2['nama_kota']: [f"{p2['index_kualitas_udara']:.1f}", f"{p2['pm25']:.1f}", f"{p2['index_co2']:.1f}",
                                            f"{k2['index_kualitas_hidup']:.1f}", f"{k2['index_keamanan']:.1f}",
                                            f"{k2['index_kesehatan']:.1f}", f"{k2['index_pendidikan']:.1f}"],
                            'Selisih': [f"{(p2['index_kualitas_udara'] - p1['index_kualitas_udara']):.1f}",
                                      f"{(p2['pm25'] - p1['pm25']):.1f}", f"{(p2['index_co2'] - p1['index_co2']):.1f}",
                                      f"{(k2['index_kualitas_hidup'] - k1['index_kualitas_hidup']):.1f}",
                                      f"{(k2['index_keamanan'] - k1['index_keamanan']):.1f}",
                                      f"{(k2['index_kesehatan'] - k1['index_kesehatan']):.1f}",
                                      f"{(k2['index_pendidikan'] - k1['index_pendidikan']):.1f}"]
                        }
                        
                        df_comparison = pd.DataFrame(comparison_data)
                        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                        
                        st.markdown("---")
                        
                        # Summary insights
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### Ringkasan Polusi")
                            better_pollution = p1['nama_kota'] if p1['index_kualitas_udara'] < p2['index_kualitas_udara'] else p2['nama_kota']
                            st.success(f"{better_pollution} memiliki kualitas udara lebih baik")
                        
                        with col2:
                            st.markdown("#### Ringkasan Kualitas Hidup")
                            better_quality = k1['nama_kota'] if k1['index_kualitas_hidup'] > k2['index_kualitas_hidup'] else k2['nama_kota']
                            st.success(f"{better_quality} memiliki kualitas hidup lebih baik")
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