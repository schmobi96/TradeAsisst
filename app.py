import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_KEY = '0K46WI6OG3S5D4KO'

# === Get Stock Data ===
def get_stock_data(symbol='AAPL'):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
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

# === Detect Swing Points ===
def find_swings(prices, window=1):
    swings = []
    for i in range(window, len(prices) - window):
        is_high = all(prices[i] > prices[i - j] and prices[i] > prices[i + j] for j in range(1, window + 1))
        is_low = all(prices[i] < prices[i - j] and prices[i] < prices[i + j] for j in range(1, window + 1))
        if is_high:
            swings.append((i, 'high'))
        elif is_low:
            swings.append((i, 'low'))
    return swings

# === Streamlit UI ===
st.title("Elliott Wave Landing Zones")

symbol = st.text_input("Enter Stock Symbol", value='AAPL')
df = get_stock_data(symbol)

if not df.empty:
    df['swing'] = ''
    swings = find_swings(df['close'].tolist(), window=1)
    for i, t in swings:
        df.at[df.index[i], 'swing'] = t

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Price'))

    for idx, row in df.iterrows():
        if row['swing'] == 'high':
            fig.add_trace(go.Scatter(x=[row.name], y=[row['close']],
                                     mode='markers+text', text='High',
                                     marker=dict(color='red', size=8),
                                     name='Swing High'))
        elif row['swing'] == 'low':
            fig.add_trace(go.Scatter(x=[row.name], y=[row['close']],
                                     mode='markers+text', text='Low',
                                     marker=dict(color='green', size=8),
                                     name='Swing Low'))

    # Add landing zones (simulated)
    latest_close = df['close'].iloc[-1]
    wave2_zone = [latest_close * 0.95, latest_close * 0.98]
    wave4_zone = [latest_close * 0.90, latest_close * 0.93]

    fig.add_shape(type="rect",
                  x0=df.index[5], x1=df.index[-1],
                  y0=wave2_zone[0], y1=wave2_zone[1],
                  fillcolor="LightGreen", opacity=0.3, line_width=0)

    fig.add_shape(type="rect",
                  x0=df.index[5], x1=df.index[-1],
                  y0=wave4_zone[0], y1=wave4_zone[1],
                  fillcolor="LightBlue", opacity=0.3, line_width=0)

    fig.add_annotation(text="Wave 2 Buy Zone", x=df.index[6], y=wave2_zone[1] + 0.5, showarrow=False)
    fig.add_annotation(text="Wave 4 Buy Zone", x=df.index[6], y=wave4_zone[1] + 0.5, showarrow=False)

    fig.update_layout(title=f"{symbol} - Swing Points + Elliott Zones",
                      xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)
else:
    st.error("Failed to load data. Check your symbol or try again later.")
