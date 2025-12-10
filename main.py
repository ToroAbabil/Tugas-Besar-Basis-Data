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
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;}
    .stTabs [data-baseweb="tab-list"] {gap: 24px;}
    .stTabs [data-baseweb="tab"] {height: 50px; padding: 10px 20px;}
</style>
""", unsafe_allow_html=True)

# ============================================
# HELPER FUNCTIONS
# ============================================

def render_filter(key_prefix):
    """Render filter negara dan kota"""
    col1, col2 = st.columns(2)
    
    with col1:
        negara_list = DatabaseConfig.get_negara_list()
        negara_options = ['Semua Negara'] + negara_list['nama_negara'].tolist()
        selected_negara = st.selectbox("Pilih Negara", negara_options, key=f"{key_prefix}_negara")
    
    with col2:
        if selected_negara != 'Semua Negara':
            kode_negara = negara_list[negara_list['nama_negara'] == selected_negara]['kode_negara'].values[0]
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
        kode_negara = negara_list[negara_list['nama_negara'] == selected_negara]['kode_negara'].values[0]
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
            st.metric(label, f"{latest_data[col_name].mean():.1f}")

def render_trend_chart(df, y_col, title, selected_kota, color):
    """Render chart trend"""
    if selected_kota != 'Semua Kota':
        fig = px.line(df, x='tahun', y=y_col, title=f'{title} - {selected_kota}', 
                     labels={'tahun': 'Tahun', y_col: title}, markers=True)
        fig.update_traces(line_color=color)
    else:
        fig = px.line(df, x='tahun', y=y_col, color='nama_kota', title=f'{title} per Kota',
                     labels={'tahun': 'Tahun', y_col: title}, markers=True, 
                     color_discrete_sequence=DatabaseConfig.COLOR_PALETTE)
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_comparison_bar(df, indicators, labels_map, title):
    """Render grouped bar chart untuk perbandingan indikator"""
    fig = go.Figure()
    for indicator in indicators:
        fig.add_trace(go.Bar(
            name=labels_map.get(indicator, indicator).upper(),
            x=df['nama_kota'], y=df[indicator]
        ))
    fig.update_layout(title=title, xaxis_title='Kota', yaxis_title='Nilai Index', 
                     barmode='group', height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_horizontal_bar(df, x_col, title, color_scale):
    """Render horizontal bar chart"""
    df_sorted = df.sort_values(x_col, ascending=True)
    fig = px.bar(df_sorted, y='nama_kota', x=x_col, orientation='h', title=title,
               labels={'nama_kota': 'Kota', x_col: title.split('per')[0].strip()},
               color=x_col, color_continuous_scale=color_scale)
    fig.update_layout(height=max(400, len(df_sorted) * 30))
    st.plotly_chart(fig, use_container_width=True)

def render_data_table(df, available_columns, default_cols, key):
    """Render tabel data dengan pemilihan kolom"""
    st.markdown("---")
    st.subheader("Data Detail")
    selected_columns = st.multiselect("Pilih kolom yang ingin ditampilkan:",
        options=list(available_columns.keys()), default=default_cols,
        format_func=lambda x: available_columns[x], key=key)
    
    if selected_columns:
        display_df = df[selected_columns].sort_values('tahun', ascending=False) if 'tahun' in selected_columns else df[selected_columns]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption(f"Menampilkan {len(display_df)} baris data")
    else:
        st.warning("Pilih minimal satu kolom untuk ditampilkan")

def render_comparison_metrics(data, metrics_list, col_name):
    """Render metrics untuk perbandingan 2 kota"""
    st.markdown(f"#### {data['nama_kota']}")
    for metric, label in metrics_list:
        st.metric(label, f"{data[metric]:.1f}")

def render_comparison_tab(df1, df2, data_type='polusi'):
    """Render tab perbandingan (polusi atau kualitas hidup)"""
    if df1.empty or df2.empty:
        st.warning(f"Data {data_type} tidak lengkap untuk perbandingan")
        return
    
    common_years = set(df1['tahun'].tolist()) & set(df2['tahun'].tolist())
    if not common_years:
        st.warning("Tidak ada data tahun yang sama untuk kedua kota")
        return
    
    latest_year = max(common_years)
    d1 = df1[df1['tahun'] == latest_year].iloc[0]
    d2 = df2[df2['tahun'] == latest_year].iloc[0]
    
    # Metrics
    col1, col2 = st.columns(2)
    
    if data_type == 'polusi':
        metrics = [('index_kualitas_udara', 'Index Kualitas Udara'), ('pm25', 'PM2.5'), 
                  ('index_co2', 'CO2'), ('index_no2', 'NO2')]
        chart_data = [d1['index_kualitas_udara'], d1['pm25'], d1['index_co2'], d1['index_no2']]
        chart_data2 = [d2['index_kualitas_udara'], d2['pm25'], d2['index_co2'], d2['index_no2']]
        chart_labels = ['Index Polusi', 'PM2.5', 'CO2', 'NO2']
        y_col = 'index_kualitas_udara'
    else:
        metrics = [('index_kualitas_hidup', 'Index Kualitas Hidup'), ('index_keamanan', 'Keamanan'),
                  ('index_kesehatan', 'Kesehatan'), ('index_pendidikan', 'Pendidikan'), 
                  ('index_biaya_hidup', 'Biaya Hidup')]
        indicators = ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']
        y_col = 'index_kualitas_hidup'
    
    with col1:
        render_comparison_metrics(d1, metrics, 'col1')
    
    with col2:
        render_comparison_metrics(d2, metrics, 'col2')
        # Add delta untuk col2
        for i, (metric, label) in enumerate(metrics):
            delta = d2[metric] - d1[metric]
    
    st.markdown("---")
    
    # Chart perbandingan
    if data_type == 'polusi':
        fig = go.Figure(data=[
            go.Bar(name=d1['nama_kota'], x=chart_labels, y=chart_data),
            go.Bar(name=d2['nama_kota'], x=chart_labels, y=chart_data2)
        ])
        fig.update_layout(title=f'Perbandingan Indikator Polusi ({latest_year})', 
                         barmode='group', height=400)
    else:
        # Radar chart untuk kualitas hidup
        fig = go.Figure()
        labels_radar = ['Keamanan', 'Kesehatan', 'Pendidikan', 'Biaya Hidup']
        fig.add_trace(go.Scatterpolar(r=[d1[ind] for ind in indicators], theta=labels_radar,
                                     fill='toself', name=d1['nama_kota']))
        fig.add_trace(go.Scatterpolar(r=[d2[ind] for ind in indicators], theta=labels_radar,
                                     fill='toself', name=d2['nama_kota']))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        title=f'Perbandingan Indikator Kualitas Hidup ({latest_year})', height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend comparison
    st.markdown(f"#### Trend {data_type.title()} dari Waktu ke Waktu")
    combined = pd.concat([df1.assign(kota=d1['nama_kota']), df2.assign(kota=d2['nama_kota'])])
    fig = px.line(combined, x='tahun', y=y_col, color='kota', markers=True,
                labels={'tahun': 'Tahun', y_col: y_col.replace('_', ' ').title()})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# SIDEBAR NAVIGATION
# ============================================
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
    
    for col, (title, df_func, y_col, scale, is_largest) in [
        (col1, ("Data Polusi Terkini", DatabaseConfig.get_polusi_data, 'index_kualitas_udara', 'Reds', True)),
        (col2, ("Data Kualitas Hidup Terkini", DatabaseConfig.get_kualitas_hidup_data, 'index_kualitas_hidup', 'Greens', True))
    ]:
        with col:
            st.markdown(f"### {title}")
            df = df_func()
            if not df.empty:
                latest_year = df['tahun'].max()
                latest_df = df[df['tahun'] == latest_year].nlargest(5, y_col) if is_largest else df[df['tahun'] == latest_year].nsmallest(5, y_col)
                
                fig = px.bar(latest_df, x='nama_kota', y=y_col,
                           title=f'5 Kota {"Tertinggi" if "Polusi" in title else "Terbaik"} ({latest_year})',
                           labels={'nama_kota': 'Kota', y_col: y_col.replace('_', ' ').title()},
                           color=y_col, color_continuous_scale=scale)
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Data {title.lower()} tidak tersedia")
    
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
# HALAMAN POLUSI & KUALITAS HIDUP (GENERIC)
# ============================================
elif menu in ["Polusi Udara", "Kualitas Hidup"]:
    data_type = 'polusi' if menu == "Polusi Udara" else 'kualitas'
    is_polusi = data_type == 'polusi'
    
    st.title(f"Analisis Data {menu}")
    
    selected_negara, selected_kota, negara_list, kota_list = render_filter(data_type)
    df = get_filtered_data(selected_negara, selected_kota, negara_list, kota_list, data_type)
    
    if not df.empty:
        st.markdown("---")
        
        # Metrics configuration
        if is_polusi:
            metrics_config = {'index_kualitas_udara': 'Rata-rata Index Polusi', 'pm25': 'Rata-rata PM2.5',
                            'index_co2': 'Rata-rata CO2', 'index_no2': 'Rata-rata NO2'}
            indicators = ['index_co2', 'index_ozone', 'index_no2', 'pm25']
            labels_map = {'index_co2': 'CO2', 'index_ozone': 'Ozone', 'index_no2': 'NO2', 'pm25': 'PM2.5'}
            main_col = 'index_kualitas_udara'
            color = DatabaseConfig.COLORS['danger']
            color_scale = 'Reds'
            available_columns = {'nama_kota': 'Nama Kota', 'nama_negara': 'Nama Negara', 'tahun': 'Tahun',
                               'index_kualitas_udara': 'Index Kualitas Udara', 'index_co2': 'Index CO2',
                               'index_ozone': 'Index Ozone', 'index_no2': 'Index NO2', 'pm25': 'PM2.5'}
            default_cols = ['nama_kota', 'nama_negara', 'tahun', 'index_kualitas_udara', 'pm25']
        else:
            metrics_config = {'index_kualitas_hidup': 'Index Kualitas', 'index_keamanan': 'Keamanan',
                            'index_kesehatan': 'Kesehatan', 'index_pendidikan': 'Pendidikan',
                            'index_biaya_hidup': 'Biaya Hidup'}
            indicators = ['index_keamanan', 'index_kesehatan', 'index_pendidikan', 'index_biaya_hidup']
            labels_map = {k: k.replace('index_', '').replace('_', ' ').title() for k in indicators}
            main_col = 'index_kualitas_hidup'
            color = DatabaseConfig.COLORS['success']
            color_scale = 'Greens'
            available_columns = {'nama_kota': 'Nama Kota', 'nama_negara': 'Nama Negara', 'tahun': 'Tahun',
                               'index_kualitas_hidup': 'Index Kualitas Hidup', 'index_keamanan': 'Index Keamanan',
                               'index_kesehatan': 'Index Kesehatan', 'index_pendidikan': 'Index Pendidikan',
                               'index_biaya_hidup': 'Index Biaya Hidup'}
            default_cols = ['nama_kota', 'nama_negara', 'tahun', 'index_kualitas_hidup', 'index_keamanan']
        
        render_metrics(df, metrics_config)
        st.markdown("---")
        
        # Visualisasi
        tab1, tab2, tab3 = st.tabs([f"Trend {menu.split()[0]}", "Perbandingan Indikator", "Perbandingan Kota"])
        
        with tab1:
            st.subheader(f"Trend {main_col.replace('_', ' ').title()}")
            render_trend_chart(df, main_col, f'Trend {menu.split()[0]}', selected_kota, color)
        
        with tab2:
            st.subheader(f"Perbandingan Indikator {menu.split()[0]}")
            latest_year = df['tahun'].max()
            latest_df = df[df['tahun'] == latest_year].copy()
            if not latest_df.empty:
                if len(latest_df) > 10:
                    latest_df = latest_df.nlargest(10, main_col)
                render_comparison_bar(latest_df, indicators, labels_map, 
                                    f'Perbandingan Indikator {menu.split()[0]} ({latest_year})')
        
        with tab3:
            st.subheader(f"Perbandingan {menu.split()[0]} Antar Kota")
            latest_year = df['tahun'].max()
            latest_df = df[df['tahun'] == latest_year].copy()
            if not latest_df.empty:
                render_horizontal_bar(latest_df, main_col, 
                                    f'{main_col.replace("_", " ").title()} per Kota ({latest_year})',
                                    color_scale)
        
        render_data_table(df, available_columns, default_cols, f"{data_type}_columns")
    else:
        st.warning(f"Data {data_type} tidak tersedia untuk filter yang dipilih")

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
            
            # Ambil data
            polusi1 = DatabaseConfig.get_polusi_data(id_kota=id_kota1)
            polusi2 = DatabaseConfig.get_polusi_data(id_kota=id_kota2)
            kualitas1 = DatabaseConfig.get_kualitas_hidup_data(id_kota=id_kota1)
            kualitas2 = DatabaseConfig.get_kualitas_hidup_data(id_kota=id_kota2)
            
            tab1, tab2, tab3 = st.tabs(["Perbandingan Polusi", "Perbandingan Kualitas Hidup", "Overview"])
            
            with tab1:
                st.subheader("Perbandingan Data Polusi")
                render_comparison_tab(polusi1, polusi2, 'polusi')
            
            with tab2:
                st.subheader("Perbandingan Kualitas Hidup")
                render_comparison_tab(kualitas1, kualitas2, 'kualitas')
            
            with tab3:
                st.subheader("Overview Perbandingan")
                try:
                    if not any([polusi1.empty, polusi2.empty, kualitas1.empty, kualitas2.empty]):
                        all_years = (set(polusi1['tahun'].tolist()) & set(polusi2['tahun'].tolist()) &
                                    set(kualitas1['tahun'].tolist()) & set(kualitas2['tahun'].tolist()))
                        
                        if all_years:
                            latest_year = max(all_years)
                            p1, p2 = polusi1[polusi1['tahun'] == latest_year].iloc[0], polusi2[polusi2['tahun'] == latest_year].iloc[0]
                            k1, k2 = kualitas1[kualitas1['tahun'] == latest_year].iloc[0], kualitas2[kualitas2['tahun'] == latest_year].iloc[0]
                            
                            comparison_data = {
                                'Indikator': ['Index Polusi', 'PM2.5', 'CO2', 'Index Kualitas Hidup', 'Keamanan', 'Kesehatan', 'Pendidikan'],
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
                            
                            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
                            st.markdown("---")
                            
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
                except Exception as e:
                    st.error(f"Terjadi error: {str(e)}")
    else:
        st.error("Data kota tidak tersedia")

# Footer
st.markdown("---")
st.markdown('<div style="text-align: center; color: gray;"><p>Dashboard Polusi dan Kualitas Hidup | Kelompok 9</p></div>', 
           unsafe_allow_html=True)