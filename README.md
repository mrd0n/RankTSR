Python scripts to calculate the Total Shareholder Return for CVE.TO and compare to 
a list of it's peers over a defined period.

refresh_data.py - handles the price data loading, refresh and calculations
RankTSR.py - calculates ranking, outputs performance summary and charts 

Example output:

    For period  2021-2023 ( 2021-01-01 : 2023-12-31 )
    CVE.TO starting VWAP date: 2020-12-31 VWAP: 7.221259417474435
    CVE.TO ending VWAP date: 2023-12-29 VWAP: 22.702139632578053
    +--------+------------+----------+-----------+--------+
    | Ticker | Start VWAP | End VWAP | Dividends |  TSR   |
    +--------+------------+----------+-----------+--------+
    |  DVN   | 15.169575  | 44.8715  |  10.0100  | 2.6179 |
    | IMO.TO | 23.944658  | 75.7963  |   4.4300  | 2.3505 |
    | CVE.TO |  7.221259  | 22.7021  |   1.0780  | 2.2931 |
    | OVV.TO | 18.177292  | 58.7366  |   0.0000  | 2.2313 |
    | CNQ.TO | 30.260149  | 87.4635  |  10.2261  | 2.2283 |
    |  COP   | 41.485251  | 114.3829 |  10.8500  | 2.0187 |
    |  HES   | 52.544130  | 140.9641 |   4.2520  | 1.7637 |
    |  APA   | 14.173405  | 35.7666  |   1.7630  | 1.6479 |
    | SU.TO  | 22.120119  | 43.4390  |   5.0350  | 1.1914 |
    |   BP   | 21.186388  | 35.4706  |   4.3280  | 0.8785 |
    |  CVX   | 88.899881  | 145.9496 |  17.0300  | 0.8333 |
    +--------+------------+----------+-----------+--------+
    The percentile rank for CVE.TO is 0.85% and the CVE Score is 1.87 


    Performance Summary:

    +-----------+------------+------------+-----------+------+-------+
    |   Period  |   Start    |    End     | Weighting | Rank | Score |
    +-----------+------------+------------+-----------+------+-------+
    |    2021   | 2021-01-01 | 2021-12-31 |    0.1    | 0.85 |  1.87 |
    |    2022   | 2022-01-01 | 2022-12-31 |    0.1    | 0.76 |  1.64 |
    |    2023   | 2023-01-01 | 2023-12-31 |    0.1    | 0.42 |  0.77 |
    | 2021-2023 | 2021-01-01 | 2023-12-31 |    0.7    | 0.85 |  1.87 |
    |     -     |     -      |     -      |     -     |  -   |   -   |
    |   Total   |            |            |           |      |  1.74 |
    +-----------+------------+------------+-----------+------+-------+

![example chart](https://raw.githubusercontent.com/mrd0n/RankTSR/main/charts/tsr_chart_2021-All%20years.png "2021-2023 example")

Developed with python 3.11.7