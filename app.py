import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_KEY = '0K46WI6OG3S5D4KO'

# === Get Full Stock History ===
def get_stock_data(symbol='AAPL'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}'
    r = requests.get(url).json()
    data = r.get('Time Series (Daily)', {})
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data).T
    df.index = pd.to_datetime(df.index)
    df = df.rename(columns={'4. close': 'close'})
    df['close'] = df['close'].astype(float)
    df = df.sort_index()
    return df

# === Streamlit UI ===
st.title("Elliott Wave Pattern Visualizer (HKCM Style)")
symbol = st.text_input("Enter Stock Symbol", value='AAPL')

df = get_stock_data(symbol)

if not df.empty:
    fig = go.Figure()

    # === Plot price ===
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price'))

    # === Simulated Elliott Wave Boxes (manually defined) ===
    # You'll adjust these indices based on real swing highs/lows for now
    wave_boxes = {
        "Wave 1": (100, 140),
        "Wave 2": (141, 170),
        "Wave 3": (171, 220),
        "Wave 4": (221, 250),
        "Wave 5": (251, 290)
    }

    colors = ['LightGreen', 'LightCoral', 'LightBlue', 'Khaki', 'Thistle']
    for i, (label, (start_idx, end_idx)) in enumerate(wave_boxes.items()):
        if end_idx < len(df):
            start_date = df.index[start_idx]
            end_date = df.index[end_idx]
            low = df['close'].iloc[start_idx:end_idx].min()
            high = df['close'].iloc[start_idx:end_idx].max()
            fig.add_shape(type='rect',
                          x0=start_date, x1=end_date,
                          y0=low, y1=high,
                          fillcolor=colors[i % len(colors)],
                          opacity=0.3, line_width=0)
            fig.add_annotation(text=label, x=start_date, y=high, showarrow=False, font=dict(size=12, color="black"))

    fig.update_layout(title=f"{symbol} - Elliott Wave Zones",
                      xaxis_title="Date", yaxis_title="Price",
                      showlegend=False)
    st.plotly_chart(fig)

else:
    st.error("Could not retrieve data. Try a different symbol or wait a bit.") 
