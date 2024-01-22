"""
For each ticker in the list of tickers:
- Download the daily price data 
- Calulate the Typical Price and VWAP
- Download the dividends issued
- Calculate the Total Shareholder Return (TSR)
- TSR = (Ending 30 day VWAP - Starting 30 Day VWAP + Dividends) / Starting 30 day VWAP
"""

import pandas as pd
import pytz
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import matplotlib.pyplot as plt

# Ignore warnings in deprecated packages
import warnings
warnings.filterwarnings('ignore')


# Function to calculate the Total Shareholder Return (TSR) for a list
# of provided ticker that returns a list of tickers and their TSR
def calculate_tsr(tickers, price_data_df, dividend_data_df, start_date, end_date):
    # Initialize an empty list to store the ticker and TSR
    tsr_list = []

    # Loop through each ticker and calculate the Total Shareholder Return (TSR) for the period
    for ticker in tickers:
        # find the starting VWAP
        starting_vwap = price_data_df[(price_data_df.index >= start_date) &
                                      (price_data_df.index <= end_date +
                                       relativedelta(days=7)) &
                                      (price_data_df['Ticker'] == ticker)].head(1)

        # find the ending VWAP
        ending_vwap = price_data_df[(price_data_df.index >= end_date - relativedelta(days=7)) &
                                    (price_data_df.index <= end_date) &
                                    (price_data_df['Ticker'] == ticker)].tail(1)

        # Calculate the total amount of dividends issued over the period for CVE
        dividends_total = dividend_data_df[(dividend_data_df['Ticker'] == ticker) &
                                           (dividend_data_df.index >= start_date) &
                                           (dividend_data_df.index <= end_date)].sum()

        # Calculate the total shareholder return (TSR)
        tsr = (ending_vwap['VWAP'].values[0] - starting_vwap['VWAP'].values[0] +
               dividends_total['Dividends']) / starting_vwap['VWAP'].values[0]

        # Append the ticker and TSR to the list
        tsr_list.append([ticker, tsr])

    return tsr_list


if __name__ == "__main__":
    '''
        The list peer of companies:
            Cenovus Energy Corporation (CVE.TO)
            Apache Corporation (APA)
            Devon Energy Corporation (DVN)
            BP Plc. (BP)
            Hess Corporation (HES)
            Canadian Natural Resources Limited (CNQ.TO)
            Imperial Oil Limited (IMO.TO)
            Chevron Corporation (CVX)
            Ovintiv Inc. (OVV.TO)
            ConocoPhillips (COP)
            Suncor Energy Inc. (SU.TO)
    '''
    tickers = ['CVE.TO',
               'CNQ.TO', 'OVV.TO', 'APA', 'DVN', 'BP',
               'HES', 'IMO.TO', 'CVX', 'COP', 'SU.TO']

    # set the end date for the price data download
    end_date = datetime(2023, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))

    # start_date is 3 years and 30 days before the end_date
    # this should handle leap years
    start_date = end_date - relativedelta(years=3) + relativedelta(days=1)

    # Initialize an empty dataframe to store the daily price data
    price_data_df = pd.DataFrame()
    dividend_data_df = pd.DataFrame()

    # define the periods to have the TSR calculated
    tsr_periods = [
                ['2021',
                    datetime(2021, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('America/New_York')),
                    datetime(2021, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))],
                ['2022',
                    datetime(2022, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('America/New_York')),
                    datetime(2022, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))],
                ['2023', 
                    datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('America/New_York')),
                    datetime(2023, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))],
                ['2021-2023',
                    datetime(2021, 1, 1, 12, 0, 0, tzinfo=pytz.timezone('America/New_York')),
                    datetime(2023, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))]
                ]

    # Download the daily price data between the start and end dates
    # including 60 calendar days before the start date so that the 30 day VWAP can be calculated
    for ticker in tickers:
        data = yf.download(ticker, interval='1d', start=start_date-timedelta(days=60),
                           end=end_date, progress=False)

        # normalize the datetime object with timezone 'America/New_York'
        data.index = data.index.tz_localize('America/New_York')

        # Add the ticker to the dataframe
        data['Ticker'] = ticker

        # Calculate the typical price
        data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3

        # Calculate the TypicalPriceVolume
        data['TPV'] = data['TP'] * data['Volume']

        # Calculate the rolling 30 day VWAP
        data['VWAP'] = data['TPV'].rolling(window=30).sum() / data['Volume'].rolling(window=30).sum()

        # Get the dividends
        dividends = yf.Ticker(ticker).dividends.loc[start_date.strftime("%Y-%m-%d"):end_date.strftime("%Y-%m-%d")].to_frame()
        dividends.index = dividends.index.tz_convert('America/New_York')
        dividends['Ticker'] = ticker

        # Append the price and calculated data to the dataframe
        price_data_df = pd.concat([price_data_df, data], ignore_index=False)

        # Append the dividends to the dataframe
        dividend_data_df = pd.concat([dividend_data_df, dividends], ignore_index=False)

    # loop through the tsr_periods and calculate the TSR
    for tsr_period in tsr_periods:
        # calculate the tsr for the period
        print("For period ", tsr_period[0], "(", tsr_period[1].strftime("%Y-%m-%d"), ":",
              tsr_period[2].strftime("%Y-%m-%d"), ")")
        tsr_list = calculate_tsr(tickers, price_data_df, dividend_data_df, tsr_period[1], tsr_period[2])

        # sort the list by decending tsr to print a table of tickers and their TSR
        tsr_list.sort(key=lambda x: x[1], reverse=True)

        # print the rank of each ticker by TSR
        print(tabulate(tsr_list, headers=['Ticker', 'TSR'], tablefmt='fancy_grid'))

        # Convert the list into a dictionary
        tsr_list = {x[0]: x[1] for x in tsr_list}

        # calculate the number of tickers in the list where ticker 'CVE.TO' has a higher TSR than the others
        count = sum(1 for ticker, tsr in tsr_list.items() if tsr < tsr_list['CVE.TO'])

        print("CVE.TO has a higher TSR than", count / (len(tsr_list)-1) * 100,
              "% of it\'s peers for period", tsr_period[0], ".\n\n")

    '''
        # Loop through each ticker and plot the tsr values
        for ticker, tsr in tsr_list.items():
            plt.bar(ticker, tsr)
        plt.xlabel('Ticker')
        plt.ylabel('Total Shareholder Return (TSR)')
        plt.title('TSR for each Ticker from ' + start_date.strftime("%Y-%m-%d") + ' to ' +
                end_date.strftime("%Y-%m-%d"))
        plt.scatter('CVE.TO', tsr_list['CVE.TO'], marker='o', color='red')
        plt.text('CVE.TO', tsr_list['CVE.TO'], 'CVE.TO has a higher TSR than ' +
                str(count / (len(tsr_list)-1) * 100) +
                '% of it\'s peers.', fontsize=10, color='black')
        plt.show()
    '''
