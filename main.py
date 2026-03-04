import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Pro Kripto Sinyal Analiz", layout="wide")
st.title("🛡️ Alpha Pro: Çoklu Gösterge & Seviye Analizi")

def get_data(symbol='BTC/USDT'):
    try:
        exchange = ccxt.kraken()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=150)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Veri hatası: {e}")
        return None

coin = st.sidebar.selectbox("Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
df = get_data(coin)

if df is not None:
    # 1. RSI
    df['RSI'] = ta.rsi(df['close'], length=14)
    # 2. MACD
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)
    # 3. Hareketli Ortalamalar (SMA 20 & 50)
    df['SMA20'] = ta.sma(df['close'], length=20)
    df['SMA50'] = ta.sma(df['close'], length=50)
    # 4. Bollinger Bantları
    bbands = ta.bbands(df['close'], length=20)
    df = pd.concat([df, bbands], axis=1)
    
    # 5. Destek ve Direnç Hesaplama (Son 100 Mum)
    support = df['low'].tail(100).min()
    resistance = df['high'].tail(100).max()

    last_price = df['close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # --- PANEL TASARIMI ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Anlık Fiyat", f"{last_price} $")
    col2.metric("Destek Seviyesi", f"{support} $")
    col3.metric("Direnç Seviyesi", f"{resistance} $")

    # --- GELİŞMİŞ SİNYAL MANTIĞI ---
    score = 0
    if last_rsi < 40: score += 1  # RSI Alış yönlü
    if last_price > df['SMA20'].iloc[-1]: score += 1 # Trend Üstü
    if df['MACD_12_26_9'].iloc[-1] > df['MACDs_12_26_9'].iloc[-1]: score += 1 # MACD Kesişimi
    if last_price < support * 1.02: score += 1 # Desteğe Yakın

    st.subheader("📊 Strateji Analiz Raporu")
    if score >= 3:
        st.success(f"🚀 GÜÇLÜ AL SİNYALİ (Puan: {score}/4) - Trend ve Göstergeler Pozitif!")
    elif score <= 1:
        st.error(f"⚠️ DİKKAT: SATIŞ BASKISI (Puan: {score}/4) - Göstergeler Zayıf!")
    else:
        st.info(f"⚖️ NÖTR / BEKLE (Puan: {score}/4) - Net Bir Trend Oluşmadı.")

    # --- PROFESYONEL GRAFİK ---
    fig = go.Figure()
    # Mumlar
    fig.add_trace(go.Candlestick(x=df['ts'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Fiyat"))
    # Ortalamalar
    fig.add_trace(go.Scatter(x=df['ts'], y=df['SMA20'], line=dict(color='orange', width=1), name="SMA 20"))
    fig.add_trace(go.Scatter(x=df['ts'], y=df['SMA50'], line=dict(color='blue', width=1), name="SMA 50"))
    # Destek/Direnç Çizgileri
    fig.add_hline(y=support, line_dash="dash", line_color="green", annotation_text="Güçlü Destek")
    fig.add_hline(y=resistance, line_dash="dash", line_color="red", annotation_text="Güçlü Direnç")

   # Grafik Ayarlarını Güncelle (Hatasız Versiyon)
    fig.update_layout(
        template="dark",
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    # Izgara çizgilerini kapatarak daha sade bir görünüm sağlıyoruz
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)
    
