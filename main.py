import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Dashboard Forecast Nilai Tukar", layout="wide")

# ======================
# LOAD & PREPROCESSING DATA 
# ======================
kurs = pd.read_csv("Data_Historis_USD_IDR_2019.csv")
minyak = pd.read_csv("Data_Historis_Minyak_2019.csv")
forecast = pd.read_csv("hasil_forecast_arimax_fix.csv")

# bersihin nama kolom 
kurs.columns = kurs.columns.str.strip()
minyak.columns = minyak.columns.str.strip()
forecast.columns = forecast.columns.str.strip()

# convert tanggal
kurs['Tanggal'] = pd.to_datetime(kurs['Tanggal'])
minyak['Date'] = pd.to_datetime(minyak['Date'])
forecast['Tanggal'] = pd.to_datetime(forecast['Tanggal'])

# rename kolom
minyak = minyak.rename(columns={'Date': 'Tanggal', 'Price': 'Harga'})

# ubah ke numerik
kurs['Terakhir'] = kurs['Terakhir'].astype(str).str.replace(',', '').astype(float)
minyak['Harga'] = minyak['Harga'].astype(str).str.replace(',', '').astype(float)

# sorting + index
kurs = kurs.sort_values("Tanggal").set_index("Tanggal")
minyak = minyak.sort_values("Tanggal").set_index("Tanggal")
forecast = forecast.sort_values("Tanggal").set_index("Tanggal")

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "Nilai Tukar Rupiah", "Harga Minyak Mentah", "Forecast", "Evaluasi"],
        icons=["house", "currency-exchange", "fuel-pump", "graph-up-arrow", "clipboard-data"],
        default_index=0,
    )

# ======================
# HOME
# ======================
if selected == "Home":
    st.write("##")
    st.markdown("""
        <h1 style='text-align: center; font-size: 50px;'>
        Peramalan Nilai Tukar IDR-USD,<br>Oktober - Desember 2025
        </h1>
        <p style='text-align: center; font-size: 18px; color: #666;'>
        Dashboard ini digunakan untuk melakukan peramalan nilai tukar Rupiah terhadap USD 
        menggunakan model ARIMAX dengan variabel eksternal harga minyak mentah dunia.
        </p>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Tentang Proyek")
    st.write("""
    Dashboard ini membantu analisis pergerakan nilai tukar serta memberikan hasil peramalan 
    yang dapat digunakan sebagai dasar pengambilan keputusan, khususnya dalam menghadapi 
    risiko fluktuasi nilai tukar.
    """)

# ======================
# NILAI TUKAR
# ======================
elif selected == "Nilai Tukar Rupiah":
    st.subheader("Grafik Nilai Tukar Rupiah")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=kurs.index,
        y=kurs['Terakhir'],
        mode='lines',
        name='Nilai Tukar',
        line=dict(width=2)
    ))

    # hitung range otomatis (biar nggak flat)
    y_min = kurs['Terakhir'].min()
    y_max = kurs['Terakhir'].max()
    padding = (y_max - y_min) * 0.2  # 20% biar lebih lega

    fig.update_layout(
        title="Pergerakan Nilai Tukar Rupiah",
        template="plotly_white",
        yaxis=dict(range=[y_min - padding, y_max + padding]),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================
# MINYAK
# ======================
elif selected == "Harga Minyak Mentah":
    st.subheader("Grafik Harga Minyak Mentah")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=minyak.index,
        y=minyak['Harga'],
        mode='lines',
        name='Harga Minyak',
        line=dict(color='orange')
    ))

    fig.update_layout(
        title="Pergerakan Harga Minyak Mentah Dunia",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

# ======================
# FORECAST
# ======================
elif selected == "Forecast":
    st.subheader("Visualisasi Forecast Harian per Minggu")

    df_weekly = forecast.copy()
    df_weekly['Month'] = df_weekly.index.strftime('%B')

    def get_week_of_month(date):
        first_day = date.replace(day=1)
        dom = date.day
        adjusted_dom = dom + first_day.weekday()
        return int((adjusted_dom - 1) / 7) + 1

    df_weekly['Week_Num'] = [get_week_of_month(d) for d in df_weekly.index]
    df_weekly['Label'] = df_weekly['Month'] + " Minggu ke-" + df_weekly['Week_Num'].astype(str)

    selected_week = st.selectbox("Pilih Periode Mingguan:", df_weekly['Label'].unique())
    filtered_df = df_weekly[df_weekly['Label'] == selected_week]

    # Grafik forecast harian
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=filtered_df.index.strftime('%d %b'),
        y=filtered_df['Forecast_ARIMAX'],
        mode='lines+markers',
        name='Forecast'
    ))

    fig1.update_layout(
        title=f"Tren Forecast: {selected_week}",
        template="plotly_white"
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # Perbandingan actual vs forecast
    st.subheader("Perbandingan Actual vs Forecast")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast['Actual'],
        name='Actual'
    ))
    fig2.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast['Forecast_ARIMAX'],
        name='Forecast',
        line=dict(dash='dash')
    ))

    fig2.update_layout(template="plotly_white")

    st.plotly_chart(fig2, use_container_width=True)

    # tabel
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Data Aktual")
        st.dataframe(forecast[['Actual']], use_container_width=True)

    with col2:
        st.subheader("Data Forecast")
        st.dataframe(forecast[['Forecast_ARIMAX']], use_container_width=True)

# ======================
# EVALUASI
# ======================
elif selected == "Evaluasi":
    st.subheader("Evaluasi Model")

    rmse = ((forecast['Actual'] - forecast['Forecast_ARIMAX'])**2).mean()**0.5
    mape = (abs((forecast['Actual'] - forecast['Forecast_ARIMAX']) / forecast['Actual']).mean()) * 100

    col1, col2 = st.columns(2)
    col1.metric("RMSE", f"{rmse:.2f}")
    col2.metric("MAPE", f"{mape:.2f}%")

    st.markdown("---")

    st.write("""
    RMSE menunjukkan rata-rata error dalam satuan rupiah, sedangkan MAPE menunjukkan 
    error dalam bentuk persentase. Semakin kecil nilainya, maka model semakin baik 
    dalam melakukan peramalan.
    """)