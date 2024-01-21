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
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
import pyarrow
import matplotlib.pyplot as plt

# Ignore warnings in deprecated packages
import warnings
warnings.filterwarnings('ignore')

# The list peer of stocks
# Cenovus Energy Corporation (CVE.TO)
# Apache Corporation (APA)
# Devon Energy Corporation (DVN)
# BP Plc. (BP)
# Hess Corporation (HES)
# Canadian Natural Resources Limited (CNQ.TO)
# Imperial Oil Limited (IMO.TO)
# Chevron Corporation (CVX)
# Ovintiv Inc. (OVV.TO)
# ConocoPhillips (COP)
# Suncor Energy Inc. (SU.TO)

tickers = ['CVE.TO', 'CNQ.TO', 'OVV.TO', 'APA', 'DVN', 'BP', 'HES', 'IMO.TO', 'CVX', 'COP', 'SU.TO']

# set the end date and start date
end_date = datetime(2023, 12, 31, 12, 0, 0, tzinfo=pytz.timezone('America/New_York'))

# start_date is 3 years and 30 days before the end_date
# this should handle leap years
start_date = end_date - relativedelta(years=3) + relativedelta(days=1)

# Initialize an empty dataframe to store the stock data
price_data_df = pd.DataFrame()
dividend_data_df = pd.DataFrame()

# Download the stock data between the start and end dates
# including 60 calendar days before the start date so that the 30 day VWAP can be calculated
for ticker in tickers:
    data = yf.download(ticker,interval='1d',start=start_date-timedelta(days=60), 
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

# Save dataframes to csv
#price_data_df.to_csv('price_data.csv')
#dividend_data_df.to_csv('dividend_data.csv')

# Initialize an Total Shareholder Return list
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

    # Append the ticker and tsr result to the list
    tsr_list.append([ticker, tsr])


# sort the list by decending tsr
tsr_list.sort(key=lambda x: x[1], reverse=True)

# print the rank of each ticker by TSR using tabulate in a pretty table with borders
print(tabulate(tsr_list, headers=['Ticker', 'TSR'], tablefmt='fancy_grid'))

# index the tsr list by ticker
tsr_list = {x[0]: x[1] for x in tsr_list}

# calculate the number of tickers in the list where ticker 'CVE.TO' has a higher TSR than the others
count = sum(1 for ticker, tsr in tsr_list.items() if tsr < tsr_list['CVE.TO'])

print("CVE.TO has a higher TSR than ", count / (len(tsr_list)-1) * 100,
      "% of it\'s peers.")

# Loop through each ticker and plot the tsr values
for ticker, tsr in tsr_list.items():
    plt.bar(ticker, tsr)
plt.xlabel('Ticker')
plt.ylabel('Total Shareholder Return (TSR)')
plt.title('TSR for each Ticker from ' + start_date.strftime("%Y-%m-%d") + ' to ' + 
          end_date.strftime("%Y-%m-%d"))
plt.scatter('CVE.TO', tsr_list['CVE.TO'], marker='o', color='red')
plt.text('CVE.TO', tsr_list['CVE.TO'], 'CVE.TO has a higher TSR than ' + str(count / (len(tsr_list)-1) * 100) + 
         '% of it\'s peers.', fontsize=10, color='black')
plt.show()






