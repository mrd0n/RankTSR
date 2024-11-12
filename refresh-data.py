# -*- coding: utf-8 -*-
"""

Load and Refresh the Ticker Data required to calculate Rolling 30 day VWAP and Total
Shareholder Return (TSR).  Store in CSV files for use by other scripts and
visualisations.

Created on Thu Jan  5 18:12:42 2024

@Author: Don
"""

import configparser
import ast
import pandas as pd
import os
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Ignore warnings in deprecated packages
import warnings
warnings.filterwarnings('ignore')


def load_data(tickers):
    """
    Load and update ticker data files for a list of tickers.

    Parameters:
    - tickers: list of strings, the tickers of the stocks to update

    Returns:
    - pandas DataFrame, combined ticker data for the specified tickers
    """

    # Initialize an empty dataframe
    ticker_data = pd.DataFrame()

    for ticker in tickers:
        # Load ticker data from file if it exists
        if not os.path.exists('data/' + ticker + '.csv'):
            # data = yf.Ticker(ticker)
            data = yf.download(ticker, '2020-01-01', datetime.today(), progress=False)
            data['Ticker'] = ticker

            # Calculate the typical price
            data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3

            # Calculate the TypicalPriceVolume
            data['TPV'] = data['TP'] * data['Volume']

        # Append any new data from yfinance
        else:
            data = pd.read_csv('data/' + ticker + '.csv')

            # Convert the Date column to datetime
            data['Date'] = pd.to_datetime(data['Date'])

            # index the ticker data
            data = data.set_index('Date')

            # find the last date within the loaded file as a datetime
            last_date = pd.to_datetime(data.index[-1])

            # find the latest date available from yfinance using yf.download
            last_yfinance_date = yf.download(ticker, start=datetime.today()-timedelta(days=14),
                                             end=datetime.today(), progress=False).index[-1]
            # update the ticker data
            if last_date < last_yfinance_date:
                new_data = yf.download(ticker, start=last_date+timedelta(days=1), progress=False)

                # if new_data is empty, continue the loop
                if new_data.empty:
                    continue

                # new_data = new_data.history(start=last_date+timedelta(days=1), period='1d')
                new_data['Ticker'] = ticker

                # Calculate the typical price
                new_data['TP'] = (new_data['High'] + new_data['Low'] + new_data['Close']) / 3

                # Calculate the TypicalPriceVolume
                new_data['TPV'] = new_data['TP'] * new_data['Volume']

                print(f'Updating {ticker} with ' + str(new_data.shape[0]) + ' new rows.')

                data = pd.concat([data, new_data], ignore_index=False, )

        # Calculate the rolling 30 trading day VWAP
        data['VWAP'] = data['TPV'].rolling(window=30).sum() / data['Volume'].rolling(window=30).sum()

        # save updated ticker data to file
        data.to_csv('data/' + ticker + '.csv', index=True)

        # append updated ticker data to main dataframe
        ticker_data = pd.concat([ticker_data, data])

    return ticker_data


# function to load dividend data for a list of tickers using yfinance
def load_dividends(tickers):
    """
    Load dividend data for a list of tickers using yfinance.

    Parameters:
    - tickers: list of strings, the tickers of the stocks to load dividend data for

    Returns:
    - pandas DataFrame, combined dividend data for the specified tickers
    """
    # Initialize an empty dataframe
    dividend_data = pd.DataFrame()

    for ticker in tickers:
        # Load dividend data from yfinance
        data = yf.Ticker(ticker).dividends
        data = pd.DataFrame(data)
        data['Ticker'] = ticker

        # Convert the Date column to datetime with naive time
        # ata.index = pd.to_datetime(data.index).tz_localize(None)

        # remove timezone information and format to yyyy-mm-dd
        data.index = data.index.tz_localize(None).strftime('%Y-%m-%d')
        data.index = pd.to_datetime(data.index)

        # append updated dividend data to main dataframe
        dividend_data = pd.concat([dividend_data, data])

    return dividend_data


