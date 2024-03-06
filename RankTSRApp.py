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


def update_chart_preview(data, period):
    try:
        chart_preview.loading = True
        # Filter the data to only the period
        ticker_data = data[data[str(period)+'_TSR'].notnull()]
        axes = plot_tsr_timeline(ticker_data, period)
        plt.close(axes.figure)
        chart_preview.object = axes.figure
        chart_table.object = ticker_data
    finally:
        chart_preview.loading = False


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

    config = configparser.ConfigParser()
    config.read('config.ini')

    # read the tickers to have the TSR calculated from config.ini
    tickers = ast.literal_eval(config.get("settings", "tickers"))

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

    pn.bind(update_chart_preview, data=price_data_df, period=period_widget, watch=True)

    try:
        chart_preview.loading = True
        # Filter the data to only the period
        ticker_data = price_data_df[price_data_df[str(period_names[0])+'_TSR'].notnull()]
        axes = plot_tsr_timeline(ticker_data, period_names[0])
        plt.close(axes.figure)
        chart_preview.object = axes.figure
        chart_table.object = ticker_data
    finally:
        chart_preview.loading = False

    # Serve the app
    template.show()
