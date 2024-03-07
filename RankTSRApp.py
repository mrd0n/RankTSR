# -*- coding: utf-8 -*-
"""
Panel app to visualize the daily TSR for a list of tickers for a defined period.

Created on Thu Jan  5 20:07:32 2024

@Author: Don
"""
from RankTSR import load_data, plot_tsr_timeline
import configparser
import ast
from datetime import datetime
import matplotlib.pyplot as plt
import panel as pn

# Ignore warnings in deprecated packages
import warnings
warnings.filterwarnings('ignore')

# set up panel
pn.extension("perspective", design='material')


def update_chart_preview(data, primary_ticker, period):
    try:
        chart_preview.loading = True
        # Filter the data to only the period
        ticker_data = data[data[str(period)+'_TSR'].notnull()]
        axes = plot_tsr_timeline(ticker_data, primary_ticker, period)
        plt.close(axes.figure)
        chart_preview.object = axes.figure
        chart_table.object = ticker_data
    finally:
        chart_preview.loading = False


if __name__ == "__main__":
    '''
    Panel App to display TSR performance over defined period
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

    # build list of period names (period[0])
    period_names = []
    for period in tsr_periods:
        period_names.append(period[0])

    # Instantiate Widgets & Pane
    period_widget = pn.widgets.Select(name="period", value=period_names[0], options=period_names)
    chart_preview = pn.pane.Matplotlib(plt.figure(), format="svg", sizing_mode="scale_both")
    chart_table = pn.pane.Perspective(editable=False, sizing_mode="stretch_both")

    main = pn.Column(period_widget), pn.Tabs(("Preview", chart_preview), ("Table", chart_table))

    template = pn.template.FastListTemplate(
        # sidebar=sidebar,
        main=main,
        title="TSR Viewer"
    )

    pn.bind(update_chart_preview, primary_ticker=primary_ticker, data=price_data_df, period=period_widget, watch=True)

    try:
        chart_preview.loading = True
        # Filter the data to only the period
        ticker_data = price_data_df[price_data_df[str(period_names[0])+'_TSR'].notnull()]
        axes = plot_tsr_timeline(ticker_data, primary_ticker, period_names[0])
        plt.close(axes.figure)
        chart_preview.object = axes.figure
        chart_table.object = ticker_data
    finally:
        chart_preview.loading = False

    # Serve the app
    template.show()
