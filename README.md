Python script to calculate the Total Sharehoder Return for CVE.TO and compare to 
a list of it's peers over a defined period

`
For period  2021-2023 ( 2021-01-01 : 2023-12-31 ) <br>
╒════╤══════════╤══════════════╤════════════╤═════════════╤══════════╤═══════════╕ <br> 
│    │ Ticker   │   Start VWAP │   End VWAP │   Dividends │      TSR │      Rank │ <br> 
╞════╪══════════╪══════════════╪════════════╪═════════════╪══════════╪═══════════╡ <br> 
│  4 │ DVN      │      15.2995 │    44.8715 │     10.01   │ 2.58715  │ 1         │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  7 │ IMO.TO   │      24.0387 │    75.7963 │      4.43   │ 2.33738  │ 0.909091  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  0 │ CVE.TO   │       7.2922 │    22.7021 │      1.078  │ 2.26104  │ 0.818182  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  1 │ CNQ.TO   │      30.3033 │    87.4635 │     10.2261 │ 2.22372  │ 0.727273  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  2 │ OVV.TO   │      18.2912 │    58.7366 │      0      │ 2.2112   │ 0.636364  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  9 │ COP      │      41.5737 │   114.383  │     10.85   │ 2.01231  │ 0.545455  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  6 │ HES      │      52.8091 │   140.964  │      4.252  │ 1.74983  │ 0.454545  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  3 │ APA      │      14.3132 │    35.7666 │      1.763  │ 1.62202  │ 0.363636  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│ 10 │ SU.TO    │      22.1727 │    43.439  │      5.035  │ 1.1862   │ 0.272727  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  5 │ BP       │      21.223  │    35.4706 │      4.328  │ 0.875257 │ 0.181818  │  
├────┼──────────┼──────────────┼────────────┼─────────────┼──────────┼───────────┤  
│  8 │ CVX      │      88.8961 │   145.95   │     17.03   │ 0.833371 │ 0.0909091 │  
╘════╧══════════╧══════════════╧════════════╧═════════════╧══════════╧═══════════╛  
The percentile rank for CVE.TO is 81.82%   
`
![example chart](https://github.com/mrd0n/RankTSR/blob/main/tsr_chart_2021-2023.png "2021-2023 example")

Developed with python 3.11.7