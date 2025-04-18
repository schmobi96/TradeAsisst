import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_KEY = 'UYI5BMKI97Y4DGIB'

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
def find_swings(prices, window=2):
    swings = []
    for i in range(window, len(prices) - window):
        is_high = all(prices[i] > prices[i - j] and prices[i] > prices[i + j] for j in range(1, window + 1))
        is_low = all(prices[i] < prices[i - j] and prices[i] < prices[i + j] for j in range(1, window + 1))
        if is_high or is_low:
            swings.append(i)
    return swings

# === Streamlit UI ===
st.title("Elliott Wave Detector + Fibonacci Buy Zones")

symbol = st.text_input("Enter Stock Symbol", value='AAPL')
df = get_stock_data(symbol)

if not df.empty:
    swings = find_swings(df['close'].tolist(), window=2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price', line=dict(width=2)))

    # Only use first 6 swing points (Wave 1 to Wave 5 = 5 lines)
    labeled_swings = swings[:6] if len(swings) >= 6 else []

    # Draw waves 1-5
    for i in range(len(labeled_swings) - 1):
        x0, y0 = df.index[labeled_swings[i]], df['close'].iloc[labeled_swings[i]]
        x1, y1 = df.index[labeled_swings[i + 1]], df['close'].iloc[labeled_swings[i + 1]]
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines+text',
            text=[f"Wave {i+1}", ""],
            textposition="top center",
            line=dict(dash='dot', width=2),
            name=f"Wave {i+1}"
        ))

    # Fibonacci Buy Zones
    if len(labeled_swings) >= 4:
        # Wave 1 = swing[0] -> swing[1], Wave 3 = swing[2] -> swing[3]
        wave1_start = df['close'].iloc[labeled_swings[0]]
        wave1_end = df['close'].iloc[labeled_swings[1]]
        wave1_diff = abs(wave1_end - wave1_start)

        wave2_zone = [
            wave1_end - wave1_diff * 0.618,
            wave1_end - wave1_diff * 0.5
        ]

        wave3_start = df['close'].iloc[labeled_swings[2]]
        wave3_end = df['close'].iloc[labeled_swings[3]]
        wave3_diff = abs(wave3_end - wave3_start)

        wave4_zone = [
            wave3_end - wave3_diff * 0.5,
            wave3_end - wave3_diff * 0.382
        ]

        # Draw zones
        x_start = df.index[labeled_swings[1]]
        x_end = df.index[labeled_swings[-1]]

        fig.add_shape(type="rect", x0=x_start, x1=x_end,
                      y0=wave2_zone[0], y1=wave2_zone[1],
                      fillcolor="LightGreen", opacity=0.3, line_width=0)

        fig.add_shape(type="rect", x0=x_start, x1=x_end,
                      y0=wave4_zone[0], y1=wave4_zone[1],
                      fillcolor="LightBlue", opacity=0.3, line_width=0)

        fig.add_annotation(text="Wave 2 Buy Zone", x=x_start, y=wave2_zone[1], showarrow=False)
        fig.add_annotation(text="Wave 4 Buy Zone", x=x_start, y=wave4_zone[1], showarrow=False)

    # Highlight swing points
    for idx in labeled_swings:
        fig.add_trace(go.Scatter(
            x=[df.index[idx]], y=[df['close'].iloc[idx]],
            mode='markers',
            marker=dict(color='orange', size=8),
            name='Swing'
        ))

    fig.update_layout(title=f"{symbol} - Waves + Fibonacci Buy Zones",
                      xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

else:
    st.error("Could not retrieve data. Try another symbol or wait a bit.")
