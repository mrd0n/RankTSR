import pandas as pd
import os
from scipy import stats
import yfinance as yf
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from prettytable import PrettyTable

# Ignore warnings in deprecated packages
import warnings
warnings.filterwarnings('ignore')


# function to load ticker data from a file and then update for a list of tickers
# from the last date within the loaded file to latest available from yfinance
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
        if not os.path.exists(ticker + '.csv'):
            # data = yf.Ticker(ticker)
            data = yf.download(ticker, '2020-01-01', datetime.today(), progress=False)
            data['Ticker'] = ticker

            # Calculate the typical price
            data['TP'] = (data['High'] + data['Low'] + data['Close']) / 3

            # Calculate the TypicalPriceVolume
            data['TPV'] = data['TP'] * data['Volume']

        # Append any new data from yfinance
        else:
            data = pd.read_csv(ticker + '.csv')

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

                # new_data = new_data.history(start=last_date+timedelta(days=1), period='1d')
                new_data['Ticker'] = ticker

                # Calculate the typical price
                new_data['TP'] = (new_data['High'] + new_data['Low'] + new_data['Close']) / 3

                # Calculate the TypicalPriceVolume
                new_data['TPV'] = new_data['TP'] * new_data['Volume']

                data = pd.concat([data, new_data], ignore_index=False, )

        # Calculate the rolling 30 trading day VWAP
        data['VWAP'] = data['TPV'].rolling(window=30).sum() / data['Volume'].rolling(window=30).sum()

        # save updated ticker data to file
        data.to_csv(ticker + '.csv', index=True)

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

        # save updated dividend data to file
        # data.to_csv(ticker + '_dividends.csv', index=True)

        # append updated dividend data to main dataframe
        dividend_data = pd.concat([dividend_data, data])

    return dividend_data


def calculate_tsr(tickers, price_data_df, dividend_data_df, start_date, end_date):
    """
    Calculate the Total Shareholder Return (TSR) for a list of tickers over a specified period.

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

        # Calculate the total amount of dividends issued over the period for CVE
        dividends_total = dividend_data_df[(dividend_data_df['Ticker'] == ticker) &
                                           (dividend_data_df.index >= start_date) &
                                           (dividend_data_df.index <= end_date)]['Dividends'].sum()

        # Calculate the total shareholder return (TSR)
        tsr = (ending_vwap - starting_vwap + dividends_total) / starting_vwap

        # Append the ticker and TSR to the list
        tsr_list.append([ticker, starting_vwap, ending_vwap, dividends_total, tsr])

        if ticker == 'CVE.TO':
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


def plot_tsr(tsr_df, start_date, end_date, CVE_Rank):
    """
    Loop through each ticker and plot the tsr values
    """

    # Loop through each ticker and plot the tsr values
    for ticker, tsr in tsr_df[['Ticker', 'TSR']].values:
        plt.bar(ticker, tsr)
    plt.xlabel('Ticker')
    plt.xticks(fontsize=6, rotation=45)
    plt.ylabel('Total Shareholder Return (TSR)')
    plt.title('TSR for each company from ' + start_date + ' to ' +
              end_date)
    plt.scatter('CVE.TO', tsr_list.loc[tsr_list['Ticker'] == 'CVE.TO', 'TSR'].values[0], marker='o', color='red')
    plt.text('CVE.TO', tsr_list.loc[tsr_list['Ticker'] == 'CVE.TO', 'TSR'].values[0],
             '   CVE.TO percentile is ' + f"{CVE_Rank:.2f}%", fontsize=10, color='black')
    # save the chart to a file
    plt.savefig('tsr_chart_' + tsr_period[0] + '.png', dpi=600)
    # plt.show()
    # clear the plot
    plt.clf()


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

    # load data for the tickers
    price_data_df = load_data(tickers)

    # load dividend data for the tickers
    dividend_data_df = load_dividends(tickers)

    # define the periods to have the TSR calculated
    tsr_periods = [
                ['2021',
                    datetime(2021, 1, 1, 12, 0, 0),
                    datetime(2021, 12, 31, 12, 0, 0),
                    0.10],
                ['2022',
                    datetime(2022, 1, 1, 12, 0, 0),
                    datetime(2022, 12, 31, 12, 0, 0),
                    0.10],
                ['2023',
                    datetime(2023, 1, 1, 12, 0, 0),
                    datetime(2023, 12, 31, 12, 0, 0),
                    0.10],
                ['2021-2023',
                    datetime(2021, 1, 1, 12, 0, 0),
                    datetime(2023, 12, 31, 12, 0, 0),
                    0.70]
                ]

    performance_summary = []

    # loop through the tsr_periods and calculate the TSR
    for tsr_period in tsr_periods:
        # calculate the tsr for the period
        print("For period ", tsr_period[0], "(", tsr_period[1].strftime("%Y-%m-%d"), ":",
              tsr_period[2].strftime("%Y-%m-%d"), ")")
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

        # calculate the percentile rank of CVE.TO
        # remove the CVE.TO TSR from the list
        TSRs = tsr_list[tsr_list['Ticker'] != 'CVE.TO']['TSR'].values
        CVE_TSR = tsr_list[tsr_list['Ticker'] == 'CVE.TO']['TSR'].values[0]

        CVE_Rank = stats.percentileofscore(TSRs, CVE_TSR)/100

        # calculate CVE Score based on PSU formula interpolated between 0.25 <-> 0.5 and 0.5 <-> 0.9
        if CVE_Rank >= 0.90:
            CVE_Score = 2
        elif CVE_Rank >= 0.5:
            CVE_Score = ((CVE_Rank - 0.5) / 0.4) + 1
        elif CVE_Rank >= 0.25 and CVE_Rank < 0.90:
            CVE_Score = ((CVE_Rank - 0.25) / 0.25) * 0.75 + 0.25
        else:
            CVE_Score = 0

        # print the TSR vaule from tsr_list for ticker CVE.TO
        print("The percentile rank for CVE.TO is", f"{CVE_Rank:.2f}%",
              "and the CVE Score is", f"{CVE_Score:.2f}", "\n\n")

        # plot the tsr values for this period
        plot_tsr(tsr_sorted,
                 tsr_period[1].strftime("%Y-%m-%d"),
                 tsr_period[2].strftime("%Y-%m-%d"),
                 CVE_Rank)

        # add performance of period to performance summary
        performance_summary.append({'period': tsr_period[0],
                                    'start': tsr_period[1].strftime("%Y-%m-%d"),
                                    'end': tsr_period[2].strftime("%Y-%m-%d"),
                                    'weighting': tsr_period[3],
                                    'rank': CVE_Rank, 'score': CVE_Score})

    # print the performance summary
    print("Performance Summary:\n")
    table = PrettyTable(['Period', 'Start', 'End', 'Weighting', 'Rank', 'Score'])
    total = 0
    for row in performance_summary:
        table.add_row([row['period'],
                       row['start'],
                       row['end'],
                       row['weighting'],
                       f"{row['rank']:.2f}",
                       f"{row['score']:.2f}"])
        total = total + row['weighting'] * row['score']
    table.add_row(['-', '-', '-', '-', '-', '-'])
    table.add_row(['Total', '', '', '', '', f"{total:.2f}"])
    print(table)
