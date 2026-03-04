import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

st.set_page_config(page_title="Alpha Pro: İşlem Asistanı", layout="wide")
st.title("🎯 Alpha Pro: Giriş - Çıkış & Risk Yönetimi")

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
    # --- İNDİKATÖRLER ---
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['SMA20'] = ta.sma(df['close'], length=20)
    df['SMA50'] = ta.sma(df['close'], length=50)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    last_price = df['close'].iloc[-1]
    last_atr = df['ATR'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # --- RİSK YÖNETİMİ HESABI (ATR TABANLI) ---
    # Alış için: Stop = Fiyat - (1.5 * ATR), Kar = Fiyat + (3 * ATR) -> 1:2 Oranı
    stop_loss = last_price - (last_atr * 1.5)
    take_profit = last_price + (last_atr * 3)
    
    # --- PANEL TASARIMI ---
    st.subheader("📊 Canlı İşlem Stratejisi")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Giriş (Buy)", f"{last_price:,} $")
    c2.metric("Stop-Loss (SL)", f"{round(stop_loss, 2)} $", delta="-Risk", delta_color="inverse")
    c3.metric("Take-Profit (TP)", f"{round(take_profit, 2)} $", delta="+Hedef")
    c4.metric("R/R Oranı", "1 : 2")

    # --- SİNYAL PUANLAMA ---
    score = 0
    if last_rsi < 45: score += 1
    if last_price > df['SMA20'].iloc[-1]: score += 1
    if last_price > df['SMA50'].iloc[-1]: score += 1
    if df['close'].iloc[-1] > df['close'].iloc[-2]: score += 1

    if score >= 3:
        st.success(f"✅ İŞLEME GİRİLEBİLİR (Puan: {score}/4) - Yön Yukarı!")
    elif score <= 1:
        st.error(f"❌ İŞLEMDEN KAÇIN (Puan: {score}/4) - Satış Baskısı!")
    else:
        st.info(f"⚖️ BEKLEMEDE KAL (Puan: {score}/4) - Kararsız Piyasa.")

    # --- GRAFİK ---
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['ts'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name="Fiyat"))
    
    # SL ve TP Çizgileri
    fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", annotation_text="STOP (Zarar Kes)")
    fig.add_hline(y=take_profit, line_dash="dash", line_color="green", annotation_text="HEDEF (Kâr Al)")
    
# Grafik Ayarları (En Güvenli ve Sade Versiyon)
    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        showlegend=True
    )

    # İşlem Seviyelerini Grafiğe Ekle
    fig.add_hline(y=stop_loss, line_dash="dash", line_color="red", 
                 annotation_text=f"STOP: {round(stop_loss, 1)}", annotation_position="bottom left")
    fig.add_hline(y=take_profit, line_dash="dash", line_color="green", 
                 annotation_text=f"HEDEF: {round(take_profit, 1)}", annotation_position="top left")
    fig.add_hline(y=last_price, line_dash="dot", line_color="blue", 
                 annotation_text="GİRİŞ", annotation_position="right")

    # Grafiği Ekrana Bas
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"💡 Strateji Notu: Şu anki piyasa oynaklığına (ATR) göre risk mesafeniz {round(last_atr * 1.5, 2)} $ olarak hesaplanmıştır.")