def populate_full_tsr(tickers, price_data_df, dividend_data_df, start_date, end_date, period_name):
    """
    Calculate the Total Shareholder Return (TSR) for a list of tickers over a specified period
    for each day in the period.

    Parameters:
    - tickers: list of strings representing the tickers to calculate TSR for
    - price_data_df: DataFrame with price data including VWAP for each ticker
    - start_date: start date of the period to calculate TSR
    - end_date: end date of the period to calculate TSR

    Returns:
    - tsr_list: DataFrame with the calculated TSR for each ticker
    """

    # Loop through each ticker and calculate the Total Shareholder Return (TSR) for the period
    for ticker in tickers:
        # if period is in the future, continue the loop
        if start_date > datetime.now():
            continue

        # if end_date is in the future, set ending_vwap_date to today
        if end_date > datetime.now():
            end_date = datetime.now()

        # find the starting VWAP by finding the closest trading day to the start_date
        starting_vwap = price_data_df[(price_data_df.index >= start_date - relativedelta(days=7)) &
                                      (price_data_df.index < start_date) &
                                      (price_data_df['Ticker'] == ticker)].tail(1)
        starting_vwap_date = starting_vwap.index[0]
        starting_vwap = starting_vwap['VWAP'].values[0]

        # find the ending VWAP by finding the closest trading day to the end_date
        ending_vwap = price_data_df[(price_data_df.index >= end_date - relativedelta(days=7)) &
                                    (price_data_df.index <= end_date) &
                                    (price_data_df['Ticker'] == ticker)].tail(1)
        ending_vwap_date = ending_vwap.index[0]

        period_df = price_data_df[(price_data_df.index >= starting_vwap_date) &
                                  (price_data_df.index <= ending_vwap_date) &
                                  (price_data_df['Ticker'] == ticker)]

        period_dividend_df = dividend_data_df[(dividend_data_df.index >= starting_vwap_date) &
                                              (dividend_data_df.index <= ending_vwap_date) &
                                              (dividend_data_df['Ticker'] == ticker)]

        period_df[period_name+'_TSR_to_date'] = (period_df['VWAP'] - starting_vwap +
                                                 period_dividend_df['Dividends'].sum()) / starting_vwap

        # Calc TSR for period and ticker within price_data_df
        price_data_df.loc[price_data_df['Ticker'] == ticker, period_name+'_TSR'] = period_df[period_name+'_TSR_to_date']

    return price_data_df


if __name__ == "__main__":
    '''
    This script loads data from yfinance and calculate the Total Shareholder Return (TSR)
    for a list of tickers defined in config.ini over a specified period for each day in the period.
    '''

    config = configparser.ConfigParser()
    config.read('config.ini')

    folders = ['data', 'charts']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # read the tickers to have the TSR calculated from config file
    tickers = ast.literal_eval(config.get("settings", "tickers"))

    # read the periods to have the TSR calculated from config file
    tsr_periods = ast.literal_eval(config.get("settings", "tsr_periods"))

    # convert the periods to datetime objects
    for period in tsr_periods:
        period[1] = datetime.strptime(period[1], '%Y-%m-%d')
        period[2] = datetime.strptime(period[2], '%Y-%m-%d')

    # load data for the tickers
    price_data_df = load_data(tickers)

    # load dividend data for the tickers
    dividend_data_df = load_dividends(tickers)

    # loop through the tsr_periods and calculate the TSR
    for tsr_period in tsr_periods:
        # if period is in the future, continue the loop
        if tsr_period[1] > datetime.now():
            continue

        # calculate the tsr for the period
        print("Calculating TSR for period ", tsr_period[0], "(", tsr_period[1].strftime("%Y-%m-%d"), ":",
              tsr_period[2].strftime("%Y-%m-%d"), ")")
        price_data_df = populate_full_tsr(tickers, price_data_df, dividend_data_df,
                                          tsr_period[1], tsr_period[2], tsr_period[0])

    # write the detailed_tsr to a csv file
    price_data_df.to_csv('data/detailed_tsr.csv')

    # write the dividend_data to a csv file
    dividend_data_df.to_csv('data/dividend_data.csv')

    print("Done!")
