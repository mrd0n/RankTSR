# download stock split data from yahoo finance
# then convert to csv and save to data folder

import yfinance as yf
import pandas as pd


def get_stock_split(ticker):
    data = yf.Ticker(ticker).info
    return data

def save_stock_split(ticker):
    data = get_stock_split(ticker)
    df = pd.DataFrame(data)
    df.to_csv('data/' + ticker + '_split.csv')

    return

save_stock_split('cnq.to')    