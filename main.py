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

# Yan Panel (Sidebar)
coin = st.sidebar.selectbox("Takip Edilecek Coin", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
df = get_data(coin)

if df is not None:
    # İndikatörler (Teknik Analiz)
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA20'] = ta.ema(df['close'], length=20)
    last_rsi = df['RSI'].iloc[-1]
    last_close = df['close'].iloc[-1]

    # Sinyal Alanı
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Güncel Fiyat", f"{last_close} $")
    with col2:
        st.metric("RSI Değeri", round(last_rsi, 2))

    if last_rsi < 30:
        st.success("🔥 GÜÇLÜ AL SİNYALİ (Aşırı Satım Bölgesi)")
    elif last_rsi > 70:
        st.error("⚠️ SATIŞ BASKISI (Aşırı Alım Bölgesi)")
    else:
        st.info("⚖️ NÖTR - Beklemede")

    # Grafik (TradingView Tarzı)
    fig = go.Figure(data=[go.Candlestick(x=df['ts'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.update_layout(template="dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.write("---")
st.caption("Not: Bu veriler yatırım tavsiyesi değildir.")
