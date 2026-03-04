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
        # Kraken borsasından veri çekiyoruz
        exchange = ccxt.kraken()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=150)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

# Yan Menü (Coin Seçimi)
coin = st.sidebar.selectbox("İşlem Yapılacak Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
df = get_data(coin)

if df is not None:
    # --- TEKNİK ANALİZ HESAPLAMALARI ---
    df['SMA20'] = ta.sma(df['close'], length=20)
    df['SMA50'] = ta.sma(df['close'], length=50)
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    last_price = df['close'].iloc[-1]
    last_atr = df['ATR'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # --- ATR TABANLI RİSK YÖNETİMİ ---
    # Alış için: Stop = Fiyat - (1.5 * ATR), Kar = Fiyat + (3 * ATR)
    stop_loss = last_price - (last_atr * 1.5)
    take_profit = last_price + (last_atr * 3)
    
    # --- ÜST PANEL (METRİKLER) ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Giriş (Anlık)", f"{last_price:,} $")
    c2.metric("Zarar Kes (Stop-Loss)", f"{round(stop_loss, 2):,} $", delta="-Risk", delta_color="inverse")
    c3.metric("Kâr Al (Take-Profit)", f"{round(take_profit, 2):,} $", delta="+Hedef")

    # --- SİNYAL PUANLAMA ---
    score = 0
    if last_rsi < 50: score += 1
    if last_price > df['SMA20'].iloc[-1]: score += 1
    if last_price > df['SMA50'].iloc[-1]: score += 1
    if df['close'].iloc[-1] > df['close'].iloc[-2]: score += 1

    if score >= 3:
        st.success(f"✅ GÜÇLÜ AL SİNYALİ (Puan: {score}/4)")
    elif score <= 1:
        st.error(f"❌ DİKKAT: SATIŞ BASKISI (Puan: {score}/4)")
    else:
        st.info(f"⚖️ NÖTR: BEKLEMEDE KAL (Puan: {score}/4)")

    # --- HATA VERMEYEN STABIL GRAFİK ---
    st.subheader("📈 Fiyat Trendi ve Hareketli Ortalamalar")
    chart_data = df.set_index('ts')[['close', 'SMA20', 'SMA50']]
    st.line_chart(chart_data)

    # --- DETAYLI TABLO ---
    st.subheader("📋 İşlem Seviyeleri ve Teknik Özet")
    ozet_data = {
        "Parametre": ["Anlık Fiyat", "Zarar Kes (SL)", "Hedef Fiyat (TP)", "RSI Değeri", "Piyasa Oynaklığı (ATR)"],
        "Değer": [f"{last_price:,}", f"{round(stop_loss, 2):,}", f"{round(take_profit, 2):,}", f"{round(last_rsi, 2)}", f"{round(last_atr, 2)}"]
    }
    st.table(pd.DataFrame(ozet_data))

    st.caption("Not: Veriler Kraken üzerinden 1 saatlik periyotla çekilmektedir. Yatırım tavsiyesi değildir.")
