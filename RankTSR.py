# -*- coding: utf-8 -*-
"""
Calculates the Total Shareholder Return for a list of tickers over a specified set of periods.
For each defined perdiod displays the performance period summary and saves a ranking chart to a file.
For each defined period creates and saves a chart of daily TSR values for each ticker over the specified periods.

Created on Thu Jan  5 20:07:32 2024

@Author: Don
"""

import configparser
import ast
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
from prettytable import PrettyTable
import numpy as np

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
    price_data_df = pd.DataFrame()

    if not os.path.exists('data/detailed_tsr.csv'):
        # print error and abort
        print("Error: Detailed TSR data file not found. Run refresh-data.py.")
        return
    else:
        price_data_df = pd.read_csv('data/detailed_tsr.csv')
        # Convert the Date column to datetime and index on it
        price_data_df['Date'] = pd.to_datetime(price_data_df['Date'])
        price_data_df = price_data_df.set_index('Date')

    return price_data_df


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

    if not os.path.exists('data/dividend_data.csv'):
        # print error and abort
        print("Error: Dividend data file not found. Run refresh-data.py.")
        return
    else:
        dividend_data = pd.read_csv('data/dividend_data.csv')
        # Convert the Date column to datetime and index on it
        dividend_data['Date'] = pd.to_datetime(dividend_data['Date'])
        dividend_data = dividend_data.set_index('Date')

    return dividend_data


def calculate_tsr(tickers, price_data_df, dividend_data_df, start_date, end_date):
    """
    Calculate the Total Shareholder Return (TSR) for a list of tickers over a specified period.
      (Betwen the start date and end date)

    Parameters:
    - tickers: list of strings representing the tickers to calculate TSR for
    - price_data_df: DataFrame with price data including VWAP for each ticker
    - start_date: start date of the period to calculate TSR
    - end_date: end date of the period to calculate TSR

    Returns:
    - tsr_list: DataFrame with the calculated TSR for each ticker
    """
    # Initialize an empty list to store the ticker and TSR
    tsr_list = []

    # Loop through each ticker and calculate the Total Shareholder Return (TSR) for the period
    for ticker in tickers:
        # if period is in the future, continue the loop
        if start_date > datetime.now() or end_date > datetime.now():
            continue

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
        ending_vwap = ending_vwap['VWAP'].values[0]

        # Calculate the total amount of dividends issued over the period for primary_ticker
        dividends_total = dividend_data_df[(dividend_data_df['Ticker'] == ticker) &
                                           (dividend_data_df.index >= start_date) &
                                           (dividend_data_df.index <= end_date)]['Dividends'].sum()

        # Calculate the total shareholder return (TSR)
        tsr = (ending_vwap - starting_vwap + dividends_total) / starting_vwap

        # Append the ticker and TSR to the list
        tsr_list.append([ticker, starting_vwap, ending_vwap, dividends_total, tsr])

        if ticker == primary_ticker:
            # print starting and ending VWAP and dates
            print(ticker + ' starting VWAP date: ' +
                  starting_vwap_date.strftime("%Y-%m-%d") + ' VWAP: ' + str(starting_vwap))
            print(ticker + ' ending VWAP date: ' +
                  ending_vwap_date.strftime("%Y-%m-%d") + ' VWAP: ' + str(ending_vwap))

    # calculate the order of each ticker using the TSR
    tsr_list = pd.DataFrame(tsr_list, columns=['Ticker', 'Start VWAP', 'End VWAP', 'Dividends', 'TSR'])
    tsr_list['Rank'] = tsr_list['TSR'].rank(ascending=False)

    # sort the list by TSR
    tsr_list = tsr_list.sort_values(by='TSR', ascending=False)

    return tsr_list


