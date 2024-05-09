import numpy as np
import scipy.stats as si
import streamlit as st
import pandas as pd
import plotly.express as px
from yahoo_fin import options
import yfinance as yf

st.set_page_config(page_title='Options Calculator', layout = 'wide', initial_sidebar_state = 'auto')

def N(x):
    return si.norm.cdf(x)
    
def callFormula(S, K, T, r, q, v):
    x = (np.log(S/K) + (r - q + v**2/2)*T) / (v*np.sqrt(T))
    y = x - v* np.sqrt(T)
    return S*np.exp(-q*T) * N(x) - K * np.exp(-r*T)* N(y)

def putFormula(S, K, T, r, q, v):
    x = (np.log(S/K))
    x = x + (r - q + v**2/2)*T / (v*np.sqrt(T))
    y = x - v* np.sqrt(T)
    return K*np.exp(-r*T)*N(-y) - S*np.exp(-q*T)*N(-x)

st.sidebar.header("Options Value Calculator")
with st.sidebar.form(key='inputs_form'):    
    S = st.number_input('Strike:', value=10.0, min_value=0.0)
    K = st.number_input('Stock Price:', value=10.0, min_value=0.0)
    T = st.number_input('Time till expiration (days):', value=31, min_value=0)
    r = st.number_input('Risk-Free Interest Rate (%):', value=5.0, min_value=0.0)
    q = st.number_input('Dividend Rate (%):', value=0.0, min_value=0.0)
    v = st.number_input('Volatility (%):', value=35.0, min_value=0.0)
    submit = st.form_submit_button(label='Find Value')


cv = callFormula(S,K,T/365,r/100,q/100,v/100)
pv = putFormula(S,K,T/365,r/100,q/100,v/100)

c, d= st.sidebar.columns(2)
c.metric("Call Value","${:.4f}".format(cv))
d.metric("Put Value","${:.4f}".format(pv))

st.header("Options Data Scraper")
st.write("Created by Faiz Patel")
st.write("Made using Yahoo Finance and YF Python Libraries (yahoo_fin & yfinance)")
st.write("Options value calculator created using black-scholes model")

a, b  = st.columns([1,1])
with a:
    ticker = st.text_input("Ticker:","AAPL")
    ticker = ticker.upper()
    tick = yf.Ticker(ticker)
    price = round(yf.Ticker(ticker).history(period='1s')['Close'][0],2)
    st.metric(label = "Current Price of {}".format(ticker), value = price)
with b:
    expiration = st.selectbox("Pick expiry date:", tick.options, index=0)



calls = options.get_calls(ticker,expiration)
puts = options.get_puts(ticker,expiration)
calls['Type'] = 'call'
puts['Type'] = 'puts'
df = pd.concat([calls,puts])

mainPlot = px.scatter(df, x='Strike', y='Last Price', color='Type', title="Option Prices for " + ticker + " (Expiry at " + expiration +")")
mainPlot.add_vline(x=price, annotation_text="Current Price: ${:.2f}".format(price))

a,b,c = st.columns([1.2,1,1])

a,b,c = st.columns([1,4,1])
with b:
    st.plotly_chart(mainPlot)


callPlot = px.scatter(calls, x='Strike', y='Last Price', title="Call Option Prices for " + ticker + " (Expiry at " + expiration+")")
callPlot.add_vline(x=price, annotation_text="Current Price: ${:.2f}".format(price))

putPlot = px.scatter(puts, x='Strike', y='Last Price', title="Put Option Prices for " + ticker + " (Expiry at " + expiration+")")
putPlot.add_vline(x=price, annotation_text="Current Price: ${:.2f}".format(price))

colCalls, colPuts  = st.columns([1,1])

with colCalls:
    st.header("Calls")
    st.plotly_chart(callPlot)

with colPuts:
    st.header("Puts")
    st.plotly_chart(putPlot)