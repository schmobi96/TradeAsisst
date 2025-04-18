import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

API_KEY = '0K46WI6OG3S5D4KO'

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

st.title("Elliott Wave Stock Chart (MVP)")
symbol = st.text_input("Enter Stock Symbol", value='AAPL')

df = get_stock_data(symbol)
if not df.empty:
    st.write(f"Showing data for: {symbol}")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price'))
    st.plotly_chart(fig)
else:
    st.error("Could not retrieve data. Please check symbol or try again later.")
