import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta

# Sayfa Ayarları
st.set_page_config(page_title="Alpha Pro: Kesin Çözüm", layout="wide")
st.title("🎯 Alpha Pro: Profesyonel İşlem Terminali")

# Veri Çekme Fonksiyonu
def get_data(symbol='BTC/USDT'):
    try:
        exchange = ccxt.kraken()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=150)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        return df
    except:
        return None

# Sidebar
coin = st.sidebar.selectbox("Coin Seçin", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
df = get_data(coin)

if df is not None:
    # --- TEKNİK ANALİZ ---
    df['SMA20'] = ta.sma(df['close'], length=20)
    df['SMA50'] = ta.sma(df['close'], length=50)
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    last_price = df['close'].iloc[-1]
    last_atr = df['ATR'].iloc[-1]
    
    # --- RİSK YÖNETİMİ HESABI ---
    stop_loss = last_price - (last_atr * 1.5)
    take_profit = last_price + (last_atr * 3)
    
    # --- ÖZET PANELİ ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Giriş (Anlık)", f"{last_price:,} $")
    c2.metric("Zarar Kes (SL)", f"{round(stop_loss, 2):,} $", delta_color="inverse")
    c3.metric("Kâr Al (TP)", f"{round(take_profit, 2):,}")

    # --- SİNYAL DURUMU ---
    score = 0
    if df['RSI'].iloc[-1] < 50: score += 1
    if last_price > df['SMA20'].iloc[-1]: score += 1
    if last_price > df['SMA50'].iloc[-1]: score += 1
    if df['close'].iloc[-1] > df['close'].iloc[-2]: score += 1

    if score >= 3:
        st.success(f"✅ GÜÇLÜ AL SİNYALİ (Puan: {score}/4)")
    elif score <= 1:
        st.error(f"❌ DİKKAT: SATIŞ BASKISI (Puan: {score}/4)")
    else:
        st.info(f"⚖️ NÖTR: BEKLEMEDE KAL (Puan: {score}/4)")

    # --- HATA VERMEYEN YENİ GRAFİK SİSTEMİ ---
    st.subheader("📈 Trend ve Hareketli Ortalamalar")
    # Sadece fiyat ve ortalamaları içeren sade bir veri seti
    chart_data = df.set_index('ts')[['close', 'SMA20', 'SMA50']]
    st.line_chart(chart_data)

    # --- SEVİYE TABLOSU ---
    st.subheader("📋 İşlem Detayları")
    seviyeler = {
        "Açıklama": ["Anlık Fiyat", "Güvenli Stop Seviyesi", "Hedef Fiyat (1:2 R/R)", "Piyasa Oynaklığı (ATR)"],
        "Değer ($)": [f"{last_price:,}", f"{round(stop_loss, 2):,}", f"{round(take_profit, 2):,}", f"{round(last_atr, 2)}"]
    }
    st.table(pd.DataFrame(seviyeler))

    st.write("🔄 *Not: Sayfa her yenilendiğinde veriler güncellenir.*")
