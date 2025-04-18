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

# === Detect Swings ===
def find_swings(prices, window=1):
    swings = []
    for i in range(window, len(prices) - window):
        is_high = all(prices[i] > prices[i - j] and prices[i] > prices[i + j] for j in range(1, window + 1))
        is_low = all(prices[i] < prices[i - j] and prices[i] < prices[i + j] for j in range(1, window + 1))
        if is_high or is_low:
            swings.append(i)
    return swings

# === Streamlit UI ===
st.title("Elliott Wave Visualizer with Live Data")

symbol = st.text_input("Enter Stock Symbol", value='AAPL')
df = get_stock_data(symbol)

if not df.empty:
    swings = find_swings(df['close'].tolist(), window=2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price', line=dict(width=2)))

    # Draw wave lines
    for i in range(len(swings) - 1):
        x0, y0 = df.index[swings[i]], df['close'].iloc[swings[i]]
        x1, y1 = df.index[swings[i + 1]], df['close'].iloc[swings[i + 1]]
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines+text',
            text=[f"Wave {i+1}", ""],
            textposition="top center",
            line=dict(dash='dot', width=2),
            name=f"Wave {i+1}"
        ))

    # Mark swing points
    for idx in swings:
        fig.add_trace(go.Scatter(
            x=[df.index[idx]], y=[df['close'].iloc[idx]],
            mode='markers',
            marker=dict(color='orange', size=8),
            name='Swing'
        ))

    fig.update_layout(title=f"{symbol} - Elliott Wave Pattern Detection",
                      xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

else:
    st.error("Could not retrieve data. Try another symbol or wait a bit.")