def plot_tsr_ranking(tsr_df, start_date, end_date, primary_Rank):
    """
    Loop through each ticker and plot the tsr values
    """

    # create a figure and axis
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=96)

    # Loop through each ticker and plot the tsr values
    for ticker, tsr in tsr_df[['Ticker', 'TSR']].values:
        plt.bar(ticker, tsr)

    # set the legend and labels
    ax.set_xlabel('Ticker')
    ax.set_ylabel('Total Shareholder Return (TSR)', fontsize=12, labelpad=10)

    # Add in red line and rectangle on top
    ax.plot([0.05, .9], [.98, .98], transform=fig.transFigure, clip_on=False, color='#E3120B', linewidth=.6)
    ax.add_patch(plt.Rectangle((0.05, .98), 0.04, -0.02,
                               facecolor='#E3120B', transform=fig.transFigure,
                               clip_on=False, linewidth=0))

    # Add in title and subtitle
    ax.text(x=0.05, y=.93, s='Total Shareholder Return Ranking for each Ticker',
            transform=fig.transFigure, ha='left', fontsize=14, weight='bold', alpha=.8)
    ax.text(x=0.05, y=.90, s='TSR for each company from ' + start_date + ' to ' + end_date,
            transform=fig.transFigure, ha='left', fontsize=12, alpha=.8)

    # Set source text
    ax.text(x=0.05, y=0.05, s="Source: Stock data from Yahoo Finance",
            transform=fig.transFigure, ha='left', fontsize=10, alpha=.7)

    # mark primary_ticker on the chart
    plt.plot(primary_ticker, tsr_list.loc[tsr_list['Ticker'] == primary_ticker, 'TSR'].values[0],
             marker='o', color='red', markersize=6, alpha=0.3)
    plt.plot(primary_ticker, tsr_list.loc[tsr_list['Ticker'] == primary_ticker, 'TSR'].values[0],
             marker='o', color='red', markersize=3)
    plt.text(primary_ticker, tsr_list.loc[tsr_list['Ticker'] == primary_ticker, 'TSR'].values[0],
             '   ' + primary_ticker + ' percentile is ' + f"{primary_Rank:.2f}%", fontsize=10, color='black')

    # save the chart to a file
    plt.savefig('charts/tsr_chart_' + tsr_period[0] + '.png', dpi=600)
    # plt.show()

    # return plot
    return plt


def plot_tsr_timeline(ticker_data, primary_ticker, period):
    """
    Loop through each ticker and plot the tsr values on a figure
    """

    # create a figure and axis
    fig, ax = plt.subplots(figsize=(13.33, 7.5), dpi=96)
    # fig = Figure()
    # ax = fig.subplots()

    # Loop through each ticker and plot the tsr values
    for ticker in ticker_data['Ticker'].unique():
        plot_data = ticker_data[ticker_data['Ticker'] == ticker]
        if ticker == primary_ticker:
            line_width = 3
        else:
            line_width = 1
        ax.plot(plot_data.index, plot_data[str(period)+'_TSR'],
                label=ticker, linewidth=line_width)
        ax.plot(plot_data.index.max(), plot_data[str(period)+'_TSR'].iloc[-1], 'o', markersize=6, alpha=0.3)
        ax.plot(plot_data.index.max(), plot_data[str(period)+'_TSR'].iloc[-1], 'o', markersize=3)

    # set the legend and labels
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Shareholder Return (TSR)', fontsize=12, labelpad=10)
    ax.legend(loc='best', fontsize=6)

    # set the grid
    ax.grid(True)
    ax.grid(which="major", axis='x', color='#DAD8D7', alpha=0.5, zorder=1)
    ax.grid(which="major", axis='y', color='#DAD8D7', alpha=0.5, zorder=1)

    # Remove the spines
    ax.spines[['top', 'right', 'bottom']].set_visible(False)

    # Make the left spine thicker
    ax.spines['left'].set_linewidth(1.1)

    # Add in red line and rectangle on top
    ax.plot([0.05, .9], [.98, .98], transform=fig.transFigure, clip_on=False, color='#E3120B', linewidth=.6)
    ax.add_patch(plt.Rectangle((0.05, .98), 0.04, -0.02, facecolor='#E3120B', transform=fig.transFigure,
                               clip_on=False, linewidth=0))

    # Add in title and subtitle
    ax.text(x=0.05, y=.93, s=str(period) + ' TSR for each Ticker',
            transform=fig.transFigure, ha='left', fontsize=14, weight='bold', alpha=.8)
    ax.text(x=0.05, y=.90, s="Total Shareholder Return",
            transform=fig.transFigure, ha='left', fontsize=12, alpha=.8)

    # Set source text
    ax.text(x=0.05, y=0.12, s="Source: Stock data from Yahoo Finance",
            transform=fig.transFigure, ha='left', fontsize=10, alpha=.7)

    # Adjust the margins around the plot area
    plt.subplots_adjust(left=None, bottom=0.2, right=None, top=0.85, wspace=None, hspace=None)

    # Set a white background
    fig.patch.set_facecolor('white')

    return fig


