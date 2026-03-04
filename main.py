import streamlit as st  # Hata burasıydı, bu satır mutlaka en üstte olmalı!
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go

# Sayfa Ayarları
st.set_page_config(page_title="Kripto Sinyal Paneli", layout="wide")
st.title("🚀 Alpha Kripto Sinyal Merkezi")

# Veri Çekme Fonksiyonu
def get_data(symbol='BTC/USDT'):
    try:
        exchange = ccxt.binance()
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(bars, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return None

# Yan Panel
coin = st.sidebar.selectbox("Coin Seç", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
df = get_data(coin)

if df is not None:
    df['RSI'] = ta.rsi(df['close'], length=14)
    last_rsi = df['RSI'].iloc[-1]
    last_close = df['close'].iloc[-1]

    st.metric(f"{coin} Fiyat", f"{last_close} $", delta=f"RSI: {round(last_rsi, 2)}")

    if last_rsi < 35:
        st.success("🔥 AL SİNYALİ")
    elif last_rsi > 65:
        st.error("⚠️ SAT SİNYALİ")
    else:
        st.info("⚖️ NÖTR")

    fig = go.Figure(data=[go.Candlestick(x=df['ts'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.update_layout(template="dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