def percent_rank(arr, score, sig_digits=8):
    arr = np.asarray(arr)
    arr = np.round(arr, sig_digits)
    score = np.round(score, sig_digits)
    if score in arr:
        small = (arr < score).sum()
        return small / (len(arr) - 1)
    else:
        if score < arr.min():
            return 0
        elif score > arr.max():
            return 1
        else:
            arr = np.sort(arr)
            position = np.searchsorted(arr, score)
            small = arr[position - 1]
            large = arr[position]
            small_rank = ((arr < score).sum() - 1) / (len(arr) - 1)
            large_rank = ((arr < large).sum()) / (len(arr) - 1)
            step = (score - small) / (large - small)
            rank = small_rank + step * (large_rank - small_rank)
            return rank


if __name__ == "__main__":
    '''
    Calculate and print relative performance for each ticker for each period defined in
    config.ini against the primary_ticker.
    '''

    config = configparser.ConfigParser()
    config.read('config.ini')

    # read the tickers to have the TSR calculated from config.ini
    tickers = ast.literal_eval(config.get("settings", "tickers"))
    primary_ticker = ast.literal_eval(config.get("settings", "primary_ticker"))

    # read the periods to have the TSR calculated from config.ini
    tsr_periods = ast.literal_eval(config.get("settings", "tsr_periods"))

    # convert the periods to datetime objects
    for period in tsr_periods:
        period[1] = datetime.strptime(period[1], '%Y-%m-%d')
        period[2] = datetime.strptime(period[2], '%Y-%m-%d')

    # load data for the tickers
    price_data_df = load_data(tickers)

    # load dividend data for the tickers
    dividend_data_df = load_dividends(tickers)

    performance_summary = []

    # loop through the tsr_periods and calculate the TSR
    for tsr_period in tsr_periods:
        # if period is in the future, continue the loop
        if tsr_period[1] > datetime.now() or tsr_period[2] > datetime.now():
            continue

        # calculate the tsr for the period
        print("For period ", tsr_period[0], "(", tsr_period[1].strftime("%Y-%m-%d"), ":",
              tsr_period[2].strftime("%Y-%m-%d"), ")")

        # if period is in the future, continue the loop
        if tsr_period[1] > datetime.now() and tsr_period[1] > datetime.now():
            continue

        tsr_list = calculate_tsr(tickers, price_data_df, dividend_data_df,
                                 tsr_period[1], tsr_period[2])

        # sort the list by decending tsr to print a table of tickers and their TSR
        tsr_sorted = tsr_list.sort_values(by='TSR', ascending=False)

        # print the rank of each ticker by TSR using PrettyTable and format to 2 decimal places
        table = PrettyTable(['Ticker', 'Start VWAP', 'End VWAP', 'Dividends', 'TSR'])
        for index, row in tsr_sorted.iterrows():
            table.add_row([row['Ticker'],
                           f"{row['Start VWAP']:4f}",
                           f"{row['End VWAP']:.4f}",
                           f"{row['Dividends']:.4f}",
                           f"{row['TSR']:.4f}"])
        print(table)

        # calculate the percentile rank of primary_ticker removing primary_ticker TSR from the list
        TSRs = tsr_list[tsr_list['Ticker'] != primary_ticker]['TSR'].values
        primary_TSR = tsr_list[tsr_list['Ticker'] == primary_ticker]['TSR'].values[0]

        # primary_Rank = stats.percentileofscore(TSRs, primary_TSR)/100
        primary_Rank = percent_rank(pd.Series(TSRs), primary_TSR, 3)

        # Interpolate the percentile rank of primary_ticker between the rank above and below
        if primary_Rank < 0.9 and primary_Rank > 0.25:
            above = tsr_list[tsr_list['TSR'] > primary_TSR]['TSR'].values.min()
            below = tsr_list[tsr_list['TSR'] < primary_TSR]['TSR'].values.max()
            primary_Rank += ((primary_TSR - below) / (above - below))*1/tsr_list['TSR'].count()
        if primary_Rank >= 0.90:
            primary_Score = 2
        elif primary_Rank >= 0.5:
            primary_Score = ((primary_Rank - 0.5) / 0.4) + 1
        elif primary_Rank >= 0.25 and primary_Rank < 0.90:
            primary_Score = ((primary_Rank - 0.25) / 0.25) * 0.75 + 0.25
        else:
            primary_Score = 0

        # print the TSR vaule from tsr_list for ticker primary_ticker
        print("The percentile rank for ", f"{primary_ticker}", " is",
              f"{primary_Rank:.3f}%", "and the ", f"{primary_ticker}",
              " Score is", f"{primary_Score:.2f}", "\n\n")

        # plot the tsr values for this period
        plot_tsr_ranking(tsr_sorted,
                         tsr_period[1].strftime("%Y-%m-%d"),
                         tsr_period[2].strftime("%Y-%m-%d"),
                         primary_Rank)

        # Extact performance start year
        performance_start_year = tsr_period[0][0:4]

        # add performance of period to performance summary
        performance_summary.append({'set': performance_start_year,
                                    'period': tsr_period[0],
                                    'start': tsr_period[1].strftime("%Y-%m-%d"),
                                    'end': tsr_period[2].strftime("%Y-%m-%d"),
                                    'weighting': tsr_period[3],
                                    'rank': primary_Rank,
                                    'score': primary_Score})

    # print the performance summary
    print("Performance Summary:\n")
    table = PrettyTable(['Period', 'Start', 'End', 'Weighting', 'Rank', 'Score'])
    total = 0
    for row in performance_summary:
        table.add_row([row['period'],
                       row['start'],
                       row['end'],
                       row['weighting'],
                       f"{row['rank']:.3f}",
                       f"{row['score']:.2f}"])
        total = total + row['weighting'] * row['score']
        # if the next row in performance_summary is for a different set, add a total row

        # if this row is the last in performance_summary, add a total row
        if not (performance_summary.index(row) == len(performance_summary) - 1):
            if row['set'] != performance_summary[performance_summary.index(row) + 1]['set']:
                table.add_row(['Total', '', '', '', '', f"{total:.2f}"])
                table.add_row(['-', '-', '-', '-', '-', '-'])
                total = 0
    print(table)

    # for each period, plot the daily tsr for each ticker over the timeline
    for period in tsr_periods:
        # if period is in the future, continue the loop
        if period[1] > datetime.now():
            continue

        # Filter the data to only the period
        ticker_data = price_data_df[price_data_df[str(period[0])+'_TSR'].notnull()]

        # create the figure plot
        fig = plot_tsr_timeline(ticker_data, primary_ticker, period[0])

        # save the figure to a file
        fig.savefig('charts/tsr_timeline_' + period[0] + '.png', dpi=600)
